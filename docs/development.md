---
outline: deep
---

# 参与开发

## 开源仓库

UsagiPass的前端 & 后端 & 官网均已开源，欢迎提出Issues和PullRequests。

我们的 GitHub 仓库: https://github.com/TrueRou/UsagiPass

## 配置私人MITM

UsagiPass 使用 [MITM中间人](https://developer.mozilla.org/zh-CN/docs/Glossary/MitM) 转发并修改来自华立服务器的流量。

当前版本的 UsagiPass 会修改来自 wq.sys-all.cn 和 tgk-wcaime.wahlap.com 的流量，后者主要用于更新查分器。

有条件的开发者可以搭建属于自己的代理服务器，可以在降低服务器负载的同时提升安全性。

### 前置环境

- 合适的 Linux 发行版，这里以 Debian 为例
- 能够连接至 GitHub 的网络环境
- Python 3.11+

### 搭建方式

1. 依次输入以下命令

```shell
apt-get update && apt install -y git python3-pip
git clone https://github.com/TrueRou/UsagiPass.git
cd UsagiPass/backend
pip3 install mitmproxy
mitmweb -s mitm.py --listen-port 2560 --set block_global=false --set connection_strategy=lazy
```

::: tip
切记：必须暴露 TCP `2560` 端口，如部署防火墙的请在规则允许 `2560` 端口的外网访问
:::

### Docker

::: tip
感谢群友 原味零花 提供的 Dockerfile, 需要的开发者可以加群获取
:::

```docker
FROM debian AS fetch
RUN apt update && apt install git ca-certificates -y && update-ca-certificates
RUN git clone https://github.com/TrueRou/UsagiPass.git

FROM debian
EXPOSE 2560
COPY --from=fetch /UsagiPass/backend/* /app/backend/
RUN apt update && apt install pipx python3-minimal ca-certificates -y && update-ca-certificates
RUN pipx install mitmproxy
WORKDIR /app/backend
ENTRYPOINT [ "/root/.local/bin/mitmweb" ]
CMD [ "-s", "mitm.py", "--listen-port", "2560", "--set", "block_global=false", "--set", "connection_strategy=lazy" ]
```