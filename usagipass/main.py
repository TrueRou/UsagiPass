import logging
import uvicorn

from usagipass.app import settings
from usagipass.app.logging import Ansi, log
from usagipass.app.entrypoint import asgi_app


def main():
    log(f"Uvicorn running on http://{settings.app_host}:{str(settings.app_port)} (Press CTRL+C to quit)", Ansi.YELLOW)
    uvicorn.run(asgi_app, log_level=logging.WARNING, port=settings.app_port, host=settings.app_host, root_path=settings.app_root)


if __name__ == "__main__":
    main()
