from module.module_class.exception_class import WebsocketUrlError
from websockets.legacy.client import connect
from module.module_base.logger import logger
from sys import exit


class SocketClass:
    _hostname: str
    _uuid: str
    client_info: dict
    connection = None

    def __init__(self, host: str, port: int):
        if host.startswith("ws://"):
            self._hostname = f"{host}:{port}"
        elif host.startswith("http://") or host.startswith("https://"):
            raise WebsocketUrlError("websocket链接必须以'ws://'开头")
        elif host.startswith("wss://"):
            raise WebsocketUrlError("暂时不支持wss")

    async def connect(self):
        logger.debug("正在尝试连接到websocket服务器")
        try:
            self.connection = await connect(self._hostname)
            await self.connection.send(str({
                "type": "Client",
                "client": "QQ",
                "name": "QQBot",
                "load": "ClientHello"
            }))
            data = eval(await self.connection.recv())
            self._uuid = data["uuid"]
            self.client_info = eval(data["clientInfo"])
            logger.success(f"成功连接到websocket服务器, 分配的uuid: {self._uuid}")
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

    async def send_message(self, data: str, broadcast: bool = False, target: str = "") -> str:
        await self.connection.send(str({
            "type": "Client",
            "client": "QQ",
            "name": "QQBot",
            "load": data,
            "broadcast": broadcast,
            "uuid": self._uuid,
            "connection": 'keep-alive',
            "target": target
        }))
        return await self.connection.recv()

    async def disconnection(self) -> None:
        await self.connection.close(code=1000, reason="插件关闭，关闭连接")
        await self.connection.wait_closed()
