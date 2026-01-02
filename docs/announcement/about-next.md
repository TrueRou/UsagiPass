# 新版 UsagiPass 说明

UsagiPass 指 基于水鱼/落雪查分器的数据动态生成玩家的 DXPASS 相关服务。

UsagiCard 指 样式类似 DXPASS 的实体卡片以及围绕卡片提供的相关服务。

服务条款：https://up.turou.fun/docs/terms-of-use.html

隐私政策：https://up.turou.fun/docs/privacy-policy.html

## 前言

首先感谢所有支持 UsagiPass 的用户，正是因为有你们的支持，我们才有动力继续开发和维护这个项目。为了不再强制依赖水鱼和落雪查分器，并且为未来更多功能的开发打下基础，我们决定对 UsagiPass 进行一次重大的升级。主要涉及重构账号系统和服务内容两大方面。本次升级于 2026 年 1 月 2 日正式完成，现将相关变更说明如下：

1. 合并 UsagiPass 与 UsagiCard 的账号系统（UsagiPass 不再强制依赖水鱼 / 落雪账号）
2. 合并 UsagiPass 与 UsagiCard 的图片系统（图片仅需上传一次，即可在两边使用）
3. 使用 Nuxt 重构 UsagiPass 和 UsagiCard（使用服务端渲染提升首屏加载速度）
4. 提升更新查分器的操作体验，点击小火箭即可在后台触发更新，不再在前台等待了
5. 优化图片查找和上传体验，现在可以根据标签进行上传和筛选了
6. 部分 UI 改进以及操作逻辑优化，添加了新手指引
7. 重新设计 DXPASS 部分样式，更符合自适应需求

## 目前的情况

1. UsagiPass 已经完成升级，上述变更均已实装。
2. UsagiCard 升级暂未完成，仍在进行中，目前 UsagiCard 仍然使用旧版系统，所有功能均未受影响。
3. UsagiCard 新用户注册和订单创建已暂时关闭，预计在 2026 年 2 月底前完成升级，升级完成后将重新开放订单创建。

额外说明：2025 年 12 月底，华立开始给二维码页面使用 HTTPS，所以 UsagiPass 必须安装 CA 证书才能继续使用，这与本次升级无关。

## 账号迁移说明

UsagiPass 与 兔卡账号 已完成深度融合升级，现统一更名为 UsagiLab 账号。关于账号升级的详细说明，请查看[账号迁移说明](./account-system.md)。

## 开发者相关

下面的内容仅面向对 UsagiPass / UsagiCard 感兴趣的开发者，介绍本次更新后 UsagiPass / UsagiCard 的整体架构设计和实现细节。

1. 原有的架构：

UsagiPass 与 UsagiCard 使用完全独立的账号系统、图片系统和查分系统。二者均为 Vue 3 + Vite 前端，后端使用 Python 开发。

2. 目前的情况：

UsagiPass 和 UsagiCard 使用 Nuxt + Nitro SSR 开发，Nitro 负责承载部分业务，以及转发 leporid 和 otoge-service 提供的 API 服务。

![](https://s2.loli.net/2026/01/02/mlyqvWZNP9tXMfz.png)

::: details UsagiPass 具体说明
- 图片和账号系统：调用 leporid 提供的图片和账号相关 API 服务。
- 查分相关功能：调用 otoge-service 提供的查分相关 API 服务。
- 个人偏好系统：Nitro 直接存取 usagipass 数据库中的用户偏好数据表。
:::

::: details UsagiCard 具体说明
- 图片和账号、订单等内部系统：调用 leporid 提供的图片和账号相关 API 服务。
- 查分、成绩等相关功能：调用 otoge-service 提供的查分相关 API 服务、部分逻辑由 Nitro 负责处理。
- 个人偏好系统：Nitro 直接存取 usagipass 数据库中的用户偏好数据表。
:::

在更新过后，您仍可以自行部署完整的 UsagiPass 服务。在默认情况下，虽然部署后将使用公共的 leporid 账号系统和图片系统，但您的个性化设置和 MITM 代理均运行在本地，仍可保证全链路安全。

在更新查分器时，默认会从本地数据库查出查分器账号信息，然后调用公共的 otoge-service 服务来上传成绩。如果您希望更进一步的安全，由于 maimai-prober 开源，您也可以自行搭建它。
