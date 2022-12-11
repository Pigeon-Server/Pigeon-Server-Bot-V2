from sys import exit
from mirai.bot import Mirai
from mirai.adapters.websocket import WebSocketAdapter
from mirai_extensions.trigger import HandlerControl, InterruptControl
from mirai.adapters.http import HTTPAdapter
from module.module_base.config import main_config
from module.module_base.logger import logger
from module.module_class.message_class import Message
from module.module_class.exception_class import ConnectionTypeError

adapter: HTTPAdapter | WebSocketAdapter | None = None  # 定义适配器
match main_config.mirai_bot_config.connect_type:
    case "Http":
        adapter = HTTPAdapter(verify_key=main_config.mirai_bot_config.mirai_http.key,
                              host=main_config.mirai_bot_config.mirai_http.host,
                              port=main_config.mirai_bot_config.mirai_http.port,
                              single_mode=main_config.mirai_bot_config.mirai_http.single_mode)
    case "WebSocket":
        adapter = WebSocketAdapter(verify_key=main_config.mirai_bot_config.mirai_http.key,
                                   host=main_config.mirai_bot_config.mirai_http.host,
                                   port=main_config.mirai_bot_config.mirai_http.port,
                                   single_mode=main_config.mirai_bot_config.mirai_http.single_mode,
                                   sync_id=main_config.mirai_bot_config.mirai_http.sync_id)
if adapter is None:
    logger.error("连接方式选择错误！可选的方式为\"Http\"或者\"WebSocket\"")
    raise ConnectionTypeError()  # 报错并退出程序
else:
    try:
        bot = Mirai(qq=main_config.mirai_bot_config.qq, adapter=adapter)  # 创建bot实例
        control = HandlerControl(bot)  # 创建事件控制器
        message = Message(bot)  # 创建消息处理模块
        interrupt = InterruptControl(bot)  # 创建中断控制器
    except ConnectionError:
        logger.error("无法连接到Mirai-Http-Api!请检查设置是否正确！")
        exit()
    except:
        logger.error("发生未知错误！")
        exit()
