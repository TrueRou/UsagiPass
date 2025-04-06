import os
from dotenv import load_dotenv

load_dotenv()

# uvicorn settings
app_host = os.environ.get("APP_HOST", "127.0.0.1")
app_port = int(os.environ.get("APP_PORT", 8000))
app_root = os.environ.get("APP_ROOT", "")
app_root = "" if app_root == "/" else app_root
app_url = os.environ.get("APP_URL", "https://up.turou.fun/")

# mitmproxy settings
mitm_host = os.environ.get("MITM_HOST", "0.0.0.0")
mitm_port = int(os.environ.get("MITM_PORT", 2560))

# database settings
mysql_url = os.environ["MYSQL_URL"]
jwt_secret = os.environ.get("JWT_SECRET") or "change_me_in_production_enviroment"
httpx_proxy = os.environ.get("HTTPX_PROXY", None) or None
arcade_proxy = os.environ.get("ARCADE_PROXY", None) or None

# provider settings
lxns_developer_token = os.environ.get("LXNS_DEVELOPER_TOKEN", None) or None
divingfish_developer_token = os.environ.get("DIVINGFISH_DEVELOPER_TOKEN", None) or None

default_character = os.environ.get("DEFAULT_CHARACTER", "default")
default_background = os.environ.get("DEFAULT_BACKGROUND", "default")
default_frame = os.environ.get("DEFAULT_FRAME", "default")
default_passname = os.environ.get("DEFAULT_PASSNAME", "default")

# refresh settings
refresh_hour_threshold = int(os.environ.get("REFRESH_HOUR_THRESHOLD", 24))
refresh_hour_active = os.environ.get("REFRESH_HOUR_ACTIVE", "10-17")
refresh_hour_inactive = os.environ.get("REFRESH_HOUR_INACTIVE", "0-9,18-23")
