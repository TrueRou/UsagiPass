---
outline: deep
---

# 参与开发

## 开源仓库

我们的Github仓库: https://github.com/TrueRou/UsagiPass

## 帮助我们

UsagiPass使用代理转发来自sys-all的流量，这使我们的代理服务器压力较大。

有条件的开发者可以搭建属于自己的代理服务器，或者协助我们搭建分布式的代理服务器组。

### 前置环境

- 合适的Linux发行版，这里我们以Debian为例
- 能够连接至Github的网络环境
- Python3.9+

### 搭建方式

1. git clone https://github.com/TrueRou/UsagiPass.git
1. cd UsagiPass/backend
1. pip install mitmproxy
1. mitmweb -s mitm.py --listen-port 2560 --set block_global=false --set connection_strategy=lazy
1. 暴露TCP 2560端口