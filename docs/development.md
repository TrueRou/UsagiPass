---
outline: deep
---

# 参与开发

## 开源仓库

UsagiPass 的前后端以及官网均已开源，欢迎提出 Issues 和 PullRequests。

我们的 GitHub 仓库：https://github.com/TrueRou/UsagiPass

## 项目部署

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
