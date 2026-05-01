---
name: clash-reality-sub
description: Generate hidden Clash/Mihomo subscription config files for this repository's nginx static container. Use when the user provides a UUID for the repository default VLESS Reality node and wants a Clash-format YAML config plus the /s/<secret> URL.
---

# Clash Reality Subscription

Use this skill in the `singbox-sub` repository to create hidden Clash/Mihomo YAML files served by the nginx static container.

## Repository Defaults

- Deployment base URL: `https://sub.specode.work`
- The default VLESS Reality node details and routing policy are stored in `templates/mihomo-base.yaml`.
- Normally only `--uuid` changes per generated config.
- Default generated configs include `ipv6: false`, `unified-delay`, sniffer, fake-ip compatibility filters, Apple/Microsoft service groups, CN/private direct rules, and `FINAL` fallback.

## Workflow

1. Treat user-provided node details as sensitive. Do not echo the UUID or Reality public key unless necessary.
2. Run `python3 scripts/generate_config.py --uuid "<uuid>"` from the repository root. Use only `--uuid` for the repository default node.
3. Store generated configs under the repository `configs/` directory. Filenames must be high-entropy tokens that match nginx's `/s/<token>` route.
4. Return the generated file path and full subscription URL under `https://sub.specode.work/s/<token>`. Also include the local Docker URL `http://127.0.0.1:8080/s/<token>` when useful.
5. Remind the user that the URL is a hidden high-entropy link, not strong authentication.

## Script

Use:

```bash
python3 scripts/generate_config.py --uuid "<uuid>"
```

Optional flags:

- `--token`: Explicit hidden URL token. Defaults to a generated high-entropy token.
- `--output-dir`: Output directory. Defaults to `configs`.
- `--base-url`: Deployment base URL. Defaults to `https://sub.specode.work`.
- `--template`: Template path. Defaults to `templates/mihomo-base.yaml`.
- `--force`: Overwrite the output file when `--token` already exists.

## Clash/Mihomo Notes

- Use `type: vless`, `network: tcp`, `tls: true`, `flow: xtls-rprx-vision`.
- Map the user's "Fingerprint" value to `client-fingerprint`, not certificate `fingerprint`.
- Map the user's "key" to `reality-opts.public-key`.
- Map SNI to `servername`.
- Keep the template lightweight: do not add remote rule providers unless the user asks for a heavier ruleset.
- The default split rules rely on Mihomo/Clash.Meta support for `GEOSITE`, `GEOIP`, `IP-CIDR`, and `no-resolve`.
