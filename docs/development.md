---
outline: deep
---

# 参与开发

## 开源仓库

UsagiPass 的前后端以及官网均已开源，欢迎提出 Issues 和 PullRequests。

我们的 GitHub 仓库：https://github.com/TrueRou/UsagiPass

## 配置私人MITM

UsagiPass 使用 [MITM 中间人](https://developer.mozilla.org/zh-CN/docs/Glossary/MitM)转发并修改来自华立服务器的流量。

当前版本的 UsagiPass 会修改来自 wq.sys-all.cn 和 tgk-wcaime.wahlap.com 的流量，后者主要用于更新查分器。

有条件的开发者可以搭建属于自己的代理服务器，可以在降低服务器负载的同时提升安全性。

### 前置环境

- 合适的 Linux 发行版，这里以 Debian 为例
- 能够连接至 GitHub 的网络环境
- Python 3.12+
- MySQL Community Server

### 搭建方式

- 前往对应的查分器网站申请开发者密钥并等待审核通过；
- 在 项目根目录 下创建 `.env` 文件, 可以根据 `.env.example.mitm-only` 模板文件进行配置，别忘了在 `LXNS_DEVELOPER_TOKEN` 或 `DIVINGFISH_DEVELOPER_TOKEN` 中填入你申请的开发者密钥；
- 执行 `pip install poetry` 全局安装 Poetry；
- 执行 `poetry install` 安装项目依赖；
- 执行 `poetry run app` 运行后端及代理；
- 执行 `cd web && npm run dev` 运行前端。

> 更新项目: `git pull && poetry install && poetry run app`

::: tip
切记：必须暴露 TCP `2560` 端口，如部署防火墙的请在规则允许 `2560` 端口的外网访问

端口可以在 `.env` 文件中进行配置
:::