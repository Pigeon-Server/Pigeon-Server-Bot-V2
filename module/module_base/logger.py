# 日志模块
from sys import stderr
from loguru import logger
from os.path import join, exists
from os import makedirs
from datetime import datetime
from json5 import load

# 检查是否存在logs文件夹
logs = join('logs')
if not exists(logs):
    makedirs(logs)
# 创建日志
if not load(open(f"config/module.json5", "r", encoding="UTF-8", errors="ignore"))["debug_mode"]:
    logger.remove()
    logger.add(stderr, level="INFO")
logger.add(f"./logs/output_{datetime.strftime(datetime.now(), '%Y-%m-%d')}.log",
           format="[{time:MM-DD HH:mm:ss}] - {level}: {message}", rotation="00:00")
