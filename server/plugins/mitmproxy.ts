import { Proxy } from 'http-mitm-proxy'

const SYSALL_HOSTS = new Set([
    '42.193.74.107',
    '129.28.248.89',
    '43.137.91.207',
    '81.71.193.236',
    '43.145.45.124',
    'wq.sys-all.cn',
    'wq.sys-allnet.cn',
])

const WAHLAP_HOSTS = new Set([
    '152.136.21.46',
    'tgk-wcaime.wahlap.com',
])

const WEEKDAYS_JP = ['月', '火', '水', '木', '金', '土', '日']
const TOKYO_OFFSET_SECONDS = 9 * 60 * 60

function buildTokyoDate(timestamp: number) {
    const seconds = Number.isFinite(timestamp) ? timestamp : 0
    const adjusted = new Date((seconds + TOKYO_OFFSET_SECONDS) * 1000)

    const hours = String(adjusted.getUTCHours()).padStart(2, '0')
    const minutes = String(adjusted.getUTCMinutes()).padStart(2, '0')
    const secondsStr = String(adjusted.getUTCSeconds()).padStart(2, '0')
    const time = `${hours}:${minutes}:${secondsStr}`

    const year = adjusted.getUTCFullYear()
    const month = String(adjusted.getUTCMonth() + 1).padStart(2, '0')
    const day = String(adjusted.getUTCDate()).padStart(2, '0')
    const weekdayIndex = (adjusted.getUTCDay() + 6) % 7
    const weekday = WEEKDAYS_JP[weekdayIndex]
    const date = `${year}/${month}/${day}(${weekday})`

    return { time, date }
}

export default defineNitroPlugin((_nitroApp) => {
    const proxy = new Proxy()
    const config = useRuntimeConfig()

    proxy.onRequest((ctx, _callback) => {
        const host = ctx.clientToProxyRequest.headers.host
        const urlPart = ctx.clientToProxyRequest.url

        if (!host || !urlPart) {
            ctx.proxyToClientResponse.writeHead(400, {})
            ctx.proxyToClientResponse.end()
        }

        // redirect sysall qrcode requests to the UsagiPass frontend
        // example: http://wq.sys-all.cn/qrcode/req/MAID241020A01.html?l=1730217600&t=E8889E
        else if (SYSALL_HOSTS.has(host) && urlPart.startsWith('/qrcode/req')) {
            const maid = urlPart.substring(urlPart.indexOf('/qrcode/req/'), urlPart.indexOf('.html')).replace('/qrcode/req/', '')
            const timestamp = Number(new URL(urlPart, `http://${host}`).searchParams.get('l') ?? '0')
            const { time, date } = buildTokyoDate(timestamp)

            const redirectUrl = new URL(config.usagipass.baseURL || 'https://up.turou.fun')
            redirectUrl.searchParams.set('maid', maid)
            redirectUrl.searchParams.set('time', time)
            redirectUrl.searchParams.set('date', date)

            ctx.proxyToClientResponse.writeHead(302, { Location: redirectUrl.toString() })
            ctx.proxyToClientResponse.end()
        }

        // redirect wahlap oauth requests to the UsagiPass frontend
        // example: http://tgk-wcaime.wahlap.com/wc_auth/oauth/callback/maimai-dx?r=c9N1mMeLT&t=241114354&code=071EIC0003YUbTf5X31EIC0p&state=24F0976C60BD9796310AD933AFEF39FFCD7C0E64E9571E69A5AE5
        else if (WAHLAP_HOSTS.has(host) && urlPart.startsWith('/wc_auth/oauth/callback/maimai-dx')) {
            const urlParams = new URL(urlPart, `http://${host}`).searchParams

            const redirectBaseUrl = new URL(config.usagipass.baseURL || 'https://up.turou.fun')
            const redirectUrl = new URL('/wechat/callback', redirectBaseUrl)
            redirectUrl.searchParams.set('r', urlParams.get('r') || '')
            redirectUrl.searchParams.set('t', urlParams.get('t') || '')
            redirectUrl.searchParams.set('code', urlParams.get('code') || '')
            redirectUrl.searchParams.set('state', urlParams.get('state') || '')

            ctx.proxyToClientResponse.writeHead(302, { Location: redirectUrl.toString() })
            ctx.proxyToClientResponse.end()
        }

        // response wahlap mitm connection test
        // example: http://tgk-wcaime.wahlap.com/test
        else if (WAHLAP_HOSTS.has(host) && urlPart.startsWith('/test')) {
            const body = Buffer.from('{"source": "UsagiPass", "proxy":"ok"}')
            ctx.proxyToClientResponse.writeHead(200, {
                'Content-Type': 'application/json; charset=utf-8',
                'Access-Control-Allow-Origin': '*',
            })
            ctx.proxyToClientResponse.end(body)
        }

        // block all other requests
        else {
            ctx.proxyToClientResponse.writeHead(204)
            ctx.proxyToClientResponse.end()
        }
    })

    proxy.listen({ port: config.mitmproxy.listenPort, host: config.mitmproxy.listenHost })
})
