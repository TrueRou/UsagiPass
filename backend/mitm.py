import datetime
import json
import mitmproxy.http

sysall_ip = "42.193.74.107"
target_url = "192.168.100.4"


def request(flow: mitmproxy.http.HTTPFlow):
    # refuse all requests that are not from sysall
    if flow.request.host != sysall_ip:
        flow.response = mitmproxy.http.Response.make(
            content=f'{{"error":"invalid request", "url": "{flow.request.url}", "msg": "The url is not allowed by UsagiPass mitmproxy, please check your proxy routes.", "msg_zh": "不允许的请求，请检查代理的路由配置"}}'
        )
        return

    # redirect qrcode requests to the local server
    if flow.request.path.find("qrcode") != -1 and flow.request.path.find("req") != -1:
        maid = flow.request.path_components[2].replace(".html", "")
        timestamp = int(flow.request.query.get("l"))

        flow.request.host = target_url
        flow.request.path = "/"
        flow.request.port = 4173
        flow.request.headers["Host"] = target_url
        flow.response.cookies["maimaiCode"] = maid
        flow.response.cookies["timeLimit"] = datetime.datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")

    # redirect other assets to the local server
    flow.request.host = target_url
