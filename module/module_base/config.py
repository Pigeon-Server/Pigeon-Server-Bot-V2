# 模块-配置文件
from module.module_class.config_class import ConfigTools, ConfigInit, ServerConfigInit, ModuleConfigInit
from module.module_class.json_database_class import JsonDataBaseCLass
from typing import List
from module.module_base.logger import logger
from sys import exit
from os.path import exists
from os import mkdir
if not exists("config"):
    mkdir("config")
    logger.error("无法找到配置文件文件夹，已自动创建，请前往github获取config模板文件")
    exit()
config_tools = ConfigTools()
logger.debug("开始加载配置文件")
try:
    logger.debug("正在加载模块配置")
    module_config: ModuleConfigInit = config_tools.load_config("module.json5", ModuleConfigInit)
    logger.success("模块配置加载成功")
    if module_config.debug_mode:
        logger.debug("Debug模式已启用")
    logger.debug("正在加载主配置文件")
    main_config: ConfigInit = config_tools.load_config("config.json5", ConfigInit)
    logger.success("主配置文件加载完成")
    if module_config.questions:
        logger.debug("问答模块已启用，正在加载")
        faq_answer: dict = config_tools.load_config("FAQ.json5")
        logger.success("问答模块加载成功")
    if module_config.block_word:
        logger.debug("屏蔽词模块已启用，正在加载")
        blocking_word_list: List[str] = config_tools.load_config("word.json5")
        logger.success("屏蔽词模块加载成功")
    if module_config.image_review:
        if not exists("image"):
            mkdir("image")
        logger.debug("图片审核模块已启用，正在加载")
        image_list: JsonDataBaseCLass = JsonDataBaseCLass("image.json", 5)
        logger.success("图片审核模块加载成功")
    if module_config.shutup and module_config.questions:
        logger.debug("屏蔽模块已启用，正在加载")
        except_list: JsonDataBaseCLass = JsonDataBaseCLass("except.json", 4)
        logger.success("屏蔽模块加载成功")
    if module_config.black_list or module_config.white_list:
        logger.debug("服务器模块已启用，正在加载")
        server_config: ServerConfigInit = config_tools.load_config("server.json5", ServerConfigInit)
        logger.success("服务器模块加载成功")
    if module_config.check_mc_update:
        logger.debug("检查MC更新已启用，正在加载")
        version_check: JsonDataBaseCLass = JsonDataBaseCLass("version.json", 5)
        logger.success("检查更新模块启用成功")
except Exception as error:
    logger.error(error)
    logger.error("配置文件加载出错，正在退出")
    exit()
