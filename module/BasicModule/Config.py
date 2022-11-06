# 模块-配置文件
from module.Class.ConfigClass import ConfigTools, ConfigInit, ServerConfigInit, ModuleConfigInit
from module.Class.JsonDataBaseClass import JsonDataBaseCLass
from typing import List
from module.BasicModule.Logger import logger
from sys import exit
from os.path import exists
from os import mkdir
if not exists("config"):
    mkdir("config")
    logger.error("无法找到配置文件")
    exit()
configTools = ConfigTools()
logger.debug("开始加载配置文件")
try:
    logger.debug("正在加载模块配置")
    ModuleConfig: ModuleConfigInit = configTools.loadConfig("module.json5", ModuleConfigInit)
    logger.success("模块配置加载成功")
    if ModuleConfig.DebugMode:
        logger.debug("Debug模式已启用")
    logger.debug("正在加载主配置文件")
    MainConfig: ConfigInit = configTools.loadConfig("config.json5", ConfigInit)
    logger.success("主配置文件加载完成")
    if ModuleConfig.Questions:
        logger.debug("问答模块已启用，正在加载")
        FAQConfig: dict = configTools.loadConfig("FAQ.json5")
        logger.success("问答模块加载成功")
    if ModuleConfig.BlockWord:
        logger.debug("屏蔽词模块已启用，正在加载")
        BlockingWordList: List[str] = configTools.loadConfig("word.json5")
        logger.success("屏蔽词模块加载成功")
    if ModuleConfig.ImageReview:
        if not exists("image"):
            mkdir("image")
        logger.debug("图片审核模块已启用，正在加载")
        ImageList: JsonDataBaseCLass = JsonDataBaseCLass("image.json", 5)
        logger.success("图片审核模块加载成功")
    if ModuleConfig.Shutup and ModuleConfig.Questions:
        logger.debug("屏蔽模块已启用，正在加载")
        ExceptList: JsonDataBaseCLass = JsonDataBaseCLass("except.json", 4)
        logger.success("屏蔽模块加载成功")
    if ModuleConfig.BlackList or ModuleConfig.WhiteList:
        logger.debug("服务器模块已启用，正在加载")
        ServerConfig: dict = configTools.loadConfig("server.json5", ServerConfigInit)
        logger.success("服务器模块加载成功")
    if ModuleConfig.CheckMCUpdate:
        logger.debug("检查MC更新已启用，正在加载")
        VersionCheck: JsonDataBaseCLass = JsonDataBaseCLass("version.json", 5)
        logger.success("检查更新模块启用成功")
except Exception as error:
    logger.error(error)
    logger.error("配置文件加载出错，正在退出")
    exit()






