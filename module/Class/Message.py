from mirai.bot import Mirai
from asyncio.tasks import sleep
from random import uniform
from mirai.models.message import Plain, MessageChain, At
from module.BasicModule.logger import logger
from module.BasicModule.config import config
from module.Interlining.UsefulTools import CheckSendType
from sys import exit

class Message:

    __bot = None
    PlayerName: str
    AdminName: str
    PlayerGroup: int = config.Config["MiraiBotConfig"]["GroupConfig"]["PlayerGroup"]
    AdminGroup: int = config.Config["MiraiBotConfig"]["GroupConfig"]["AdminGroup"]

    def __init__(self, botObj: Mirai) -> None:
        self.__bot = botObj

    async def init(self) -> None:
        logger.debug("正在初始化消息模块")
        try:
            self.PlayerName = (await self.__bot.get_group(self.PlayerGroup)).name
            self.AdminName = (await self.__bot.get_group(self.AdminGroup)).name
            logger.success("初始化消息模块成功")
        except:
            logger.error("初始化消息模块失败")
            exit()

    async def SendMessage(self, groupName: str, targetGroup: str, message: str, AtTarget: int = None, targetMessage: int = None) -> None:
        logger.info(f"[消息]->群:{groupName}({targetGroup}):{message}")
        await sleep(uniform(1.0, 0.3))
        match CheckSendType(AtTarget, targetMessage):
            case 0:
                try:
                    await self.__bot.send_group_message(targetGroup, MessageChain([
                        Plain(message)
                    ]))
                except:
                    logger.error("发送消息出现未知错误！")
            case 1:
                try:
                    await self.__bot.send_group_message(targetGroup, MessageChain([
                        Plain(message)
                    ]), targetMessage)
                except:
                    logger.error("发送消息出现未知错误！")
            case 2:
                try:
                    await self.__bot.send_group_message(targetGroup, MessageChain([
                        At(AtTarget), Plain(message)
                    ]))
                except:
                    logger.error("发送消息出现未知错误！")
            case 3:
                try:
                    await self.__bot.send_group_message(targetGroup, MessageChain([
                        At(AtTarget), Plain(message)
                    ]), targetMessage)
                except:
                    logger.error("发送消息出现未知错误！")

    async def PlayerMessage(self, message: str, AtTarget: int = None, targetMessage: int = None) -> None:
        logger.info(f"[消息]->群:{self.PlayerName}({self.PlayerGroup}):{message}")
        await sleep(uniform(1.0, 0.3))
        match CheckSendType(AtTarget, targetMessage):
            case 0:
                try:
                    await self.__bot.send_group_message(self.PlayerGroup, MessageChain([
                        Plain(message)
                    ]))
                except:
                    logger.error("发送消息出现未知错误！")
            case 1:
                try:
                    await self.__bot.send_group_message(self.PlayerGroup, MessageChain([
                        Plain(message)
                    ]), targetMessage)
                except:
                    logger.error("发送消息出现未知错误！")
            case 2:
                try:
                    await self.__bot.send_group_message(self.PlayerGroup, MessageChain([
                        At(AtTarget), Plain(message)
                    ]))
                except:
                    logger.error("发送消息出现未知错误！")
            case 3:
                try:
                    await self.__bot.send_group_message(self.PlayerGroup, MessageChain([
                        At(AtTarget), Plain(message)
                    ]), targetMessage)
                except:
                    logger.error("发送消息出现未知错误！")

    async def AdminMessage(self, message: str, AtTarget: int = None, targetMessage: int = None) -> None:
        logger.info(f"[消息]->群:{self.AdminName}({self.AdminGroup}):{message}")
        await sleep(uniform(1.0, 0.3))
        match CheckSendType(AtTarget, targetMessage):
            case 0:
                try:
                    await self.__bot.send_group_message(self.AdminGroup, MessageChain([
                        Plain(message)
                    ]))
                except:
                    logger.error("发送消息出现未知错误！")
            case 1:
                try:
                    await self.__bot.send_group_message(self.AdminGroup, MessageChain([
                        Plain(message)
                    ]), targetMessage)
                except:
                    logger.error("发送消息出现未知错误！")
            case 2:
                try:
                    await self.__bot.send_group_message(self.AdminGroup, MessageChain([
                        At(AtTarget), Plain(message)
                    ]))
                except:
                    logger.error("发送消息出现未知错误！")
            case 3:
                try:
                    await self.__bot.send_group_message(self.AdminGroup, MessageChain([
                        At(AtTarget), Plain(message)
                    ]), targetMessage)
                except:
                    logger.error("发送消息出现未知错误！")
