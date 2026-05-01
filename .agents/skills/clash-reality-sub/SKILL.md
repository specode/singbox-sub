---
name: clash-reality-sub
description: Generate hidden Clash/Mihomo subscription config files for this repository's nginx static container from VLESS Reality node parameters. Use when the user provides UUID, Reality public key, server IP, port, flow, SNI, short ID, and client fingerprint, and wants a Clash-format YAML config plus the /s/<secret> URL.
---

# Clash Reality Subscription

Use this skill in the `singbox-sub` repository to create hidden Clash/Mihomo YAML files served by the nginx static container.

## Repository Defaults

- Deployment base URL: `https://sub.specode.work`
- Generated configs use a lightweight basic split-routing profile by default: private/local/CN traffic is `DIRECT`, and everything else goes through `PROXY`.
- If the user explicitly wants all traffic through the node, pass `--routing-profile global`.

## Workflow

1. Treat user-provided node details as sensitive. Do not echo the UUID or Reality public key unless necessary.
2. Run `scripts/generate_config.py` from this skill directory with the provided parameters.
3. Store generated configs under the repository `configs/` directory. Filenames must be high-entropy tokens that match nginx's `/s/<token>` route.
4. Return the generated file path and full subscription URL under `https://sub.specode.work/s/<token>`. Also include the local Docker URL `http://127.0.0.1:8080/s/<token>` when useful.
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
- `--routing-profile`: `basic` or `global`. Defaults to `basic`.
- `--token`: Explicit hidden URL token. Defaults to a generated high-entropy token.
- `--output-dir`: Output directory. Defaults to `configs`.
- `--base-url`: Deployment base URL. Defaults to `https://sub.specode.work`.

## Clash/Mihomo Notes

- Use `type: vless`, `network: tcp`, `tls: true`, `flow: xtls-rprx-vision`.
- Map the user's "Fingerprint" value to `client-fingerprint`, not certificate `fingerprint`.
- Map the user's "key" to `reality-opts.public-key`.
- Map SNI to `servername`.
- Keep the default `basic` routing profile lightweight: do not add remote rule providers unless the user asks for a heavier ruleset.
- The default split rules rely on Mihomo/Clash.Meta support for `GEOSITE`, `GEOIP`, `IP-CIDR`, and `no-resolve`.
