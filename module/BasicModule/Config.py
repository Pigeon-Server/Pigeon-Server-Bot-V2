# 模块-配置文件
from os.path import join, exists
from os import makedirs
from module.Class.ConfigClass import ConfigClass

# 判断config文件夹是否存在
config = join('config')
if not exists(config):
    makedirs(config)

config = ConfigClass()
