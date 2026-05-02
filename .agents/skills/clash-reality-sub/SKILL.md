---
name: clash-reality-sub
description: Generate hidden Clash/Mihomo and sing-box subscription config files for this repository's nginx static container. Use when the user provides a UUID for the repository default VLESS Reality node and wants subscription URLs. By default generate both client configs: Clash/Mihomo YAML at /s/<secret> and sing-box JSON at /sb/<secret>.
---

# Reality Subscription Pair

Use this skill in the `singbox-sub` repository to create hidden Clash/Mihomo YAML and sing-box JSON files served by the nginx static container.

## Repository Defaults

- Deployment base URL: `https://sub.specode.work`
- The default VLESS Reality node details and routing policy are stored in `templates/mihomo-base.yaml` and `templates/singbox-base.json`.
- Normally only `--uuid` changes per generated config.
- Mihomo configs are stored in `configs/` and served as `https://sub.specode.work/s/<token>`.
- sing-box configs are stored in `singbox-configs/` and served as `https://sub.specode.work/sb/<token>`.
- Default generated configs include the same VLESS Reality node, Apple/Microsoft service groups, CN/private direct rules, and proxy fallback.

## Workflow

1. Treat user-provided node details as sensitive. Do not echo the UUID or Reality public key unless necessary.
2. Run `python3 scripts/generate_config.py --format both --uuid "<uuid>"` from the repository root. Use only `--uuid` for the repository default node.
3. Store generated configs under `configs/` and `singbox-configs/`. Filenames must be high-entropy tokens that match nginx's `/s/<token>` and `/sb/<token>` routes.
4. Return both generated file paths and full subscription URLs. Also include local Docker URLs when useful.
5. Remind the user that the URL is a hidden high-entropy link, not strong authentication.

## Script

Use:

```bash
python3 scripts/generate_config.py --format both --uuid "<uuid>"
```

Optional flags:

- `--format`: `both`, `mihomo`, or `sing-box`. Use `both` unless the user specifically asks for one client.
- `--token`: Explicit hidden URL token. Defaults to a generated high-entropy token.
- `--base-url`: Deployment base URL. Defaults to `https://sub.specode.work`.
- `--force`: Overwrite the output file when `--token` already exists.

## Clash/Mihomo Notes

- Use `type: vless`, `network: tcp`, `tls: true`, `flow: xtls-rprx-vision`.
- Map the user's "Fingerprint" value to `client-fingerprint`, not certificate `fingerprint`.
- Map the user's "key" to `reality-opts.public-key`.
- Map SNI to `servername`.
- Keep the template lightweight: do not add remote rule providers unless the user asks for a heavier ruleset.
- The default split rules rely on Mihomo/Clash.Meta support for `GEOSITE`, `GEOIP`, `IP-CIDR`, and `no-resolve`.

## sing-box Notes

- Use JSON config files from `templates/singbox-base.json`.
- Use `type: vless`, `flow: xtls-rprx-vision`, `packet_encoding: xudp`, and TLS Reality under `tls.reality`.
- Map SNI to `tls.server_name`, fingerprint to `tls.utls.fingerprint`, public key to `tls.reality.public_key`, and short ID to `tls.reality.short_id`.
- For iOS/App Store graphical client compatibility, keep DNS servers in legacy `address` form instead of the newer `dns.servers[].type` form.
- Avoid newer-only fields such as `route.default_domain_resolver`, `route.rule_set[].http_client`, `dns.cache_file.store_dns`, and TUN `strict_route` unless the user confirms their client core accepts them.
- Use remote binary rule-sets under `route.rule_set`; use `download_detour` for compatibility with current graphical clients.
