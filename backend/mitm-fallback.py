import datetime
import mitmproxy.http

allowed_hosts = ["42.193.74.107", "129.28.248.89", "wq.sys-all.cn"]
target_url = "http://38.55.96.170/"  # we don't use https here.


def request(flow: mitmproxy.http.HTTPFlow):
    # refuse all requests that are not from sysall
    if flow.request.host not in allowed_hosts:
        flow.response = mitmproxy.http.Response.make(
            content=f'{{"error":"invalid request", "host": "{flow.request.host}", "msg": "The host is not allowed by UsagiPass mitmproxy, please check your proxy routes.", "msg_zh": "不允许的请求，请检查代理的路由配置"}}'
        )
        return

    # redirect qrcode requests to the local server
    if flow.request.path.find("qrcode") != -1 and flow.request.path.find("req") != -1:
        maid = flow.request.path_components[2].replace(".html", "")
        timestamp = int(flow.request.query.get("l"))
        timestr = datetime.datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")

        location = target_url + f"?maid={maid}&time={timestr}"
        flow.response = mitmproxy.http.Response.make(302, headers={"Location": location})
