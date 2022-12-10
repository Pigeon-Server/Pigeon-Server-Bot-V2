from module.BasicModule.Config import MainConfig, ModuleConfig
from module.BasicModule.Logger import logger
if MainConfig.ConfigVersion not in ["0.1.0"]:
    logger.error("配置文件版本与当前程序所支持的版本不匹配！请检查")
    exit()

from module.Object.Permission import *

if ModuleConfig.WhiteList or ModuleConfig.BlackList:
    from module.Object.Logic import *

# 是否查询MC更新
if ModuleConfig.CheckMCUpdate:
    from module.Object.Update import *

# 是否启用WebSocket上报（未完成）
if ModuleConfig.WebsocketReport:
    from module.Object.Websocket import *

# 是否启用图片审查（未完成）
if ModuleConfig.ImageReview:
    from module.Object.Image import *

# 是否启用问答模块
if ModuleConfig.Questions:
    from module.Object.Question import *

# 是否允许玩家自主设置屏蔽
if ModuleConfig.Shutup and ModuleConfig.Questions:
    from module.Object.Shutup import *

# 是否开启在线人数查询
if ModuleConfig.Online:
    from module.Object.Online import *

# 是否开启触发关键词撤回
if ModuleConfig.BlockWord:
    from module.Object.BlackWord import *

# 自动审核模块
if ModuleConfig.AutomaticReview:
    from module.Object.AutoReview import *

# MCSM模块
if ModuleConfig.MCSMModule:
    from module.Object.Mcsm import *

bot.run(port=MainConfig.MiraiBotConfig.WebSocketPort)
