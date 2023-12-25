from Core.Constants import CURRENT_DEVICE

import uvicorn

if __name__ == "__main__":
    if CURRENT_DEVICE == 'pc':
        config = uvicorn.Config("main:app"
                                , port=443
                                , log_level="debug"
                                )
    else:
        import os
        current_dir = os.path.dirname(os.path.realpath(__file__))
        config = uvicorn.Config("main:app"
                                , reload=True
                                , host="0.0.0.0"
                                , port=443
                                , log_level="debug"
                                , ssl_keyfile='{}/ssl/private.key'.format(current_dir)
                                , ssl_certfile='{}/ssl/certificate.crt'.format(current_dir)
                                )
    server = uvicorn.Server(config)
    server.run()