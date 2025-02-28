import asyncio
import logging
import uvicorn

from usagipass.app import settings
from usagipass.app.logging import Ansi, log
from usagipass.app.entrypoint import MitmMaster, asgi_app


def main():
    log(f"Uvicorn running on http://{settings.app_host}:{str(settings.app_port)} (Press CTRL+C to quit)", Ansi.YELLOW)
    uvicorn.run(asgi_app, log_level=logging.WARNING, port=settings.app_port, host=settings.app_host, root_path=settings.app_root)


def mitm_main():
    async def run_proxy_async():
        master = MitmMaster()
        await master.run()

    log(f"Mitmproxy running on http://{settings.mitm_host}:{str(settings.mitm_port)} (Press CTRL+C to quit)", Ansi.LCYAN)
    asyncio.run(run_proxy_async())


if __name__ == "__main__":
    main()
