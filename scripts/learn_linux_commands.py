import urllib.request
import re
import json
import os

def fetch_ss64():
    url = "https://ss64.com/bash/"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching ss64: {e}")
        return []
    
    commands = []
    # SS64 bash page uses a table with rows containing <a href="cmd.html">cmd</a> and then a description in the next td.
    # Pattern to match: <td><a href="...">command</a></td>\s*<td>description</td>
    pattern = re.compile(r'<td><a href="[^"]+">([^<]+)</a></td>\s*<td>([^<]+)</td>')
    for match in pattern.finditer(html):
        cmd = match.group(1).strip()
        desc = match.group(2).strip()
        if cmd and desc:
            commands.append({
                "command": cmd,
                "description": desc,
                "source": url
            })
    return commands

def fetch_labex():
    url = "https://linux-commands.labex.io/"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching labex: {e}")
        return []
    
    commands = []
    # labex returns JSON payload embedded in script tags or HTML structure.
    # We can try to extract article tags with aria-label which contains the description.
    # Example: aria-label="install - Learn how to install Linux packages..."
    pattern = re.compile(r'aria-label="([^"]+?)\s+-\s+([^"]+?)"')
    for match in pattern.finditer(html):
        cmd = match.group(1).strip()
        desc = match.group(2).strip()
        if cmd and desc:
            commands.append({
                "command": cmd,
                "description": desc,
                "source": url
            })
    return commands

def main():
    print("Fetching from ss64.com...")
    ss64_cmds = fetch_ss64()
    print(f"Found {len(ss64_cmds)} commands from ss64.")

    print("Fetching from linux-commands.labex.io...")
    labex_cmds = fetch_labex()
    print(f"Found {len(labex_cmds)} commands from labex.")

    # Combine and deduplicate (prefer labex if dup, but we can just append)
    seen = set()
    final_commands = []
    
    for item in ss64_cmds + labex_cmds:
        if item["command"] not in seen:
            seen.add(item["command"])
            final_commands.append(item)
            
    print(f"Total unique commands: {len(final_commands)}")

    # Save to atlas/core/memory/linux_commands.json
    out_dir = os.path.join(os.path.dirname(__file__), "..", "atlas", "core", "memory")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "linux_commands.json")
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(final_commands, f, indent=2)
        
    print(f"Saved to {out_file}")

if __name__ == "__main__":
    main()
