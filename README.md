# singbox-sub

一个非常轻量、尽量隐蔽的 Clash / sing-box 配置静态分享容器，基于 `nginx:alpine`，没有后端应用、数据库和转换逻辑。

把 Clash/Mihomo 配置文件放进 `configs/` 目录，把 sing-box 配置文件放进 `singbox-configs/` 目录。外部不能直接按文件名访问，只能通过隐藏路由访问：

```text
configs/8f7f1e6df4b1c8a92a9b31d50f0d7e1a.yaml -> https://你的域名/s/8f7f1e6df4b1c8a92a9b31d50f0d7e1a
singbox-configs/51ddaa7d782e46f79c84ab18c920c933.json -> https://你的域名/sb/51ddaa7d782e46f79c84ab18c920c933
```

默认关闭目录列表、根页面、直接文件名访问和访问日志。随机串要求 16 到 128 位，只允许字母、数字、`_`、`-`。

## 本地目录

```text
templates/
  mihomo-base.yaml
  singbox-base.json
scripts/
  generate_config.py
configs/
  8f7f1e6df4b1c8a92a9b31d50f0d7e1a.yaml
  51ddaa7d782e46f79c84ab18c920c933.yaml
singbox-configs/
  3dbbc45e310e4cf3ad986bd9d7a0ec22.json
```

## 生成配置

默认一次生成 Clash/Mihomo 和 sing-box 两份配置，使用同一个隐藏随机串，分别通过 `/s/<随机串>` 和 `/sb/<随机串>` 访问：

```bash
python3 scripts/generate_config.py --format both --uuid "<uuid>"
```

脚本会生成：

```text
format=mihomo
file=configs/<随机串>.yaml
path=/s/<随机串>
url=https://sub.specode.work/s/<随机串>

format=sing-box
file=singbox-configs/<随机串>.json
path=/sb/<随机串>
url=https://sub.specode.work/sb/<随机串>
```

Mihomo 基础配置在 `templates/mihomo-base.yaml`。默认 Reality 节点、DNS、嗅探、fake-ip 兼容列表、Apple/Microsoft 分组和分流规则都固定在模板里，正常只需要替换 UUID：

```bash
python3 scripts/generate_config.py --uuid "<uuid>"
```

脚本会生成 `configs/<随机串>.yaml`，并输出可访问路径：

```text
file=configs/<随机串>.yaml
path=/s/<随机串>
url=https://sub.specode.work/s/<随机串>
```

sing-box 基础配置在 `templates/singbox-base.json`，输出到 `singbox-configs/`，访问路径是 `/sb/<随机串>`：

```bash
python3 scripts/generate_config.py --format sing-box --uuid "<uuid>"
```

脚本会生成：

```text
file=singbox-configs/<随机串>.json
path=/sb/<随机串>
url=https://sub.specode.work/sb/<随机串>
```

如果要沿用已有订阅 URL，只更新同一个隐藏文件：

```bash
python3 scripts/generate_config.py --uuid "<uuid>" --token "<已有随机串>" --force
python3 scripts/generate_config.py --format sing-box --uuid "<uuid>" --token "<已有随机串>" --force
python3 scripts/generate_config.py --format both --uuid "<uuid>" --token "<已有随机串>" --force
```

## Dokploy 部署

1. 新建应用，选择这个 Git 仓库。
2. 构建方式选择 `Dockerfile`。
3. 应用端口填 `80`。
4. 把配置文件放进仓库的 `configs/` 或 `singbox-configs/` 目录，文件名用长随机串；或在 Dokploy 里分别把配置目录挂载到：

```text
/srv/sub-configs
/srv/singbox-configs
```

部署后直接访问：

```text
https://你的域名/s/8f7f1e6df4b1c8a92a9b31d50f0d7e1a
https://你的域名/sb/51ddaa7d782e46f79c84ab18c920c933
```

## 本地运行

```bash
docker build -t singbox-sub .
docker run --rm -p 8080:80 singbox-sub
```

然后访问：

```text
http://127.0.0.1:8080/s/8f7f1e6df4b1c8a92a9b31d50f0d7e1a
http://127.0.0.1:8080/sb/51ddaa7d782e46f79c84ab18c920c933
```

## 说明

- 这是纯静态服务，没有 token、转换、校验逻辑。
- `templates/mihomo-base.yaml` 和 `templates/singbox-base.json` 是基础模板，输出目录里的文件是渲染后的最终订阅。
- `/s/<串>` 会按顺序查找 `<串>.yaml`、`<串>.yml`、`<串>`。
- `/sb/<串>` 会按顺序查找 `<串>.json`、`<串>`。
- 直接访问 `/<文件名>.yaml` 或 `/<文件名>.json` 会返回 404，因为配置目录不在 web root 下。
- 根路径和目录访问都会返回 404。
- 响应带 `X-Robots-Tag: noindex, nofollow, noarchive`，并提供拒绝抓取的 `robots.txt`。
- Clash/Mihomo 配置以 `text/yaml` 返回；sing-box JSON 配置以 `application/json` 返回。
- 这不是强鉴权，只是隐藏入口；真正敏感时应使用足够长的随机串，且不要把 URL 公开传播。
