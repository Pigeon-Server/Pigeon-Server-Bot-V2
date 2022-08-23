from module.Class.SocketClass import SocketClass
from module.BasicModule.Config import config
from asyncio.runners import run

if config["WebsocketConfig"]["enable"]:
    ws = SocketClass(config["WebsocketConfig"]["host"], config["WebsocketConfig"]["port"])
    run(ws.Connect())


