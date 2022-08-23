from base64 import b64encode
from json5.lib import load, dumps
from pathlib import Path
from asyncio.runners import run
from module.BasicModule.logger import logger
from sys import exit


class ConfigClass:

    Config: dict
    FAQ: dict
    image: dict
    server: dict
    word: dict
    exception: list

    def __init__(self):
        logger.debug("正在加载主配置文件")
        try:
            self.Config = self.loadConfig("config.json5")
            logger.success("主配置文件加载完成")
        except:
            logger.error("主配置文件加载失败")
            exit()
        logger.debug("正在加载问答模块")
        try:
            self.FAQ = self.loadConfig("FAQ.json5")
            logger.success("问答模块加载完成")
        except:
            logger.error("加载问答模块失败")
            exit()
        logger.debug("正在加载服务器配置")
        try:
            self.server = self.loadConfig("server.json5")
            logger.success("服务器配置加载完成")
        except:
            logger.error("加载服务器配置失败")
            exit()
        logger.debug("正在加载违禁词和排除名单")
        try:
            self.word = self.loadConfig("word.json5")
            logger.success("违禁词和排除名单加载完成")
        except:
            logger.error("违禁词和排除名单加载失败")
            exit()
        logger.debug("正在加载屏蔽名单")
        try:
            self.exception = self.loadConfig("except.json5")
            logger.success("屏蔽名单加载完成")
        except:
            logger.error("屏蔽名单加载失败")
            exit()
        logger.debug("正在加载图片文件")
        try:
            self.image = run(self.loadImage())
            logger.success("图片加载完成")
        except:
            logger.error("图片加载失败")
            exit()
        logger.success("所有配置文件加载完毕")

    async def reloadConfig(self) -> dict:
        try:
            logger.debug("正在重载问答配置文件")
            self.FAQ = self.loadConfig("FAQ.json5")
            logger.success("问答配置文件重载完成")
            logger.debug("正在重载违禁词和排除名单")
            self.word = self.loadConfig("word.json5")
            logger.success("违禁词和排除名单重载完成")
            logger.debug("正在重载图片文件")
            self.image = await self.loadImage()
            logger.success("图片重载完成")
            return True
        except:
            logger.error("重载配置文件发生错误")
            return False

    async def loadImage(self) -> dict:
        pathConfig = self.loadConfig("image.json5")
        tempDict = {}
        for raw in pathConfig:
            with open(pathConfig[raw], 'rb') as i:
                tempDict.update({raw: str(b64encode(i.read()), 'utf-8')})
        return tempDict

    async def WriteException(self, id: int) -> bool:
        if id in self.exception:
            self.exception.remove(id)
            with open("config/except.json5", 'w', encoding="UTF-8") as f:
                f.write(dumps(self.exception, indent=4, ensure_ascii=False))
            return False
        else:
            self.exception.append(id)
            with open("config/except.json5", 'w', encoding="UTF-8") as f:
                f.write(dumps(self.exception, indent=4, ensure_ascii=False))
            return True

    @staticmethod
    def loadConfig(filename: str) -> dict:

        """
        加载config\n
        :param filename: 要加载的配置文件名(str)
        :return: dict
        """

        if not Path("config/" + filename).is_file():
            logger.error(f"{filename}配置文件不存在")
        else:
            try:
                return load(open(f"config/{filename}", "r", encoding="UTF-8", errors="ignore"))
            except:
                logger.error(f"{filename}已损坏，正在尝试重新创建")
