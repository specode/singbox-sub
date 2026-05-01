# singbox-sub

一个非常轻量、尽量隐蔽的 Clash / sing-box 配置静态分享容器，基于 `nginx:alpine`，没有后端应用、数据库和转换逻辑。

把配置文件放进 `configs/` 目录，但外部不能直接按文件名访问，只能通过 `/s/<长随机串>` 访问：

```text
configs/8f7f1e6df4b1c8a92a9b31d50f0d7e1a.yaml -> https://你的域名/s/8f7f1e6df4b1c8a92a9b31d50f0d7e1a
```

默认关闭目录列表、根页面、直接文件名访问和访问日志。随机串要求 16 到 128 位，只允许字母、数字、`_`、`-`。

## 本地目录

```text
configs/
  8f7f1e6df4b1c8a92a9b31d50f0d7e1a.yaml
  51ddaa7d782e46f79c84ab18c920c933.yaml
```

生成随机文件名：

```bash
openssl rand -hex 32
```

## Dokploy 部署

1. 新建应用，选择这个 Git 仓库。
2. 构建方式选择 `Dockerfile`。
3. 应用端口填 `80`。
4. 把配置文件放进仓库的 `configs/` 目录，文件名用长随机串；或在 Dokploy 里把你的配置目录挂载到：

```text
/srv/sub-configs
```

部署后直接访问：

```text
https://你的域名/s/8f7f1e6df4b1c8a92a9b31d50f0d7e1a
```

## 本地运行

```bash
docker build -t singbox-sub .
docker run --rm -p 8080:80 singbox-sub
```

然后访问：

```text
http://127.0.0.1:8080/s/8f7f1e6df4b1c8a92a9b31d50f0d7e1a
```

## 说明

- 这是纯静态服务，没有 token、转换、校验逻辑。
- `/s/<串>` 会按顺序查找 `<串>.yaml`、`<串>.yml`、`<串>`。
- 直接访问 `/<文件名>.yaml` 会返回 404，因为配置目录不在 web root 下。
- 根路径和目录访问都会返回 404。
- 响应带 `X-Robots-Tag: noindex, nofollow, noarchive`，并提供拒绝抓取的 `robots.txt`。
- `.yaml` / `.yml` 和无后缀随机串路径都会以 `text/yaml` 返回。
- 这不是强鉴权，只是隐藏入口；真正敏感时应使用足够长的随机串，且不要把 URL 公开传播。
