from datetime import datetime

from mitmproxy.http import HTTPFlow, Response

from usagipass.app import settings


class WechatWahlapAddon:
    sysall_hosts = [
        "42.193.74.107",
        "129.28.248.89",
        "43.137.91.207",
        "81.71.193.236",
        "43.145.45.124",
        "wq.sys-all.cn",
        "wq.sys-allnet.cn",
    ]

    wahlap_hosts = [
        "152.136.21.46",
        "tgk-wcaime.wahlap.com",
    ]

    async def request(self, flow: HTTPFlow):
        # redirect sysall qrcode requests to the usagi pass frontend
        # example: http://wq.sys-all.cn/qrcode/req/MAID241020A01.html?l=1730217600&t=E8889E
        if flow.request.host in self.sysall_hosts and flow.request.path.find("qrcode") != -1 and flow.request.path.find("req") != -1:
            maid = flow.request.path_components[2].replace(".html", "")
            timestamp = int(flow.request.query.get("l") or 0)
            # 日本星期映射
            weekdays_jp = ["月", "火", "水", "木", "金", "土", "日"]
            weekday_jp = weekdays_jp[datetime.fromtimestamp(timestamp).weekday()]
            #
            timestr = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
            datestr = datetime.fromtimestamp(timestamp).strftime(f"%Y/%m/%d({weekday_jp})")
            location = settings.app_url + f"?maid={maid}&time={timestr}&date={datestr}"
            flow.response = Response.make(302, headers={"Location": location})

        # response wahlap mitm connection test
        # example: http://tgk-wcaime.wahlap.com/test
        elif flow.request.host in self.wahlap_hosts and flow.request.path == "/test":
            flow.response = Response.make(200, content=b'{"source": "UsagiPass", "proxy":"ok"}')
            flow.response.headers["Access-Control-Allow-Origin"] = "*"

        # redirect wahlap oauth requests to the usagi pass frontend
        # example: http://tgk-wcaime.wahlap.com/wc_auth/oauth/callback/maimai-dx?r=c9N1mMeLT&t=241114354&code=071EIC0003YUbTf5X31EIC0p&state=24F0976C60BD9796310AD933AFEF39FFCD7C0E64E9571E69A5AE5
        elif flow.request.host in self.wahlap_hosts and flow.request.path.startswith("/wc_auth/oauth/callback/maimai-dx"):
            location = settings.app_url + "update" + flow.request.path.removeprefix("/wc_auth/oauth/callback/maimai-dx")
            flow.response = Response.make(302, headers={"Location": location})

        # block all other requests
        else:
            flow.response = Response.make(204)
