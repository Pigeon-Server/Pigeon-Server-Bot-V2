import collections
import json5
from pathlib import Path
from module.BasicModule.Logger import logger

class Config:
    __config = {
        "key": "ABCDEFG",
        "DataBase": {
            "host": "127.0.0.1",
            "username": "root",
            "password": "password",
            "database": "whitelist"
        },
        "channel": {
            "player": "123",
            "admin": "123"
        }
    }

    def CreateConfig(self, filename: str) -> None:

        """
        创建配置文件\n
        :param filename: 创建的配置文件名(str)
        :return: None
        """

        tempConfig = {}
        if filename == "config.json5":
            tempConfig = self.__config
        logger.debug("[Bot]正在尝试创建配置文件")
        try:
            with open(f"config/{filename}", "w", encoding="UTF-8") as write_file:
                json5.dump(tempConfig, write_file, indent="\t", sort_keys=False, ensure_ascii=False)
        except:
            logger.error("[Bot]配置文件创建失败")
        else:
            logger.debug("[Bot]配置文件创建成功")

    def loadConfig(self, filename: str) -> dict:

        """
        加载config\n
        :param filename: 要加载的配置文件名(str)
        :return: dict
        """

        if not Path("config/" + filename).is_file():
            self.CreateConfig(filename)
        else:
            try:
                return json5.load(open(f"config/{filename}", "r", encoding="UTF-8", errors="ignore"),
                                  object_hook=collections.OrderedDict)
            except:
                logger.error("[Bot]Json文件已损坏，正在尝试重新创建")
                self.CreateConfig(filename)

