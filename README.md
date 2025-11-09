# UsagiPass

<div align="center">
    <img src="https://s2.loli.net/2024/11/17/wxty6UWMREplhsa.webp" width="300" alt="UsagiPass Logo">
    <h3>动态生成可登录的 DXPASS</h3>
    <p>从零开始美化你的玩家二维码</p>
</div>

## 什么是 UsagiPass？

DXPass 是**日服限定**的，可以在制卡机上制作的具有特殊功能的实体卡片。通常印有玩家信息、角色立绘、区域背景等元素，有提升跑图距离、解锁上位难度的谱面等功能。

虽然国服无法制作 DXPass，但是独特的微信登录机制使我们有了动态生成 DXPass 的可能，UsagiPass 应运而生。

## ✨ 主要功能

- **动态生成**：基于水鱼 / 落雪查分器的数据动态生成玩家的 DXPASS，用户个性化数据云端储存；
- **高度自定义**：自定义 DXPASS 背景、外框、角色，支持使用预设素材或个性化上传自己的图片；
- **支持登录**：通过代理直接嵌入微信玩家二维码页面，可直接扫描 DXPASS 上机，逼格满满；
- **更新查分器**：支持一键更新水鱼/落雪查分器，无需复杂的配置。

## 📦 安装使用

### 安装步骤

1. **安装代理软件**：
     - 安卓：[**Clash（推荐）**](https://dxpass.turou.fun/proxies/clash.html)，[Sing-box](https://dxpass.turou.fun/proxies/singbox.html)
     - iOS：[**Shadowrocket（推荐）**](https://dxpass.turou.fun/proxies/rocket.html)，[Sing-box](https://dxpass.turou.fun/proxies/singbox.html)，[QuantX](https://dxpass.turou.fun/proxies/quantx.html)

2. **启动代理**：确保代理软件在手机后台运行中；

3. **打开微信二维码**：在微信中打开舞萌或中二公众号的**登入二维码**，将自动跳转至 UsagiPass 登录界面；

4. **登录使用**：使用水鱼或落雪查分器账号进行登录，登录后即可进入 UsagiPass 主页。

### 使用方法

1. 登录后将显示默认个性化配置，点击画面右下方的齿轮图标进入设置页面；
2. 在设置中按照喜好调整个性化配置，切换背景、角色、边框等资源；
3. 请初次使用的玩家在设置中粘贴自己的好友代码（可在舞萌DX-好友页面查询）；
4. 修改完成后点击保存按钮应用设置。

## 🔧 技术实现

UsagiPass 利用中间人代理（MITM）技术修改华立服务器的流量：

1. 通过代理替换 sys-all.cn 网页，将请求重定向到 dxpass.turou.fun；
2. 重定向时携带原网页中的查询参数（SGWCMAID），在前端以 JS 方式绘制二维码；
3. 支持更新查分器功能，原理类似 [Bakapiano 方案](https://github.com/bakapiano/maimaidx-prober-proxy-updater)，在适当时机转发 tgk-wcaime.wahlap.com 地址。

## 🤔 常见问题

**Q：我不清楚 UsagiPass 的某某功能如何使用**

A：可以在[官网](https://dxpass.turou.fun/)中找到部分功能的详细介绍。如果仍有疑问，可以加群进行询问。

**Q：IOS 使用小火箭需要购买**

A：可以使用 Sing-box 方案，Sing-box 是一款在外区商店可以免费下载的代理软件。

**Q：IOS 我不知道应该如何获得外区账号**

A：可以在 B 站搜索相关关键词，这类视频还是挺多的，请尽量不要在群内讨论相关话题。

## 🤝 支持项目

如果觉得 UsagiPass 好用的话，不妨给我们的仓库点一个 ⭐！

我们也开放了爱发电入口，如果你愿意[赞助 UsagiPass](https://afdian.com/a/turou)，我们会在特别感谢中提到你的名字。

## 🛠️ 开发者部署

### 前置环境

- node.js with pnpm
- PostgreSQL 15.0+

### 部署方式

- 在 项目根目录 下创建 `.env` 文件, 可以根据 `.env.example` 模板文件进行配置。
- 执行 `pnpm install` 安装所需依赖。
- 执行 `pnpm db:push` 初始化数据库。
- 执行 `pnpm dev` 启动开发服务器。

> 更新项目: `git pull && pnpm install && pnpm db:push && pnpm dev`

> 第一次部署时，可以执行 `pnpm db:seed` 来插入一些初始数据（联动服务器定义）。

### 关于代理

UsagiPass更新查分器功能需要配合中间人代理（MITM）使用，在开发环境下，需要使用支持 ClashMeta 规则的代理软件。

在 `pnpm dev` 启动后，默认监听 HTTP 代理 `http://localhost:7300`。

将 `shared/rules/Developement.yaml` 导入支持 ClashMeta 规则的代理软件后，启动系统代理即可。

## 📱 联系我们

- **用户群**：363346002

---

Copyright © 2019-2025 TuRou
