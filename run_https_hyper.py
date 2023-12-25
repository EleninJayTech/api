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
        config.bind = ["localhost:443"]
    else:
        import os
        current_dir = os.path.dirname(os.path.realpath(__file__))
        config.bind = ["0.0.0.0:443"]
        config.keyfile = '{}/ssl/private.key'.format(current_dir)
        config.certfile = '{}/ssl/certificate.crt'.format(current_dir)
    asyncio.run(serve(app, config))