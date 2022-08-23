from module.BasicModule.Logger import logger

class Message:

    """
    消息函数封装
    """

    __bot = None

    def __init__(self, bot) -> None:
        self.__bot = bot

    async def GetChannelName(self, id: str) -> str:
        """
        获取频道名称\n
        :param id: 频道id
        :return: str
        """
        return (await self.__bot.fetch_public_channel(id)).name

    async def ReplyMessage(self, msg, name: str, message: str) -> None:
        """
        发送回复消息\n
        :param name: 玩家名
        :param msg: 消息对象
        :param message: 要回复的消息
        :return: None
        """
        logger.info(f"[{await self.GetChannelName(msg.ctx.channel.id)}({msg.ctx.channel.id})]发送消息 --> Reply({name}):{message}")
        await msg.reply(message)

    async def SendMessage(self, id: str, message: str) -> None:
        """
        向指定频道发送消息\n
        :param id: 频道id
        :param message: 要发送的消息
        :return: None
        """
        logger.info(f"[{await self.GetChannelName(id)}({id})]发送消息 --> Send:{message}")
        await self.__bot.send(await self.__bot.fetch_public_channel(id), message)

    async def SendChannel(self, message: list[dict]) -> None:
        """
        同时向多个频道发送消息\n
        :param message: 要发送的消息(列表) [{"频道id"：“消息”}]
        :return: None
        """
        for raw in message:
            channelId = list(raw.keys())[0]
            sendMessage = list(raw.values())[0]
            logger.info(f"[{await self.GetChannelName(channelId)}({channelId})]发送消息 --> MultiplySend:{sendMessage}")
            await self.__bot.send(await self.__bot.fetch_public_channel(channelId), sendMessage)
