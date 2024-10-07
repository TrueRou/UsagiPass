import logging

import uvicorn

from app.logging import Ansi, log
from app.entrypoint import asgi_app
import config


if __name__ == "__main__":
    log(f"Uvicorn running on http://{config.bind_address}:{str(config.bind_port)} (Press CTRL+C to quit)", Ansi.YELLOW)
    uvicorn.run(asgi_app, log_level=logging.WARNING, port=config.bind_port, host=config.bind_address)
