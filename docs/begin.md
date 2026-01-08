---
outline: deep
---

# 开始

::: danger 打开网页后提示不安全，或者证书无效
在 2025 年 12 月底，华立开始给二维码页面使用 HTTPS，所以 UsagiPass 必须安装 CA 证书才能继续使用。请确保你已经正确安装了 UsagiPass 的 CA 证书。
:::

## 了解 DXPass

DXPass 是**日服限定**的，可以在制卡机上制作的具有特殊功能的实体卡片。通常印有玩家信息、角色立绘、区域背景等元素，有提升跑图距离、解锁上位难度的谱面等等功能。

![dx-pass-collection](https://s2.loli.net/2024/10/19/13bZcj9NtnW5xDq.webp)

虽然国服无法制作 DXPass，但是独特的微信登录机制使我们有了动态生成 DXPass 的可能，UsagiPass 应运而生。

## 安装 UsagiPass

安装 UsagiPass 需要你具有一定的动手能力，下面我们将逐步讲解如何安装 UsagiPass：

### 第一步：安装 CA 证书

UsagiPass 需要代理 HTTPS 流量以实现二维码页面的替换功能，故需要安装 CA 证书。

::: details 安卓设备
安装为用户证书或无 root：

1. 使用浏览器下载 [https://up.turou.fun/ca.pem](https://up.turou.fun/ca.pem) 并记住存放位置，通常保存在内部存储中的 `/Download` 目录下

2. 打开设备设置，选择安全设置，选择“**加密与凭据**”（实际选项和操作顺序根据不同厂商设定会有所不同）

3. 在“**加密与凭据**”界面下，选择**安装证书->CA 证书**，此时你的设备会弹出安全警示，选择**仍然安装**

4. 系统会跳转至默认文件管理器，在保存的目录找到证书文件并点击即可完成证书安装流程。

成功安装后系统会在通知界面常驻一个风险提示，忽略即可。:)

安装为系统证书（需要 root）：

**警告！此方法高度依赖动手能力，除非你安装用户证书后无效，否则不推荐此方法！**

**本教程不对你因使用此方法而对设备造成的任何损害负责！**

**警告！此方法高度依赖动手能力，除非你安装用户证书后无效，否则不推荐此方法！**

**本教程不对你因使用此方法而对设备造成的任何损害负责！**

**警告！此方法高度依赖动手能力，除非你安装用户证书后无效，否则不推荐此方法！**

**本教程不对你因使用此方法而对设备造成的任何损害负责！**

以任何方法将**安装后的**证书移动至 `/system/etc/security/cacerts/` 目录下

也可加入 UsagiPass 用户群，在群文件获取 Magisk 模块：363346002

更多细节可参阅[这篇文章](https://zhuanlan.zhihu.com/p/675911549)，本文不再赘述
:::

::: details iOS 设备
1. 下载 [https://up.turou.fun/ca.pem](https://up.turou.fun/ca.pem)。

2. 安装证书：去设置->通用->VPN与设备管理，点击证书安装

3. 信任证书：设置->通用->关于本机->证书信任设置，打开开关
:::

### 第二步：配置代理软件

UsagiPass 需要代理才能运行，请根据你的设备选择合适的代理软件：

::: details 安卓设备
推荐使用 **Mihomo**：

1. 下载安装 Mihomo：
   - **Github（推荐）**：[https://github.com/MetaCubeX/ClashMetaForAndroid/releases](https://github.com/MetaCubeX/ClashMetaForAndroid/releases)
   - **蓝奏云（国内）**：[https://wwps.lanzouj.com/iXMCk2cydjmd](https://wwps.lanzouj.com/iXMCk2cydjmd)
   - 加入 UsagiPass 用户群，在群公告处获取：363346002

2. 导入 UsagiPass 配置：
   - 一键导入：[导入 Clash 配置](clash://install-config?url=https://up.turou.fun/UsagiPass.yaml&name=UsagiPass)
   - 复制链接到 Clash 导入：`https://up.turou.fun/UsagiPass.yaml`
   - 从群文件获取配置：363346002
:::

::: details iOS 设备
推荐使用 **Singbox**：

1. 切换外区账号，在 AppStore 中搜索 **Singbox VT** 并下载

2. Profiles -> New Profile -> Name: 随意，Type: Remote，URL: `https://up.turou.fun/UsagiPass.json` -> Create

3. **确保选择了 UsagiPass 配置，点击启动代理即可生效！**
:::

### 第三步：访问 UsagiPass

1. 在**微信 -> 舞萌|中二公众号**中正常打开**登入二维码**

2. 你应该已经跳转到 UsagiPass 的登录界面

3. 使用水鱼或落雪查分器账号进行登录

4. 登录后即可进入 UsagiPass 主页，享受可登录的国服 DXPass 功能

## 支持 UsagiPass

如果觉得 UsagiPass 好用的话，不妨给[我们的仓库](https://github.com/TrueRou/UsagiPass)点一个 ⭐ 吧。

我们也开放了爱发电入口，如果你愿意[赞助 UsagiPass](https://afdian.com/a/turou) 我们会在特别感谢中提到你的名字。

## 常见问题

### Q: 打开网页后提示不安全，或者证书无效

A: 请确保你已经正确安装了 UsagiPass 的 CA 证书。

**Q：我不清楚 UsagiPass 的某某功能如何使用**

A：可以在左侧的目录（手机用户请点击左上角 Menu 按钮）中找到部分功能的详细介绍。如果仍有疑问，可以加群进行询问。

**Q：IOS 使用小火箭需要购买**

A：可以使用 Sing-box 方案，Sing-box 是一款在外区商店可以免费下载的代理软件。

**Q：IOS 我不知道应该如何获得外区账号**

A：可以在 B 站搜索相关关键词，这类视频还是挺多的，请尽量不要在群内讨论相关话题。

**Q：在按照步骤配置后，我无法打开 UsagiPass 网页**

A：UsagiPass 目前使用阿里云托管，域名使用阿里云个人版云解析，并且已经在工信部备案，可保证国内各地区的正常访问。

你可以随时访问我们的[状态监控](https://status.turou.fun/)页面，查看 UsagiPass 的运行状态。

若你在自行诊断后仍然出现无法连接的问题，请加群联系我们，我们会根据你的地区向阿里云发起工单，尝试解决你的问题。

另外，如果你的错误代码在下面表格中列出：

- **ERR_PROXY_CONNECTION_FAILED**
- **ERR_CONNECTION_TIMED_OUT**
- **ERR_HTTP_RESPONSE_CODE_FAILURE**

可能是代理连接不正确，请重启代理、重启手机、更换代理软件后重试。
