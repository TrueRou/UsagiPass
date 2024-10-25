---
outline: deep
---

# 参与开发

## 开源仓库

我们的 GitHub 仓库: https://github.com/TrueRou/UsagiPass

## 帮助我们

UsagiPass 使用代理转发来自 sys-all 的流量，这使我们的代理服务器压力较大。

有条件的开发者可以搭建属于自己的代理服务器，或者协助我们搭建分布式的代理服务器组。

### 前置环境

- 合适的 Linux 发行版，这里以 Debian 为例
- 能够连接至 GitHub 的网络环境
- Python 3.9+

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

启动时请使用 `-t` 参数，否则将没有日志输出
:::

```docker
FROM python:3.9-alpine AS fetch
RUN sed -i 's#https\?://dl-cdn.alpinelinux.org/alpine#https://mirrors.tuna.tsinghua.edu.cn/alpine#g' /etc/apk/repositories && \
    apk update && apk upgrade && apk add --no-cache --latest ca-certificates git && update-ca-certificates
RUN git clone https://github.com/TrueRou/UsagiPass.git

FROM python:3.9-alpine
EXPOSE 2560
COPY --from=fetch /UsagiPass/backend/* /app/
ENV PATH=/root/.cargo/bin:/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV RUSTUP_UPDATE_ROOT=https://mirrors.tuna.tsinghua.edu.cn/rustup/rustup
RUN sed -i 's#https\?://dl-cdn.alpinelinux.org/alpine#https://mirrors.tuna.tsinghua.edu.cn/alpine#g' /etc/apk/repositories \
    && apk update && apk upgrade && apk add --no-cache --latest build-base bsd-compat-headers ca-certificates curl && update-ca-certificates \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal \
    && pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --verbose mitmproxy \
    && pip cache purge && rustup self uninstall -y && apk del build-base bsd-compat-headers curl \
    && apk add --no-cache --latest libgcc libstdc++
WORKDIR /app
ENTRYPOINT [ "mitmweb" ]
CMD [ "-s", "mitm.py", "--listen-port", "2560", "--set", "block_global=false", "--set", "connection_strategy=lazy" ]
```
