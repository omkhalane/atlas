import socket
import threading
import urllib.request
import json
import re
import os
import glob
import sys
import datetime

PORT = 3210
LOG_FILE = "/tmp/atlas_proxy.log"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.datetime.now().isoformat()}] {msg}\n")
    print(msg)
    sys.stdout.flush()

def find_devtools_path_for_port(target_port):
    home = os.path.expanduser('~')
    search_dirs = [
        f"{home}/.config/google-chrome",
        f"{home}/.config/google-chrome-beta",
        f"{home}/.config/google-chrome-unstable",
        f"{home}/.config/chromium",
        f"{home}/.config/BraveSoftware/Brave-Browser",
        f"{home}/.config/microsoft-edge",
        f"{home}/snap/chromium/current/.config/chromium"
    ]
    
    for sdir in search_dirs:
        try:
            paths_to_check = [os.path.join(sdir, "DevToolsActivePort")]
            paths_to_check.extend(glob.glob(os.path.join(sdir, "Profile *", "DevToolsActivePort")))
            paths_to_check.extend(glob.glob(os.path.join(sdir, "Default", "DevToolsActivePort")))
            
            for p in paths_to_check:
                if os.path.exists(p):
                    with open(p, 'r') as f:
                        lines = f.read().strip().split('\n')
                        if len(lines) >= 2:
                            port = lines[0].strip()
                            path = lines[1].strip()
                            if port == str(target_port):
                                return path
        except Exception as e:
            pass
            
    return None

def handle_client(client_sock):
    try:
        initial_data = client_sock.recv(4096)
        if not initial_data:
            client_sock.close()
            return
            
        initial_data_str = initial_data.decode('utf-8', errors='ignore')
        first_line = initial_data_str.split('\r\n')[0]
        
        if initial_data_str.startswith('OPTIONS /api/browser/cdp-version'):
            resp = (
                "HTTP/1.1 204 No Content\r\n"
                "Access-Control-Allow-Origin: *\r\n"
                "Access-Control-Allow-Methods: GET, OPTIONS\r\n"
                "Access-Control-Allow-Headers: *\r\n"
                "\r\n"
            ).encode('utf-8')
            client_sock.sendall(resp)
            client_sock.close()
            return
        
        if initial_data_str.startswith('GET /api/browser/cdp-version'):
            chrome_port = 9222
            match = re.search(r'targetPort=(\d+)', first_line)
            if match:
                chrome_port = int(match.group(1))
                
            ws_url = None
            error_msg = None
            try:
                req = urllib.request.Request(f"http://127.0.0.1:{chrome_port}/json/version")
                req.add_header('Host', f'127.0.0.1:{chrome_port}')
                with urllib.request.urlopen(req, timeout=1) as response:
                    data = response.read()
                info = json.loads(data)
                if 'webSocketDebuggerUrl' in info:
                    ws_url = info['webSocketDebuggerUrl']
            except Exception as e:
                browser_path = find_devtools_path_for_port(chrome_port)
                if browser_path:
                    ws_url = f"ws://127.0.0.1:{chrome_port}{browser_path}"
                else:
                    error_msg = str(e)
            
            if ws_url:
                original_ws = re.sub(r':\d+/', f':{PORT}/', ws_url)
                if '?' in original_ws:
                    original_ws += f'&targetPort={chrome_port}'
                else:
                    original_ws += f'?targetPort={chrome_port}'
                
                info = {'webSocketDebuggerUrl': original_ws}
                data = json.dumps(info).encode('utf-8')
                resp = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: application/json\r\n"
                    "Access-Control-Allow-Origin: *\r\n"
                    f"Content-Length: {len(data)}\r\n\r\n"
                ).encode('utf-8') + data
                client_sock.sendall(resp)
            else:
                err = {"error": f"Failed to connect to Chrome on port {chrome_port}: {error_msg}. Also could not find DevToolsActivePort file."}
                data = json.dumps(err).encode('utf-8')
                resp = (
                    "HTTP/1.1 500 Internal Server Error\r\n"
                    "Content-Type: application/json\r\n"
                    "Access-Control-Allow-Origin: *\r\n"
                    f"Content-Length: {len(data)}\r\n\r\n"
                ).encode('utf-8') + data
                client_sock.sendall(resp)
            
            client_sock.close()
            return
            
        chrome_port = 9222
        match = re.search(r'targetPort=(\d+)', first_line)
        if match:
            chrome_port = int(match.group(1))
            
        remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_sock.connect(('127.0.0.1', chrome_port))
        
        lines = initial_data_str.split('\r\n')
        new_lines = []
        for line in lines:
            if line.lower().startswith('origin:'):
                continue
            elif line.lower().startswith('host:'):
                new_lines.append(f'Host: 127.0.0.1:{chrome_port}')
            else:
                new_lines.append(line)
        
        modified_data = '\r\n'.join(new_lines).encode('utf-8')
        remote_sock.sendall(modified_data)
        
        def forward(src, dst, name):
            byte_count = 0
            start_time = datetime.datetime.now()
            try:
                while True:
                    data = src.recv(4096)
                    if not data:
                        log(f"{name} connection closed. Total bytes: {byte_count}")
                        break
                    byte_count += len(data)
                    dst.sendall(data)
                    
                    # Log every 1MB to see if data is flowing
                    if byte_count % 1000000 < 4096 and byte_count > 0:
                        log(f"{name} transferred {byte_count} bytes so far...")
            except Exception as e:
                log(f"{name} connection closed with error: {e}. Total bytes: {byte_count}")
            finally:
                src.close()
                dst.close()
                
        t1 = threading.Thread(target=forward, args=(client_sock, remote_sock, "client->remote"))
        t2 = threading.Thread(target=forward, args=(remote_sock, client_sock, "remote->client"))
        t1.start()
        t2.start()
    except Exception as e:
        client_sock.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', PORT))
    server.listen(10)
    
    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=(client,), daemon=True).start()

if __name__ == '__main__':
    start_server()
