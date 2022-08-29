from module.Class.SocketClass import SocketClass
from module.BasicModule.Config import config
from asyncio.runners import run

if config.module["KookInterflow"]:  # 是否启用websocket上报
    # 创建websocket客户端实例
    websocket = SocketClass(config.Config["WebsocketConfig"]["host"], config.Config["WebsocketConfig"]["port"])
    # 测试连接
    run(websocket.Connect())
