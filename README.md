# UsagiPass

<div align="center">
    <img src="https://s2.loli.net/2024/11/17/wxty6UWMREplhsa.webp" width="300" alt="UsagiPass Logo">
    <h3>动态生成可登录的 DXPASS</h3>
    <p>从零开始美化你的玩家二维码</p>
</div>

![GitHub Repo stars](https://img.shields.io/github/stars/TrueRou/UsagiPass)
![GitHub forks](https://img.shields.io/github/forks/TrueRou/UsagiPass)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/TrueRou/UsagiPass)

## ✨ 主要功能

- **动态生成**：基于水鱼 / 落雪查分器的数据动态生成玩家的 DXPASS，用户个性化数据云端储存；
- **高度自定义**：自定义 DXPASS 背景、外框、角色，支持使用预设素材或个性化上传自己的图片；
- **支持登录**：通过代理直接嵌入微信玩家二维码页面，可直接扫描 DXPASS 上机，逼格满满；
- **更新查分器**：支持一键更新水鱼/落雪查分器，无需复杂的配置。

## 📦 安装使用

查阅 [官网](https://up.turou.fun/) 了解更多，进入 **用户群**：363346002 获取帮助。

## 🛠️ 项目部署

### 前置环境

- Node.js 18+ 或 Bun 1.0+
- pnpm 包管理器
- **PostgreSQL 15.0+** 数据库

### 部署方式

1. **克隆项目并安装依赖**

```bash
git clone https://github.com/TrueRou/UsagiPass.git
cd UsagiPass
pnpm install
```

保证 PostgreSQL 服务已启动，并创建好用于 UsagiPass 的数据库。

2. **配置环境变量**

创建 `.env` 文件，至少配置以下环境变量：

```env
# 数据库配置（请根据实际情况修改：postgresql://用户名:密码@主机:端口/数据库名））
NUXT_USAGIPASS_DATABASE_URL=postgresql://postgres:password@localhost:5432/usagipass
```

3. **启动开发服务器**

```bash
pnpm dev
```

访问 `http://localhost:7200` 即可使用。

### 关于代理

UsagiPass 更新成绩需要配合中间人代理（MITM）使用，在开发环境下，需要使用支持 ClashMeta 规则的代理软件。

在 `pnpm dev` 启动后，默认监听 HTTP 代理 `http://localhost:7300`。

将 `public/UsagiPassDev.yaml` 导入支持 ClashMeta 规则的代理软件后，启动系统代理即可。

## 🤝 支持项目

如果觉得 UsagiPass 好用的话，不妨给我们的仓库点一个 ⭐！

我们也开放了爱发电入口，如果你愿意[赞助 UsagiPass](https://afdian.com/a/turou)，我们会在特别感谢中提到你的名字。

---

Copyright © 2019-2025 TuRou
