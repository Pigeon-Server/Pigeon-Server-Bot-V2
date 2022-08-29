from mirai.bot import Mirai
from asyncio.tasks import sleep
from random import uniform
from mirai.models.message import Plain, MessageChain, At
from module.BasicModule.Logger import logger
from module.BasicModule.Config import config
from module.Interlining.UsefulTools import CheckSendType
from sys import exit

class Message:

    __bot = None
    PlayerName: str
    AdminName: str
    PlayerGroup: int
    AdminGroup: int

    def __init__(self, botObj: Mirai) -> None:
        """
        构造函数\n
        :param botObj: 传入bot实例
        """
        self.__bot = botObj
        self.PlayerGroup = config.Config["MiraiBotConfig"]["GroupConfig"]["AdminGroup"]
        self.AdminGroup = config.Config["MiraiBotConfig"]["GroupConfig"]["PlayerGroup"]

    async def init(self) -> None:
        """
        消息模块初始化\n
        """
        logger.debug("正在初始化消息模块")
        try:
            self.PlayerName = (await self.__bot.get_group(self.PlayerGroup)).name
            self.AdminName = (await self.__bot.get_group(self.AdminGroup)).name
            logger.success("初始化消息模块成功")
        except:
            logger.error("初始化消息模块失败")
            exit()

    async def SendMessage(self, targetGroup: str, message: str, AtTarget: int = None, targetMessage: int = None) -> None:
        """
        向任意群发送消息\n
        Args:
            targetGroup: 发送消息的目标群
            message: 要发送的消息
            AtTarget: @目标，可以为空
            targetMessage: 回复目标，可以为空
        """
        logger.info(f"[消息]->群:{(await self.__bot.get_group(targetGroup)).name}({targetGroup}):{message}")
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
        """
        向配置文件中定义的玩家群发送消息\n
        Args:
            message: 要发送的消息
            AtTarget: @目标，可以为空
            targetMessage: 回复目标，可以为空
        """
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
        """
        向配置文件中定义的管理群发送消息\n
        Args:
            message: 要发送的消息
            AtTarget: @目标，可以为空
            targetMessage: 回复目标，可以为空
        """
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
