from sys import exit
from mirai.bot import Mirai
from mirai.adapters.websocket import WebSocketAdapter
from mirai_extensions.trigger import HandlerControl
from mirai.adapters.http import HTTPAdapter
from module.BasicModule.config import config
from module.BasicModule.logger import logger
from module.Class.Message import Message

adapter = None
match config.Config["MiraiBotConfig"]["ConnectType"]:
    case "Http":
        adapter = HTTPAdapter(verify_key=config.Config["MiraiBotConfig"]["MiraiHTTP"]["Key"],
                                host=config.Config["MiraiBotConfig"]["MiraiHTTP"]["Host"],
                                port=config.Config["MiraiBotConfig"]["MiraiHTTP"]["Port"],
                                single_mode=config.Config["MiraiBotConfig"]["MiraiHTTP"]["SingleMode"])
    case "WebSocket":
        adapter = WebSocketAdapter(verify_key=config.Config["MiraiBotConfig"]["MiraiHTTP"]["Key"],
                                    host=config.Config["MiraiBotConfig"]["MiraiHTTP"]["Host"],
                                    port=config.Config["MiraiBotConfig"]["MiraiHTTP"]["Port"],
                                    single_mode=config.Config["MiraiBotConfig"]["MiraiHTTP"]["SingleMode"],
                                    sync_id=config.Config["MiraiBotConfig"]["MiraiHTTP"]["SyncId"])
if adapter is None:
    logger.error("连接方式选择错误！可选的方式为\"Http\"或者\"WebSocket\"")
    exit()
else:
    try:
        bot = Mirai(qq=config.Config["MiraiBotConfig"]["QQ"], adapter=adapter)
        control = HandlerControl(bot)
        message = Message(bot)
    except ConnectionError:
        logger.error("无法连接到Mirai-Http-Api!请检查设置是否正确！")
        exit()
    except:
        logger.error("发生未知错误！")
        exit()
