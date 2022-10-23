from sys import exit
from mirai.bot import Mirai
from mirai.adapters.websocket import WebSocketAdapter
from mirai_extensions.trigger import HandlerControl, InterruptControl
from mirai.adapters.http import HTTPAdapter
from module.BasicModule.Config import MainConfig
from module.BasicModule.Logger import logger
from module.Class.Message import Message
from module.Class.ExceptionClass import ConnectionTypeError

adapter: HTTPAdapter | WebSocketAdapter | None = None  # 定义适配器
match MainConfig.MiraiBotConfig.ConnectType:
    case "Http":
        adapter = HTTPAdapter(verify_key=MainConfig.MiraiBotConfig.MiraiHTTP.Key,
                              host=MainConfig.MiraiBotConfig.MiraiHTTP.Host,
                              port=MainConfig.MiraiBotConfig.MiraiHTTP.Port,
                              single_mode=MainConfig.MiraiBotConfig.MiraiHTTP.SingleMode)
    case "WebSocket":
        adapter = WebSocketAdapter(verify_key=MainConfig.MiraiBotConfig.MiraiHTTP.Key,
                                   host=MainConfig.MiraiBotConfig.MiraiHTTP.Host,
                                   port=MainConfig.MiraiBotConfig.MiraiHTTP.Port,
                                   single_mode=MainConfig.MiraiBotConfig.MiraiHTTP.SingleMode,
                                   sync_id=MainConfig.MiraiBotConfig.MiraiHTTP.SyncId)
if adapter is None:
    logger.error("连接方式选择错误！可选的方式为\"Http\"或者\"WebSocket\"")
    raise ConnectionTypeError()  # 报错并退出程序
else:
    try:
        bot = Mirai(qq=MainConfig.MiraiBotConfig.QQ, adapter=adapter)  # 创建bot实例
        control = HandlerControl(bot)  # 创建事件控制器
        message = Message(bot)  # 创建消息处理模块
        interrupt = InterruptControl(bot)  # 创建中断控制器
    except ConnectionError:
        logger.error("无法连接到Mirai-Http-Api!请检查设置是否正确！")
        exit()
    except:
        logger.error("发生未知错误！")
        exit()
