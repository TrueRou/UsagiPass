import os
from dotenv import load_dotenv

load_dotenv()

# uvicorn settings
app_host = os.environ.get("APP_HOST", "127.0.0.1")
app_port = os.environ.get("APP_PORT", 8000)
app_root = os.environ.get("APP_ROOT", "")
app_root = "" if app_root == "/" else app_root

# maiweb settings
mysql_url = os.environ["MYSQL_URL"]
jwt_secret = os.environ.get("JWT_SECRET") or "change_me_in_production_enviroment"
httpx_proxy = os.environ.get("HTTPX_PROXY", None) or None
arcade_proxy = os.environ.get("ARCADE_PROXY", None) or None

# provider settings
lxns_developer_token = os.environ.get("LXNS_DEVELOPER_TOKEN", None)
divingfish_developer_token = os.environ.get("DIVINGFISH_DEVELOPER_TOKEN", None)

default_character = os.environ.get("DEFAULT_CHARACTER", "default")
default_background = os.environ.get("DEFAULT_BACKGROUND", "default")
default_frame = os.environ.get("DEFAULT_FRAME", "default")
default_passname = os.environ.get("DEFAULT_PASSNAME", "default")

# server settings
maimai_version = os.environ.get("MAIMAI_VERSION", "[maimaiDX]1.45-0001")
server_motd = os.environ.get("SERVER_MOTD", "Welcome to UsagiPass API server!")
author_motd = os.environ.get("AUTHOR_MOTD", "Authored by TuRou")
