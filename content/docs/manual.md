---
navigation:
  title: 手册
seo:
  title: UsagiPass 使用文档
  description: UsagiPass 完整使用指南 - 动态生成可登录的 DXPASS
---

# UsagiPass 使用文档

欢迎使用 UsagiPass！本文档将帮助你快速上手并充分利用 UsagiPass 的各项功能。

## 目录

- [什么是 DXPass](#什么是-dxpass) - 了解 DXPass 的基本概念
- [快速开始](#快速开始) - 安装代理软件，开始使用 UsagiPass
  - [安卓设备](#安卓设备) - Clash/Mihomo 和 Sing-box 配置
  - [iOS 设备](#ios-设备) - Sing-box 和 Shadowrocket 配置
- [常见问题](#常见问题) - 解答使用过程中的疑问
- [支持我们](#支持我们) - 给予 Star 或赞助支持
- [联系我们](#联系我们) - 加入社区和获取帮助
- [特别感谢](#特别感谢) - 致谢支持 UsagiPass 的朋友们

---

## 什么是 DXPass

DXPass 是**日服限定**的，可以在制卡机上制作的具有特殊功能的实体卡片。通常印有玩家信息、角色立绘、区域背景等元素，有提升跑图距离、解锁上位难度的谱面等功能。

![dx-pass-collection](https://s2.loli.net/2024/10/19/13bZcj9NtnW5xDq.webp)

虽然国服无法制作 DXPass，但是独特的微信登录机制使我们有了动态生成 DXPass 的可能，UsagiPass 应运而生。

---

## 快速开始

### 第零步：安装 CA 证书

UsagiPass 需要代理 HTTPS 流量以实现二维码页面的替换功能，故需要安装 CA 证书：[https://up.turou.fun/ca.pem](https://up.turou.fun/ca.pem)

### 第一步：安装代理软件

UsagiPass 需要代理才能运行，请根据你的设备选择合适的代理软件：

#### 安卓设备

推荐使用 **Clash/Mihomo**：

1. 下载安装 Clash/Mihomo（原 ClashMeta）：
   - **Github（推荐）**：[https://github.com/MetaCubeX/ClashMetaForAndroid/releases](https://github.com/MetaCubeX/ClashMetaForAndroid/releases)
   - **蓝奏云（国内）**：[https://wwps.lanzouj.com/iXMCk2cydjmd](https://wwps.lanzouj.com/iXMCk2cydjmd)
   - 加入 UsagiPass 用户群，在群公告处获取：363346002

2. 导入 UsagiPass 配置：
   - 一键导入：[导入 Clash 配置](clash://install-config?url=https://up.turou.fun/UsagiPass.yaml&name=UsagiPass)
   - 复制链接到 Clash 导入：`https://up.turou.fun/UsagiPass.yaml`
   - 从群文件获取配置：363346002

3. **确保选择了 UsagiPass 配置，点击启动代理即可生效！**

也可以使用 **Sing-box**：
1. 下载 Sing-box
   - **Github（推荐）**：[https://github.com/SagerNet/sing-box/releases](https://github.com/SagerNet/sing-box/releases)
   - Google Play：搜索 Sing-box 并下载
   - 加入用户群获取：363346002

2. Profiles -> 新建图标 -> **Create Manually** -> Name: 随意，Type: Remote，URL: `https://up.turou.fun/UsagiPass.json` -> Create

3. 确保选择了 UsagiPass 配置，点击启动代理即可生效！

**注意**：如果在导入文件过程中出现 invalid message 错误，请仔细阅读导入流程（一定要选择 Create Manually，而不是 Import from file）。

#### iOS 设备

推荐使用 **Sing-box**（免费方案）：

1. 切换外区账号，在 AppStore 中搜索 **Sing-box VT** 并下载

2. Profiles -> New Profile -> Name: 随意，Type: Remote，URL: `https://up.turou.fun/UsagiPass.json` -> Create

3. **确保选择了 UsagiPass 配置，点击启动代理即可生效！**

**Shadowrocket（小火箭）** 方案（需要购买）：

Shadowrocket 需要美区账号，且购买后才能安装。如果你对如何获取小火箭感到疑惑，推荐使用上述 Sing-box 方案。

如果已经有小火箭：
1. 导入配置：
   - 一键导入：[导入配置](clash://install-config?url=https://up.turou.fun/UsagiPass.yaml&name=UsagiPass)
   - 或复制链接到小火箭导入：`https://up.turou.fun/UsagiPass.yaml`
   - 从群文件获取配置：363346002

2. **确保选择了 UsagiPass 配置，确保"全局代理"处开启了配置模式，点击启动代理即可生效！**

### 第二步：启动代理

确保你的代理软件已经在手机后台运行，UsagiPass 必须在代理运行的情况下才能正常工作。

### 第三步：打开 UsagiPass

1. 在**微信 -> 舞萌|中二公众号**中正常打开**登入二维码**
2. 你应该已经跳转到 UsagiPass 的登录界面
3. 使用水鱼或落雪查分器账号进行登录
4. 登录后即可进入 UsagiPass 主页，享受可登录的国服 DXPass 功能

---

## 常见问题

### Q：我不清楚 UsagiPass 的某某功能如何使用

A：可以仔细阅读本文档的相关章节。如果仍有疑问，可以加群进行询问。

### Q：iOS 使用小火箭需要购买

A：可以使用 Sing-box 方案，Sing-box 是一款在外区商店可以免费下载的代理软件。

### Q：iOS 我不知道应该如何获得外区账号

A：可以在 B 站搜索相关关键词，这类视频还是挺多的，请尽量不要在群内讨论相关话题。

### Q：在按照步骤配置后，我无法打开 UsagiPass 网页

A：UsagiPass 目前使用阿里云托管，域名使用阿里云个人版云解析，并且已经在工信部备案，可保证国内各地区的正常访问。

你可以随时访问我们的[状态监控](https://status.turou.fun/)页面，查看 UsagiPass 的运行状态。

若你在自行诊断后仍然出现无法连接的问题，请加群联系我们，我们会根据你的地区向阿里云发起工单，尝试解决你的问题。

另外，如果你的错误代码在下面表格中列出：

- **ERR_PROXY_CONNECTION_FAILED**
- **ERR_CONNECTION_TIMED_OUT**
- **ERR_HTTP_RESPONSE_CODE_FAILURE**

可能是代理连接不正确，请重启代理、重启手机、更换代理软件后重试。

### Q: 打开网页后提示不安全，或者证书无效

A: 请确保你已经正确安装了 UsagiPass 的 CA 证书。

---

## 支持我们

如果觉得 UsagiPass 好用的话，不妨给[我们的仓库](https://github.com/TrueRou/UsagiPass)点一个 ⭐ 吧。

我们也开放了爱发电入口，如果你愿意[赞助 UsagiPass](https://afdian.com/a/turou) 我们将非常感激。

---

## 联系我们

- **用户群**：363346002
- **GitHub**：[https://github.com/TrueRou/UsagiPass](https://github.com/TrueRou/UsagiPass)
- **博客**：[https://turou.fun/](https://turou.fun/)
- **爱发电**：[https://afdian.com/a/turou](https://afdian.com/a/turou)

---

## 特别感谢

特别感谢朋友们对 UsagiPass 的支持和贡献，以下排名不分先后：

- MisakaNo
- Sanzisbar
- 阿日
- ✯以太✬
- fxysk
- 柠檬诺lemon
- 原味零花
- 生盐诺亚
- Dream_Rain
- AxelPLN
- FrZ
- 星露
- 可乐不加冰

另外，UsagiPass 建立在许多开源项目和开发者的技术积累上，特别感谢以下开发者和相关项目：

- Diving-Fish：[https://www.diving-fish.com/maimaidx/prober/](https://www.diving-fish.com/maimaidx/prober/)
- LXNS：[https://maimai.lxns.net/](https://maimai.lxns.net/)
- Bakapiano：[https://github.com/bakapiano/maimaidx-prober-proxy-updater](https://github.com/bakapiano/maimaidx-prober-proxy-updater)
- maimai.py：[https://github.com/TrueRou/maimai.py](https://github.com/TrueRou/maimai.py)
