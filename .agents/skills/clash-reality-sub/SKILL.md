---
name: clash-reality-sub
description: Generate hidden Clash/Mihomo subscription config files for this repository's nginx static container from VLESS Reality node parameters. Use when the user provides UUID, Reality public key, server IP, port, flow, SNI, short ID, and client fingerprint, and wants a Clash-format YAML config plus the /s/<secret> URL.
---

# Clash Reality Subscription

Use this skill in the `singbox-sub` repository to create hidden Clash/Mihomo YAML files served by the nginx static container.

## Workflow

1. Treat user-provided node details as sensitive. Do not echo the UUID or Reality public key unless necessary.
2. Run `scripts/generate_config.py` from this skill directory with the provided parameters.
3. Store generated configs under the repository `configs/` directory. Filenames must be high-entropy tokens that match nginx's `/s/<token>` route.
4. Return the generated file path and URL path. If the deployment domain is unknown, report `https://你的域名/s/<token>` and the local Docker URL `http://127.0.0.1:8080/s/<token>`.
5. Remind the user that the URL is a hidden high-entropy link, not strong authentication.

## Script

Use:

```bash
python3 .agents/skills/clash-reality-sub/scripts/generate_config.py \
  --uuid "<uuid>" \
  --public-key "<reality-public-key>" \
  --server "<ip-or-host>" \
  --port "<port>" \
  --flow "xtls-rprx-vision" \
  --sni "<servername>" \
  --short-id "<short-id>" \
  --client-fingerprint "chrome"
```

Optional flags:

- `--name`: Clash proxy name. Defaults to `Reality`.
- `--token`: Explicit hidden URL token. Defaults to a generated high-entropy token.
- `--output-dir`: Output directory. Defaults to `configs`.
- `--base-url`: Deployment base URL. If provided, the script prints the full URL.

## Clash/Mihomo Notes

- Use `type: vless`, `network: tcp`, `tls: true`, `flow: xtls-rprx-vision`.
- Map the user's "Fingerprint" value to `client-fingerprint`, not certificate `fingerprint`.
- Map the user's "key" to `reality-opts.public-key`.
- Map SNI to `servername`.
