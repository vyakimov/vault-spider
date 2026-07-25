"""Launcher for the web app: `vault-spider-web` / `./bin/vault-spider-web`."""

from __future__ import annotations

import argparse
import socket
import sys

DEFAULT_PORT = 8765


def lan_address() -> str:
    """This machine's address on the local network, for the URL printed at startup."""
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No packets are sent; connecting a UDP socket just picks the outbound interface.
        probe.connect(("192.0.2.1", 1))
        return probe.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        probe.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vault-spider-web",
        description="Serve the Vault Spider reading and retrieval app.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help=(
            "Interface to bind. The default keeps the app on this machine; pass "
            "0.0.0.0 to reach it from your phone on the same network."
        ),
    )
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument(
        "--reload", action="store_true", help="Restart on code changes (development)."
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    import uvicorn

    from vault_spider.web.state import StartupError, build_state

    # Fail before uvicorn starts, so a missing vault or empty index reads as one clear
    # line rather than a traceback inside the server's startup.
    try:
        build_state()
    except StartupError as exc:
        print(f"Cannot start: {exc}", file=sys.stderr)
        return 1

    if args.host in ("0.0.0.0", "::"):
        print(f"  On this machine:  http://127.0.0.1:{args.port}")
        print(f"  On your network:  http://{lan_address()}:{args.port}")
        print("  Anyone on this network can read your vault at that address.\n")
    else:
        print(f"  http://{args.host}:{args.port}\n")

    uvicorn.run(
        "vault_spider.web.app:create_app",
        factory=True,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="warning",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
