---
outline: deep
---

# 实现方式

## 华立的设计

当点击公众号的玩家二维码后，**公众号后台**将玩家ID和过期时间以一定形式编码成SGWCMAID

公众号返回一个sys-all.cn的网页，查询参数中包含SGWCMAID

网页根据SGWCMAID, 显示对应的二维码图片和简陋的扫码界面

舞萌DX识别二维码, 解析出SGWCMAID, SGWCMAID配合机台信息和密钥, 向后端请求得到玩家ID

::: tip
因为SGWCMAID在微信公众号后台生成, 对于我们来说属于黑箱, 且无法从玩家ID逆向得到SGWCMAID. 故印制实体卡片, 或者利用单片机实现算号登录的操作在当前情况下是没有可行性的.
:::

## 我们的设计

通过代理替换sys-all.cn网页, 将请求重定向到dxpass.turou.fun

重定向时携带原网页中的查询参数(SGWCMAID), **在前端**以JS的方式直接绘制出二维码

::: tip
SGWCMAID不经过我们的后端, 更加安全可靠

UsagiPass前后端代码在Github开源: [https://github.com/TrueRou/UsagiPass](https://github.com/TrueRou/UsagiPass)
:::