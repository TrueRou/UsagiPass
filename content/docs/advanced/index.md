---
navigation:
  title: 高级内容
seo:
  title: UsagiPass 实现原理与开发指南
  description: UsagiPass 实现原理与开发指南
---

# UsagiPass 高级内容

本页面包含 UsagiPass 的实现原理，开发指南等相关内容。

## 目录

- [参与开发](#参与开发) - UsagiPass 开源仓库
- [实现原理](#实现原理) - UsagiPass 的设计思路

## 参与开发

UsagiPass 的前后端以及官网均已开源，欢迎提出 Issues 和 PullRequests。

我们的 GitHub 仓库：[https://github.com/TrueRou/UsagiPass](https://github.com/TrueRou/UsagiPass)

## 实现原理

### 华立的设计

当点击公众号的玩家二维码后，**公众号后台**将玩家 ID 和过期时间以一定形式编码成 SGWCMAID。

公众号返回一个 `wq.sys-all.cn` 的网页，查询参数中包含 SGWCMAID，网页根据 SGWCMAID，显示对应的二维码图片和简陋的扫码界面。

舞萌 DX 识别二维码，解析出 SGWCMAID，SGWCMAID 配合机台信息和密钥，向后端请求得到玩家 ID。

> 因为 SGWCMAID 在微信公众号后台生成，对于我们来说属于黑箱，且无法从玩家 ID 逆向得到 SGWCMAID。故印制实体卡片，或者利用单片机实现算号登录的操作在当前情况下是没有可行性的。

### 我们的设计

通过代理替换 `sys-all.cn` 网页，将请求重定向到 `up.turou.fun`，在2025年12月更新后，`sys-all.cn` 网页开始使用 HTTPS，所以我们需要安装 CA 证书以实现 HTTPS 代理。

通过代理重定向时携带原网页中的查询参数（SGWCMAID），在**前端**以 JS 的方式直接绘制出二维码。

> UsagiPass 前后端代码在 GitHub 开源：[https://github.com/TrueRou/UsagiPass](https://github.com/TrueRou/UsagiPass)
