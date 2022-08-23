# 模块-配置文件
import os
from module.Class.ConfigClass import ConfigClass

# 判断config文件夹是否存在
config = os.path.join('config')
if not os.path.exists(config):
    os.makedirs(config)

config = ConfigClass()
