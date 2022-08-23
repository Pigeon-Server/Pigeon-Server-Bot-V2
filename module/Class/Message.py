from mirai.bot import Mirai
from asyncio.tasks import sleep
from random import uniform
from mirai.models.message import Plain, MessageChain
from module.BasicModule.logger import logger

class Message:

    __bot = None

    def __init__(self, botObj: Mirai) -> None:
        self.__bot = botObj

    async def SendMessage(self, groupName: str, targetGroup: str, message: str) -> bool:
        logger.info(f"[消息]->群:{groupName}({targetGroup}):{message}")
        await sleep(uniform(1.0, 0.3))
        try:
            await self.__bot.send_group_message(targetGroup, MessageChain([
                Plain(message)
            ]))
            return True
        except:
            logger.error("发送消息出现未知错误！")
            return False
