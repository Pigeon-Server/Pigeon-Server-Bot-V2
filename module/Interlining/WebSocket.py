from module.Class.SocketClass import SocketClass
from module.BasicModule.config import config
from asyncio.runners import run

if config.Config["WebsocketConfig"]["enable"]:
    websocket = SocketClass(config.Config["WebsocketConfig"]["host"], config.Config["WebsocketConfig"]["port"])
    run(websocket.Connect())
