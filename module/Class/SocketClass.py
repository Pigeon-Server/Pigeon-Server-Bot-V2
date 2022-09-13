from module.Class.ExceptionClass import WebsocketUrlError
from websockets.legacy.client import connect
from module.BasicModule.Logger import logger
from sys import exit

class SocketClass:

    hostname: str
    __uuid: str
    clientInfo: dict
    connection = None

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
            self.connection = await connect(self.hostname)
            await self.connection.send(str({
                "type": "Client",
                "client": "QQ",
                "name": "QQBot",
                "load": "ClientHello"
            }))
            data = eval(await self.connection.recv())
            self.__uuid = data["uuid"]
            self.clientInfo = eval(data["clientInfo"])
            logger.success(f"成功连接到websocket服务器, 分配的uuid: {self.__uuid}")
        except ConnectionRefusedError as error:
            logger.error(error)
            logger.error("连接被服务器拒绝")
            exit()
        except ConnectionResetError as error:
            logger.error(error)
            logger.error("连接被重置")
            exit()
        except ConnectionError as error:
            logger.error(error)
            logger.error("无法连接到websocket服务器")
            exit()
        except Exception as error:
            logger.error(error)
            logger.error("发生未知错误")
            exit()

    async def SendMessage(self, data: str, broadcast: bool = False, target: str = "") -> str:
        await self.connection.send(str({
            "type": "Client",
            "client": "QQ",
            "name": "QQBot",
            "load": data,
            "broadcast": broadcast,
            "uuid": self.__uuid,
            "connection": 'keep-alive',
            "target": target
        }))
        return await self.connection.recv()

    async def DisConnection(self) -> None:
        await self.connection.close(code=1000, reason="插件关闭，关闭连接")
        await self.connection.wait_closed()
