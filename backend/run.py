import sys
import os
import socket
import argparse
from pathlib import Path

# Ensure workspace root and backend folder are in sys.path
backend_dir = Path(__file__).resolve().parent
root_dir = backend_dir.parent

for d in [str(root_dir), str(backend_dir)]:
    if d not in sys.path:
        sys.path.insert(0, d)

try:
    from backend.app.config import settings
    app_target = "backend.app.main:app"
except ImportError:
    from app.config import settings
    app_target = "app.main:app"

def is_port_available(host: str, port: int) -> bool:
    """Check if the specified host and port can be bound without conflict."""
    # Check by attempting to bind to the port on both IPv4 localhost and all-interfaces
    test_hosts = ["127.0.0.1"]
    if host not in ["127.0.0.1", "localhost"]:
        test_hosts.append("0.0.0.0")

    for th in test_hosts:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # On Windows, do NOT set SO_REUSEADDR as it allows port stealing / false positives
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
[ERROR] PORT CONFLICT DETECTED
================================================================================
The configured backend port {port} on {host} is currently OCCUPIED or in use.

To resolve this conflict and run on another port, choose one of these options:

1. Pass a different port via CLI flag:
     python backend/run.py --port 28091

2. Set the PORT environment variable before starting:
     - PowerShell:  $env:BACKEND_PORT="28091"; python backend/run.py
     - Windows CMD: set BACKEND_PORT=28091 && python backend/run.py
     - Bash/Linux:  BACKEND_PORT=28091 python backend/run.py

3. Update the .env file at the root of the repository:
     BACKEND_PORT=28091
================================================================================
"""
    print(banner, file=sys.stderr)
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Run Enterprise Payment & Notification Engine Backend")
    parser.add_argument("--host", default=settings.HOST, help="Host to bind to (default from env or 0.0.0.0)")
    parser.add_argument("--port", type=int, default=settings.PORT, help="Port to bind to (default from env or 28081)")
    parser.add_argument("--reload", action="store_true", help="Enable uvicorn hot reloading for development")
    args = parser.parse_args()

    # Pre-flight check port availability
    if not is_port_available(args.host, args.port):
        print_port_error_and_exit(args.port, args.host)

    import uvicorn
    print("=" * 80)
    print(f" Starting {settings.APP_NAME}")
    print(f" Environment : {settings.APP_ENV}")
    print(f" Listening on: http://{args.host}:{args.port}")
    print(f" Health check: http://localhost:{args.port}/health")
    print(f" Swagger docs: http://localhost:{args.port}/docs")
    print("=" * 80)

    try:
        uvicorn.run(
            app_target,
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info",
        )
    except OSError as e:
        if "address already in use" in str(e).lower() or getattr(e, "winerror", None) == 10048:
            print_port_error_and_exit(args.port, args.host)
        else:
            raise

if __name__ == "__main__":
    main()
