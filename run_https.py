from Config.Constants import CURRENT_DEVICE, ROOT_DIR

import uvicorn

if __name__ == "__main__":
    if CURRENT_DEVICE == 'pc':
        config = uvicorn.Config("main:app"
                                , port=443
                                , log_level="debug"
                                )
        server = uvicorn.Server(config)
        server.run()
    else:
        import os

        config = uvicorn.Config("main:app"
                                , reload=True
                                , host="0.0.0.0"
                                , port=443
                                , log_level="debug"
                                , ssl_keyfile='{}./ssl/private.key'.format(ROOT_DIR)
                                , ssl_certfile='{}./ssl/certificate.crt'.format(ROOT_DIR)
                                )
        server = uvicorn.Server(config)
        server.run()
