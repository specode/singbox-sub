#!/usr/bin/env python3
import argparse
import os
import re
import secrets
from pathlib import Path
from urllib.parse import urljoin


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://sub.specode.work"
DEFAULT_MIHOMO_TEMPLATE = ROOT / "templates" / "mihomo-base.yaml"
DEFAULT_SINGBOX_TEMPLATE = ROOT / "templates" / "singbox-base.json"
DEFAULT_MIHOMO_OUTPUT_DIR = ROOT / "configs"
DEFAULT_SINGBOX_OUTPUT_DIR = ROOT / "singbox-configs"
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


FORMATS = {
    "mihomo": {
        "template": DEFAULT_MIHOMO_TEMPLATE,
        "output_dir": DEFAULT_MIHOMO_OUTPUT_DIR,
        "extension": ".yaml",
        "route": "s",
    },
    "sing-box": {
        "template": DEFAULT_SINGBOX_TEMPLATE,
        "output_dir": DEFAULT_SINGBOX_OUTPUT_DIR,
        "extension": ".json",
        "route": "sb",
    },
}
FORMAT_CHOICES = sorted([*FORMATS.keys(), "both"])


def build_url(base_url, route, token):
    path = f"/{route}/{token}"
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


def build_output(format_name, uuid, token, template_arg, output_dir_arg, force):
    format_defaults = FORMATS[format_name]
    template_path = resolve_path(template_arg, format_defaults["template"])
    output_dir = resolve_path(output_dir_arg, format_defaults["output_dir"])
    output_path = output_dir / f"{token}{format_defaults['extension']}"

    if not template_path.exists():
        raise SystemExit(f"template not found: {template_path}")
    if output_path.exists() and not force:
        raise SystemExit(f"refusing to overwrite existing config: {display_path(output_path)}")

    return {
        "format": format_name,
        "route": format_defaults["route"],
        "output_dir": output_dir,
        "output_path": output_path,
        "config": build_config(template_path, uuid),
    }


def write_output(output, base_url, token):
    output["output_dir"].mkdir(parents=True, exist_ok=True)
    output["output_path"].write_text(output["config"], encoding="utf-8")
    os.chmod(output["output_path"], 0o644)

    print(f"format={output['format']}")
    print(f"file={display_path(output['output_path'])}")
    print(f"path=/{output['route']}/{token}")
    print(f"url={build_url(base_url, output['route'], token)}")


def main():
    parser = argparse.ArgumentParser(description="Generate a hidden VLESS Reality subscription config.")
    parser.add_argument("--uuid", required=True, help="VLESS user UUID; normally this is the only value that changes.")
    parser.add_argument(
        "--format",
        choices=FORMAT_CHOICES,
        default="mihomo",
        help="Client config format. Use both to generate Mihomo and sing-box configs with the same token.",
    )
    parser.add_argument("--token", help="Hidden URL token. Defaults to a generated high-entropy token.")
    parser.add_argument("--template", help="Template path. Defaults to the selected format's template.")
    parser.add_argument("--output-dir", help="Output directory. Defaults to the selected format's output directory.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Deployment base URL for printed subscription URL.")
    parser.add_argument("--force", action="store_true", help="Overwrite the output file when --token already exists.")
    args = parser.parse_args()

    uuid = validate_uuid(args.uuid)
    token = make_token(args.token)
    selected_formats = list(FORMATS.keys()) if args.format == "both" else [args.format]
    outputs = [
        build_output(format_name, uuid, token, args.template, args.output_dir, args.force)
        for format_name in selected_formats
    ]

    for index, output in enumerate(outputs):
        if index:
            print()
        write_output(output, args.base_url, token)


if __name__ == "__main__":
    main()
