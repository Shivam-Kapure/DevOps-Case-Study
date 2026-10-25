import sys
import os
import json
import socket
import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from dotenv import load_dotenv

# Search for .env in current and parent directories
base_dir = Path(__file__).resolve().parent.parent
env_paths = [Path.cwd() / ".env", base_dir / ".env"]
for p in env_paths:
    if p.exists():
        load_dotenv(dotenv_path=p, override=False)
        break
else:
    load_dotenv()

# Configuration
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", os.getenv("PORT", "28080")))
FRONTEND_HOST = os.getenv("FRONTEND_HOST", "0.0.0.0")
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:28081")

STATIC_DIR = Path(__file__).resolve().parent

def is_port_available(host: str, port: int) -> bool:
    """Check if the specified host and port can be bound without conflict."""
    test_hosts = ["127.0.0.1"]
    if host not in ["127.0.0.1", "localhost"]:
        test_hosts.append("0.0.0.0")

    for th in test_hosts:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if sys.platform != "win32":
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((th, port))
            sock.close()
        except OSError:
            try:
                sock.close()
            except Exception:
                pass
            return False
    return True

def print_port_error_and_exit(port: int, host: str):
    banner = f"""
================================================================================
[ERROR] FRONTEND PORT CONFLICT DETECTED
================================================================================
The configured frontend port {port} on {host} is currently OCCUPIED or in use.

To resolve this conflict and run on another port, choose one of these options:

1. Pass a different port via CLI flag:
     python frontend/server.py --port 28090

2. Set the FRONTEND_PORT environment variable before starting:
     - PowerShell:  $env:FRONTEND_PORT="28090"; python frontend/server.py
     - Windows CMD: set FRONTEND_PORT=28090 && python frontend/server.py
     - Bash/Linux:  FRONTEND_PORT=28090 python frontend/server.py

3. Update the .env file at the root of the repository:
     FRONTEND_PORT=28090
================================================================================
"""
    print(banner, file=sys.stderr)
    sys.exit(1)

class FrontendHTTPHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self):
        # Serve dynamic runtime config endpoint
        if self.path in ["/config.json", "/api/config"]:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            config_payload = {
                "backendApiUrl": BACKEND_API_URL,
                "frontendPort": FRONTEND_PORT,
                "environment": os.getenv("APP_ENV", "development"),
                "status": "ready"
            }
            self.wfile.write(json.dumps(config_payload).encode("utf-8"))
            return

        return super().do_GET()

    def log_message(self, format, *args):
        # Clean request logging
        sys.stdout.write(f"[Frontend Server] {self.address_string()} - - [{self.log_date_time_string()}] {format % args}\n")

def main():
    global FRONTEND_PORT, FRONTEND_HOST, BACKEND_API_URL

    parser = argparse.ArgumentParser(description="Run Enterprise Payment & Notification Engine Frontend")
    parser.add_argument("--host", default=FRONTEND_HOST, help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=FRONTEND_PORT, help="Port to bind to (default: 28080)")
    parser.add_argument("--backend-url", default=BACKEND_API_URL, help="Backend API URL for frontend client")
    args = parser.parse_args()

    FRONTEND_PORT = args.port
    FRONTEND_HOST = args.host
    BACKEND_API_URL = args.backend_url

    if not is_port_available(FRONTEND_HOST, FRONTEND_PORT):
        print_port_error_and_exit(FRONTEND_PORT, FRONTEND_HOST)

    print("=" * 80)
    print(" Enterprise Payment & Notification Engine - Frontend Dashboard")
    print(f" Dashboard URL : http://localhost:{FRONTEND_PORT}")
    print(f" Bound to      : {FRONTEND_HOST}:{FRONTEND_PORT}")
    print(f" Target Backend: {BACKEND_API_URL}")
    print("=" * 80)

    try:
        httpd = HTTPServer((FRONTEND_HOST, FRONTEND_PORT), FrontendHTTPHandler)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[Frontend Server] Shutting down gracefully.")
        httpd.server_close()
    except OSError as e:
        if "address already in use" in str(e).lower() or getattr(e, "winerror", None) == 10048:
            print_port_error_and_exit(FRONTEND_PORT, FRONTEND_HOST)
        else:
            raise

if __name__ == "__main__":
    main()
