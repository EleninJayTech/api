from Core.Constants import CURRENT_DEVICE

import uvicorn

if __name__ == "__main__":
    if CURRENT_DEVICE == 'pc':
        config = uvicorn.Config("main:app"
                                , port=8099
                                , log_level="debug"
                                )
    else:
        config = uvicorn.Config("main:app"
                                , reload=True
                                , host="0.0.0.0"
                                , port=8099
                                , log_level="debug"
                                )
    server = uvicorn.Server(config)
    server.run()