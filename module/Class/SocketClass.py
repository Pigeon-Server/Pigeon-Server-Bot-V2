from module.Class.ExceptionClass import WebsocketUrlError
from websockets.legacy.client import connect
from module.BasicModule.Logger import logger

class SocketClass:

    hostname: str

    def __init__(self, host: str, port: int):
        if host.startswith("ws://"):
            self.hostname = f"{host}:{port}"
        elif host.startswith("http://") or host.startswith("https://"):
            raise WebsocketUrlError("websocket网址必须以'ws://'开头")
        elif host.startswith("wss://"):
            raise WebsocketUrlError("暂时不支持wss")

    async def Connect(self):
        logger.debug("正在尝试连接到websocket服务器")
        try:
            connection = await connect(self.hostname)
            logger.success("成功连接到websocket服务器")
            await connection.close()
        except ConnectionRefusedError as error:
            logger.error(error)
            logger.error("连接被服务器拒绝")
        except ConnectionResetError as error:
            logger.error(error)
            logger.error("连接被重置")
        except ConnectionError as error:
            logger.error(error)
            logger.error("无法连接到websocket服务器")
        except Exception as error:
            logger.error(error)
            logger.error("发生未知错误")

