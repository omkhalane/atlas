import asyncio
import json
import logging
import secrets
import websockets
import http.server
import socketserver
import threading
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("atlas-connector")

PORT = 3210
SESSIONS = {}

async def websocket_handler(websocket, path):
    parts = path.split('/')
    if len(parts) >= 3 and parts[1] == 'browser':
        session_id = parts[2]
        if session_id in SESSIONS:
            logger.info(f"Browser connected for session {session_id}")
            SESSIONS[session_id]['ws'] = websocket
            SESSIONS[session_id]['status'] = 'connected'
            try:
                async for message in websocket:
                    data = json.loads(message)
                    logger.info(f"Message from browser: {data}")
                    # In Phase 2: Forward to Atlas Runtime
            except websockets.exceptions.ConnectionClosed:
                logger.info(f"Browser disconnected for session {session_id}")
            finally:
                SESSIONS[session_id]['status'] = 'disconnected'
                SESSIONS[session_id]['ws'] = None
        else:
            await websocket.close(1008, "Invalid session")

class HttpHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/connect/start':
            session_id = secrets.token_hex(4).upper()
            token = secrets.token_urlsafe(16)
            SESSIONS[session_id] = {'token': token, 'status': 'waiting', 'ws': None}
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'sessionId': session_id, 'token': token, 'url': f'http://127.0.0.1:{PORT}/connect/{token}'}).encode())
            return
        self.send_response(404)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith('/connect/'):
            token = parsed.path.split('/')[-1]
            session = next((sid for sid, s in SESSIONS.items() if s['token'] == token), None)
            if session:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                html = f"""
                <html>
                <body>
                    <h1>Atlas Browser Connector</h1>
                    <p>Connecting session {session}...</p>
                    <script>
                        // Send connection request to extension
                        window.postMessage({{ type: 'ATLAS_CONNECT', sessionId: '{session}' }}, '*');
                        setTimeout(() => document.body.innerHTML += '<p>Connection established. You can close this tab.</p>', 1000);
                    </script>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
                return
        self.send_response(404)
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.end_headers()

def run_http_server():
    with socketserver.TCPServer(("127.0.0.1", PORT), HttpHandler) as httpd:
        httpd.serve_forever()

async def main():
    threading.Thread(target=run_http_server, daemon=True).start()
    async with websockets.serve(websocket_handler, "127.0.0.1", PORT + 1): # WS on 3211 for now to avoid port conflicts with simplehttp
        logger.info(f"Atlas Connector started. HTTP: 3210, WS: 3211")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
