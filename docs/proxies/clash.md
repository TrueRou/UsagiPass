---
outline: deep
---

# <i-arcticons-clash />Clash / <i-arcticons-clash-meta />Mihomo 配置

::: tip 提示
<i-arcticons-clash />Clash 和 <i-arcticons-clash-meta />Mihomo 都支持 UsagiPass, <br>
若已装过系列软件的, 直接查看第2步
:::

1. 安装 <i-arcticons-clash />Clash / <i-arcticons-clash-meta />Mihomo（原 ClashMeta）：
    - **ClashMetaForAndroid**: [Github (推荐) ](https://github.com/MetaCubeX/ClashMetaForAndroid/releases) / [蓝奏云 (国内) ](https://wwps.lanzouj.com/iXMCk2cydjmd)
    - [**其他客户端** (MetaCubeX Wiki)](https://wiki.metacubex.one/startup/client/client/)
    - 加入 UsagiPass 用户群，在群公告处获取：363346002
2. 导入 UsagiPass 配置
    - [一键导入 <i-arcticons-clash /> / <i-arcticons-clash-meta /> 配置](clash://install-config?url=https%3a%2f%2fdxpass.turou.fun%2fUsagiPass.yaml&name=UsagiPass)
    - 复制链接到  <i-arcticons-clash /> / <i-arcticons-clash-meta /> 导入：https://dxpass.turou.fun/UsagiPass.yaml
    - 加入 UsagiPass 用户群，在群文件获取配置：363346002
3. **确保选择了 UsagiPass 配置，点击启动代理即可生效！**

<br>

::: details 高级方法: 插入在自己的  <i-arcticons-clash />Clash / <i-arcticons-clash-meta />Mihomo 配置文件

> [!TIP] 提示
> 本方法需熟知内核的 [`proxy-providers`](https://wiki.metacubex.one/config/proxy-providers) 与 [`rule-providers`](https://wiki.metacubex.one/config/rule-providers) 方法<br>
  以下内容仅供参考, 

<br>

```yaml
proxy-providers:
  UsagiPass:
    type: http
    url: "https://dxpass.turou.fun/UsagiPass.yaml"
    interval: 3600
    health-check:
      enable: true
      url: https://www.gstatic.com/generate_204
      interval: 300
      timeout: 5000
      lazy: true
      expected-status: 204

proxy-group:
- { "name": "舞萌DX登录", "type": "select", "proxies": [ "DIRECT" ], "use": [ "UsagiPass" ] }
  
rule-providers:
  maimaiDX_domain: { "type": "http", "behavior": "domain", "interval": 600, "format": "yaml", "url": "https://up.turou.fun/UsagiPass.yaml", }

rule:
  - 'RULE-SET,maimaiDX_domain,舞萌DX登录'
```
:::
