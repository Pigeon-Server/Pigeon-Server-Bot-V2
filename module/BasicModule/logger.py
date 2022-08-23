# 日志模块
from loguru import logger
import os
import datetime
# 检查是否存在logs文件夹
logs = os.path.join('logs')
if not os.path.exists(logs):
    os.makedirs(logs)
# 创建日志
log = logger.add(f"./logs/output_{datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')}.log",
                 format="[{time:MM-DD HH:mm:ss}] - {level}: {message}", rotation="00:00")
