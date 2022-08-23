# 模块-配置文件
from module.BasicModule.Logger import logger
from module.Class.ConfigClass import Config
import os
# 判断config文件夹是否存在
config = os.path.join('config')
if not os.path.exists(config):
    os.makedirs(config)
configClass = Config()
logger.debug("正在加载配置文件")
config = configClass.loadConfig("config.json5")
logger.debug("配置文件加载完成")
