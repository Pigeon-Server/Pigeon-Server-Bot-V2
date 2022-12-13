from module.module_base.config import main_config, module_config
from module.module_base.logger import logger

if main_config.config_version not in ["0.1.2"]:
    logger.error("配置文件版本与当前程序所支持的版本不匹配！请检查")
    exit()

if module_config.debug_mode:
    logger.warning("当前已开启Debug模式，可能会导致输出大量debug信息")

from module.module_object.base import *
from module.module_object.permission import *

if module_config.white_list or module_config.black_list:
    from module.module_object.logic import *

# 是否查询MC更新
if module_config.check_mc_update:
    from module.module_object.update import *

# 是否启用WebSocket上报（未完成）
if module_config.websocket_report:
    from module.module_object.websocket import *

# 是否启用图片审查（未完成）
if module_config.image_review:
    from module.module_object.image import *

# 是否启用问答模块
if module_config.questions:
    from module.module_object.question import *

# 是否允许玩家自主设置屏蔽
if module_config.shutup and module_config.questions:
    from module.module_object.shutup import *

# 是否开启在线人数查询
if module_config.online:
    from module.module_object.online import *

# 是否开启触发关键词撤回
if module_config.block_word:
    from module.module_object.black_word import *

# 自动审核模块
if module_config.automatic_review:
    from module.module_object.auto_review import *

# MCSM模块
if module_config.mcsm_module:
    from module.module_object.mcsm import *

bot.run(port=main_config.mirai_bot_config.websocket_port)
