from module.Class.SocketClass import SocketClass
from module.BasicModule.Config import ModuleConfig, MainConfig

if ModuleConfig.KookInterflow:  # 是否启用websocket上报
    # 创建websocket客户端实例
    websocket = SocketClass(MainConfig.WebsocketConfig.host, MainConfig.WebsocketConfig.port)
