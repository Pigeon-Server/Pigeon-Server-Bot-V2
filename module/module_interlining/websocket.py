from module.module_class.websocket_class import SocketClass
from module.module_base.config import module_config, main_config

if module_config.websocket_report:  # 是否启用websocket上报
    # 创建websocket客户端实例
    websocket = SocketClass(main_config.websocket_config.host, main_config.websocket_config.port)
