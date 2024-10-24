---
outline: deep
---

# 开始

## 了解DXPass

DXPass是**日服限定**的, 可以在制卡机上制作的具有特殊功能的实体卡片. 通常印有玩家信息, 角色立绘, 区域背景等元素, 有提升跑图距离、解锁上位难度的谱面等等功能.

![dx-pass-collection](https://s2.loli.net/2024/10/19/13bZcj9NtnW5xDq.webp)

虽然国服无法制作DXPass, 但是独特的微信登录机制使我们有了动态生成DXPass的可能, UsagiPass应运而生.

## 安装UsagiPass

### 安卓设备

#### Clash 使用方法

1. 安装Clash / ClashMeta: 
    - **Github(推荐)**: [https://github.com/MetaCubeX/ClashMetaForAndroid/releases](https://github.com/MetaCubeX/ClashMetaForAndroid/releases)
    - **蓝奏云(国内)**: [https://wwps.lanzouj.com/iXMCk2cydjmd](https://wwps.lanzouj.com/iXMCk2cydjmd)
    - 加入UsagiPass用户群获取: 363346002
2. 导入UsagiPass配置
    - 一键导入: [导入Clash配置](clash://install-config?url=https://dxpass.turou.fun/UsagiPass.yaml&name=UsagiPass)
    - 复制链接到Clash导入: https://dxpass.turou.fun/UsagiPass.yaml
    - 也可以加群下载文件, 从文件导入: 363346002
3. **选择该配置, 点击启动代理, 并保证ClashMeta在后台运行**
4. 在微信中打开玩家二维码, 按照提示登录水鱼查分器账号

#### Sing-box 使用方法

1. 安装Sing-box: 
    - **Github(推荐)**: [https://github.com/SagerNet/sing-box/releases](https://github.com/SagerNet/sing-box/releases)
    - 加入UsagiPass用户群获取: 363346002
2. 导入UsagiPass配置
    - 复制链接到Sing-box导入: https://dxpass.turou.fun/UsagiPass.json
    - 也可以加群下载文件, 从文件导入: 363346002
3. **选择该配置, 点击启动代理, 并保证Sing-box在后台运行**
4. 在微信中打开玩家二维码, 按照提示登录水鱼查分器账号

::: tip
UsagiPass利用代理来重定向华立二维码网页, 请保证在使用过程中代理不要关闭.
:::

### IOS设备

#### Shadowrocket(小火箭) 使用方法

1. 安装Shadowrocket(小火箭): 
    - 请自行寻找安装方法
    - 加入UsagiPass用户群寻求帮助: 363346002
2. 导入UsagiPass配置
    - 一键导入: [导入Clash配置](clash://install-config?url=https://dxpass.turou.fun/UsagiPass.yaml&name=UsagiPass)
    - 复制链接到小火箭导入: https://dxpass.turou.fun/UsagiPass.yaml
3. **选择该配置, 点击启动代理, 并保证Shadowrocket在后台运行**
4. 在微信中打开玩家二维码, 按照提示登录水鱼查分器账号

#### Sing-box 使用方法

1. 安装Shadowrocket(小火箭)作为代理工具: 
    - 请自行寻找安装方法
    - 加入UsagiPass用户群寻求帮助: 363346002
2. 导入UsagiPass配置
    - 复制链接到 Sing-box 导入: https://dxpass.turou.fun/UsagiPass.json
3. **选择该配置, 点击启动代理, 并保证Shadowrocket在后台运行**
4. 在微信中打开玩家二维码, 按照提示登录水鱼查分器账号
   
::: tip
QuantX规则绝赞制作中
:::

## 使用UsagiPass

登录UsagiPass后, 将使用默认的个性化配置, 点击画面右下方的齿轮图标可以进入设置页面.

在设置中, 可以按照喜好调整个性化配置, 切换背景、角色、边框等资源, 在调整结束后可以点击最下方的保存.

请初次使用的玩家在设置中粘贴自己的好友代码(可以在舞萌DX-好友页面查询).

同时, 我们还支持覆盖页面中的部分文本, 玩家可以自行尝试相关功能.

::: tip
上传自定义背景、角色、边框的功能尚在开发中
:::

## 支持UsagiPass

如果觉得UsagiPass好用的话, 不妨给[我们的仓库](https://github.com/TrueRou/UsagiPass)点一个Star吧

## Q & A

**Q: IOS使用小火箭需要购买**

A: 可以使用 sing-box, sing-box 是一款在外区商店可以免费下载的代理软件

**Q: IOS我不知道应该如何获得外区账号**

A: 可以在B站搜索相关关键词, 这类视频还是挺多的

**Q: 我不知道应该如何配置代理**

A: 请按照文章步骤进行, 如果真的遇到某一步卡住, 可以加群与我们交流

**Q: 在按照步骤配置后, 我无法打开UsagiPass网页**

A: 首先, 能够打开此官网则证明您可以连接至UsagiPass的分发服务器. 无法打开可能是代理配置不正确, 或者是无法连接至我们的代理服务器.

请再次检查代理配置是否正确, 是否选择了UsagiPass作为配置, **是否在代理软件中开启规则模式**.

如果您的错误代码为类似ERR_PROXY_CONNECTION_FAILED的字样, 请加群联系我们, 我们会提供备用代理服务器, 尝试解决你的问题.
