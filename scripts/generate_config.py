#!/usr/bin/env python3
import argparse
import os
import re
import secrets
from pathlib import Path
from urllib.parse import urljoin


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://sub.specode.work"
DEFAULT_TEMPLATE = ROOT / "templates" / "mihomo-base.yaml"
DEFAULT_OUTPUT_DIR = ROOT / "configs"
UUID_PLACEHOLDER = "__UUID__"

TOKEN_RE = re.compile(r"^[A-Za-z0-9_-]{16,128}$")
UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{12}$"
)


def resolve_path(path, default):
    if path is None:
        return default
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def validate_uuid(value):
    if not UUID_RE.fullmatch(value):
        raise SystemExit("uuid must be a standard 36-character UUID")
    return value.lower()


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


def build_config(template_path, uuid):
    template = template_path.read_text(encoding="utf-8")
    count = template.count(UUID_PLACEHOLDER)
    if count != 1:
        raise SystemExit(f"template must contain exactly one {UUID_PLACEHOLDER} placeholder")
    return template.replace(UUID_PLACEHOLDER, uuid)


def display_path(path):
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def main():
    parser = argparse.ArgumentParser(description="Generate a hidden Mihomo VLESS Reality config.")
    parser.add_argument("--uuid", required=True, help="VLESS user UUID; normally this is the only value that changes.")
    parser.add_argument("--token", help="Hidden URL token. Defaults to a generated high-entropy token.")
    parser.add_argument("--template", help="Template path. Defaults to templates/mihomo-base.yaml.")
    parser.add_argument("--output-dir", help="Output directory. Defaults to configs.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Deployment base URL for printed subscription URL.")
    parser.add_argument("--force", action="store_true", help="Overwrite the output file when --token already exists.")
    args = parser.parse_args()

    uuid = validate_uuid(args.uuid)
    token = make_token(args.token)
    template_path = resolve_path(args.template, DEFAULT_TEMPLATE)
    output_dir = resolve_path(args.output_dir, DEFAULT_OUTPUT_DIR)
    output_path = output_dir / f"{token}.yaml"

    if not template_path.exists():
        raise SystemExit(f"template not found: {template_path}")
    if output_path.exists() and not args.force:
        raise SystemExit(f"refusing to overwrite existing config: {display_path(output_path)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    config = build_config(template_path, uuid)
    output_path.write_text(config, encoding="utf-8")
    os.chmod(output_path, 0o644)

    print(f"file={display_path(output_path)}")
    print(f"path=/s/{token}")
    print(f"url={build_url(args.base_url, token)}")


if __name__ == "__main__":
    main()
