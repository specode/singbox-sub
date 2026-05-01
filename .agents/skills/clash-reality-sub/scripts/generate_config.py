#!/usr/bin/env python3
import argparse
import os
import re
import secrets
from pathlib import Path
from urllib.parse import urljoin


TOKEN_RE = re.compile(r"^[A-Za-z0-9_-]{16,128}$")


def quote(value):
    text = str(value)
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_config(args):
    name = args.name
    return f"""mixed-port: 7890
allow-lan: false
mode: rule
log-level: info

proxies:
  - name: {quote(name)}
    type: vless
    server: {quote(args.server)}
    port: {int(args.port)}
    uuid: {quote(args.uuid)}
    udp: true
    tls: true
    network: tcp
    flow: {quote(args.flow)}
    packet-encoding: xudp
    servername: {quote(args.sni)}
    client-fingerprint: {quote(args.client_fingerprint)}
    reality-opts:
      public-key: {quote(args.public_key)}
      short-id: {quote(args.short_id)}
    encryption: ""

proxy-groups:
  - name: PROXY
    type: select
    proxies:
      - {quote(name)}
      - DIRECT

rules:
  - MATCH,PROXY
"""


def make_token(explicit):
    token = explicit or secrets.token_urlsafe(32)
    if not TOKEN_RE.fullmatch(token):
        raise SystemExit("token must be 16-128 chars and contain only A-Z, a-z, 0-9, _ or -")
    return token


def build_url(base_url, token):
    path = f"/s/{token}"
    if not base_url:
        return path
    return urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))


def main():
    parser = argparse.ArgumentParser(description="Generate a hidden Clash/Mihomo VLESS Reality config.")
    parser.add_argument("--uuid", required=True)
    parser.add_argument("--public-key", required=True)
    parser.add_argument("--server", required=True)
    parser.add_argument("--port", required=True, type=int)
    parser.add_argument("--flow", default="xtls-rprx-vision")
    parser.add_argument("--sni", required=True)
    parser.add_argument("--short-id", required=True)
    parser.add_argument("--client-fingerprint", default="chrome")
    parser.add_argument("--name", default="Reality")
    parser.add_argument("--token")
    parser.add_argument("--output-dir", default="configs")
    parser.add_argument("--base-url")
    args = parser.parse_args()

    if args.port < 1 or args.port > 65535:
        raise SystemExit("port must be between 1 and 65535")

    token = make_token(args.token)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{token}.yaml"
    if output_path.exists():
        raise SystemExit(f"refusing to overwrite existing config: {output_path}")

    config = build_config(args)
    output_path.write_text(config, encoding="utf-8")
    os.chmod(output_path, 0o644)

    print(f"file={output_path}")
    print(f"path=/s/{token}")
    print(f"url={build_url(args.base_url, token)}")


if __name__ == "__main__":
    main()
