---
outline: deep
---

# 实现方式

## 华立的设计

当点击公众号的玩家二维码后，**公众号后台**将玩家 ID 和过期时间以一定形式编码成 SGWCMAID。

公众号返回一个 `wq.wahlap.net` 的网页，查询参数中包含 SGWCMAID。

网页根据 SGWCMAID，显示对应的二维码图片和简陋的扫码界面。

舞萌 DX 识别二维码，解析出 SGWCMAID，SGWCMAID 配合机台信息和密钥，向后端请求得到玩家 ID。

::: tip
因为 SGWCMAID 在微信公众号后台生成，对于我们来说属于黑箱，且无法从玩家 ID 逆向得到 SGWCMAID. 故印制实体卡片，或者利用单片机实现算号登录的操作在当前情况下是没有可行性的。
:::

## 我们的设计

通过代理替换 `wq.wahlap.net` 网页，将请求重定向到 `up.turou.fun`。

重定向时携带原网页中的查询参数（SGWCMAID），在**前端**以 JS 的方式直接绘制出二维码。

::: tip
UsagiPass 前后端代码在 GitHub 开源：[https://github.com/TrueRou/UsagiPass](https://github.com/TrueRou/UsagiPass)。
:::

## 关于更新查分器

在 20241116 更新中，我们支持了更新水鱼和落雪查分器。更新原理类似 [Bakapiano 方案](https://github.com/bakapiano/maimaidx-prober-proxy-updater)。

由于 UsagiPass 天然运行在微信浏览器中，我们就不需要玩家手动复制更新链接到微信并打开了。

我们同时也在代理规则中进行了处理，在合适的时候转发 tgk-wcaime.wahlap.com 地址，来获取玩家 Cookies 进而获取玩家成绩数据。

## 关于CA证书

在 2025 年 12 月底，华立开始给二维码页面使用 HTTPS，所以 UsagiPass 必须安装 CA 证书才能继续使用，我们使用 [node-http-mitm-proxy
](https://github.com/joeferner/node-http-mitm-proxy) 库来实现 HTTPS 的 MITM 代理功能。相关代码也在 GitHub 开源。

根据隐私协议，我们不会使用 CA 证书处理任何非 UsagiPass 相关的 HTTPS 流量。
