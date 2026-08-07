#!/usr/bin/env python3

import os
import re
import sys
import time
import socket
import shutil
import subprocess
import tempfile
from pathlib import Path

import requests
from playwright.sync_api import sync_playwright


# ---------------------------------------------------------
# Browser definitions
# ---------------------------------------------------------

BROWSERS = {
    "google-chrome": [
        "google-chrome",
        "google-chrome-stable",
        "chrome",
    ],
    "chromium": [
        "chromium",
        "chromium-browser",
    ],
    "brave": [
        "brave-browser",
        "brave",
    ],
    "microsoft-edge": [
        "microsoft-edge",
        "microsoft-edge-stable",
    ],
    "vivaldi": [
        "vivaldi",
    ],
    "opera": [
        "opera",
    ],
}


# ---------------------------------------------------------
# Utilities
# ---------------------------------------------------------

def find_executable(names):
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    return None


def get_installed_browsers():
    found = {}

    for browser, names in BROWSERS.items():
        executable = find_executable(names)

        if executable:
            found[browser] = executable

    return found


def is_port_open(host, port):
    try:
        with socket.create_connection((host, port), timeout=0.2):
            return True
    except OSError:
        return False


def get_cdp_info(port):
    """
    Ask Chromium's CDP HTTP server for browser information.
    """
    try:
        response = requests.get(
            f"http://127.0.0.1:{port}/json/version",
            timeout=0.5,
        )

        if response.status_code != 200:
            return None

        data = response.json()

        if "webSocketDebuggerUrl" not in data:
            return None

        return data

    except Exception:
        return None


# ---------------------------------------------------------
# Find already-running CDP browsers
# ---------------------------------------------------------

def find_running_cdp_browsers():
    """
    Looks through running processes for:

        --remote-debugging-port=XXXX

    This is much better than blindly scanning ports.
    """

    results = []

    try:
        output = subprocess.check_output(
            ["ps", "-eo", "pid,args"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return results

    for line in output.splitlines():

        match = re.search(
            r"^\s*(\d+)\s+.*--remote-debugging-port[=\s]+(\d+)",
            line,
        )

        if not match:
            continue

        pid = int(match.group(1))
        port = int(match.group(2))

        info = get_cdp_info(port)

        if not info:
            continue

        results.append({
            "pid": pid,
            "port": port,
            "browser": info.get("Browser"),
            "websocket": info.get("webSocketDebuggerUrl"),
            "user_data_dir": info.get("userDataDir"),
        })

    return results


# ---------------------------------------------------------
# Scan common CDP ports
# ---------------------------------------------------------

def scan_cdp_ports(start=9222, end=9322):
    """
    Finds CDP servers even if we don't see the process command line.
    """

    results = []

    for port in range(start, end + 1):

        if not is_port_open("127.0.0.1", port):
            continue

        info = get_cdp_info(port)

        if not info:
            continue

        results.append({
            "pid": None,
            "port": port,
            "browser": info.get("Browser"),
            "websocket": info.get("webSocketDebuggerUrl"),
            "user_data_dir": info.get("userDataDir"),
        })

    return results


# ---------------------------------------------------------
# Launch temporary CDP browser
# ---------------------------------------------------------

def launch_browser(executable, port=9222):
    """
    Launch a completely isolated browser instance.

    This does NOT touch the user's normal browser profile.
    """

    profile = tempfile.mkdtemp(prefix="atlas-cdp-")

    command = [
        executable,

        f"--remote-debugging-port={port}",

        f"--user-data-dir={profile}",

        "--no-first-run",
        "--no-default-browser-check",

        "--disable-popup-blocking",

        "about:blank",
    ]

    print()
    print("Launching:")
    print(" ".join(command))
    print()

    process = subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait for CDP to become available
    deadline = time.time() + 10

    while time.time() < deadline:

        info = get_cdp_info(port)

        if info:
            return {
                "process": process,
                "port": port,
                "profile": profile,
                "browser": info.get("Browser"),
                "websocket": info.get("webSocketDebuggerUrl"),
            }

        time.sleep(0.2)

    process.kill()

    raise RuntimeError(
        "Browser started but CDP endpoint did not become available"
    )


# ---------------------------------------------------------
# Atlas CDP end-to-end test
# ---------------------------------------------------------

def run_e2e_test(cdp_port):
    print()
    print("=" * 60)
    print("ATLAS CDP END-TO-END TEST")
    print("=" * 60)

    endpoint = f"http://127.0.0.1:{cdp_port}"

    print(f"[1/6] Connecting to CDP: {endpoint}")

    with sync_playwright() as playwright:

        browser = playwright.chromium.connect_over_cdp(endpoint)

        print("      ✓ CDP connection established")

        print("[2/6] Checking browser context")

        contexts = browser.contexts

        if not contexts:
            raise RuntimeError("No browser contexts found")

        context = contexts[0]

        print("      ✓ Browser context available")

        print("[3/6] Creating page")

        pages = context.pages

        if pages:
            page = pages[0]
        else:
            page = context.new_page()

        print("      ✓ Page available")

        print("[4/6] Navigating")

        page.goto(
            "https://example.com",
            wait_until="domcontentloaded",
            timeout=15000,
        )

        print(f"      ✓ URL: {page.url}")

        print("[5/6] Verifying DOM")

        title = page.title()

        if not title:
            raise RuntimeError("Could not read page title")

        print(f"      ✓ Title: {title}")

        heading = page.locator("h1").inner_text()

        if heading != "Example Domain":
            raise RuntimeError(
                f"Unexpected heading: {heading!r}"
            )

        print(f"      ✓ H1: {heading}")

        print("[6/6] Verifying interaction")

        # Navigate to a simple data URL so the test is deterministic.
        page.goto(
            "data:text/html,"
            "<html>"
            "<body>"
            "<input id='name'>"
            "<button id='submit'>Submit</button>"
            "<div id='result'></div>"
            "<script>"
            "document.querySelector('#submit').onclick = () => {"
            "document.querySelector('#result').textContent = "
            "'Atlas CDP works';"
            "}"
            "</script>"
            "</body>"
            "</html>",
            wait_until="domcontentloaded",
        )

        page.locator("#name").fill("Atlas")

        page.locator("#submit").click()

        result = page.locator("#result").inner_text()

        if result != "Atlas CDP works":
            raise RuntimeError(
                f"Interaction failed: {result!r}"
            )

        print("      ✓ Fill works")
        print("      ✓ Click works")
        print("      ✓ DOM extraction works")

        browser.close()

    print()
    print("=" * 60)
    print("ATLAS CDP TEST: PASS")
    print("=" * 60)
    print()


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print()
    print("=" * 60)
    print("ATLAS BROWSER DISCOVERY")
    print("=" * 60)

    # 1. Installed browsers
    installed = get_installed_browsers()

    print()
    print("Installed browsers:")

    if not installed:
        print("  None detected")
    else:
        for name, path in installed.items():
            print(f"  ✓ {name}: {path}")

    # 2. Existing CDP processes
    print()
    print("Searching running CDP browsers...")

    running = find_running_cdp_browsers()

    # 3. Port scan fallback
    scanned = scan_cdp_ports()

    # Merge
    discovered = {}

    for browser in running + scanned:
        discovered[browser["port"]] = browser

    print()

    if discovered:

        print("CDP browsers found:")

        for browser in discovered.values():

            print(
                f"  ✓ port={browser['port']} "
                f"browser={browser['browser']} "
                f"pid={browser['pid']}"
            )

    else:
        print("  No existing CDP browser found.")

    # -----------------------------------------------------
    # Use existing browser if available
    # -----------------------------------------------------

    if discovered:

        selected = next(iter(discovered.values()))

        print()
        print(
            f"Using existing CDP browser on "
            f"port {selected['port']}"
        )

        run_e2e_test(selected["port"])

        return

    # -----------------------------------------------------
    # Otherwise launch one
    # -----------------------------------------------------

    if not installed:
        print()
        print("ERROR: No Chromium-based browser installed.")
        sys.exit(1)

    # Prefer Chrome -> Chromium -> Brave -> Edge
    preferred = [
        "google-chrome",
        "chromium",
        "brave",
        "microsoft-edge",
        "vivaldi",
        "opera",
    ]

    selected_browser = None

    for name in preferred:

        if name in installed:
            selected_browser = installed[name]
            break

    if not selected_browser:
        selected_browser = next(iter(installed.values()))

    print()
    print(
        f"No existing CDP browser found."
        f"\nLaunching: {selected_browser}"
    )

    port = 9222

    # If 9222 is already occupied by something unrelated,
    # find another port.
    while is_port_open("127.0.0.1", port):
        port += 1

    launched = None

    try:

        launched = launch_browser(
            selected_browser,
            port,
        )

        print(
            f"✓ Browser launched on CDP port {port}"
        )

        run_e2e_test(port)

    finally:

        if launched:

            process = launched["process"]

            if process.poll() is None:

                print()
                print("Closing test browser...")

                process.terminate()

                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()

            # Remove temporary profile
            import shutil as _shutil

            _shutil.rmtree(
                launched["profile"],
                ignore_errors=True,
            )


if __name__ == "__main__":
    main()