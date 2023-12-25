from Core.Constants import CURRENT_DEVICE
from hypercorn.config import Config
from hypercorn.asyncio import serve
from main import app

import asyncio

if __name__ == "__main__":
    config = Config()
    config.loglevel = "debug"
    config.use_reloader = True
    # config.alpn_protocols = ["h2"]

    if CURRENT_DEVICE == 'pc':
        config.bind = ["localhost:8099"]
    else:
        config.bind = ["0.0.0.0:8099"]
    asyncio.run(serve(app, config))