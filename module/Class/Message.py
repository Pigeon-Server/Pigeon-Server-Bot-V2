from mirai.bot import Mirai
from asyncio.tasks import sleep
from random import uniform
from mirai.models.events import GroupMessage
from mirai.models.message import Plain, MessageChain, At, Image
from module.BasicModule.Logger import logger
from module.BasicModule.Config import MainConfig
from module.Interlining.UsefulTools import CheckSendType
from sys import exit
from typing import Union
from base64 import b64encode

class Message:

    __bot = None
    PlayerName: str
    AdminName: str
    PlayerGroup: int
    AdminGroup: int
    WelcomeMessage: dict

    def __init__(self, botObj: Mirai) -> None:
        """
        构造函数\n
        :param botObj: 传入bot实例
        """
        self.__bot = botObj
        self.PlayerGroup = MainConfig.MiraiBotConfig.GroupConfig.PlayerGroup
        self.AdminGroup = MainConfig.MiraiBotConfig.GroupConfig.AdminGroup

    async def init(self) -> None:
        """
        消息模块初始化\n
        """
        logger.debug("正在初始化消息模块")
        try:
            self.PlayerName = (await self.__bot.get_group(self.PlayerGroup)).name
            self.AdminName = (await self.__bot.get_group(self.AdminGroup)).name
            self.WelcomeMessage = self.MessageDecoding(MainConfig.WelcomeMessage)
            for raw in self.WelcomeMessage:
                if isinstance(raw, int):
                    data = self.WelcomeMessage[raw]
                    if data["type"] == "image":
                        self.WelcomeMessage[raw]["target"] = b64encode(open(data["target"], "rb").read())  # 提前用base64编码图片，减少后续发送耗时
            logger.success("初始化消息模块成功")
        except:
            logger.error("初始化消息模块失败")
            exit()

    async def SendWelcomeMessage(self, qq: int, name: str, groupId: int, groupName: str = None):
        """
        发送欢迎消息\n
        Args:
            qq: 入群人qq号
            name: qq名
            groupId: 群号
            groupName: 群名
        """
        try:
            if groupName is None:
                groupName = (await self.__bot.get_group(groupId)).name
            data = self.WelcomeMessage  # 取出映射字典
            location = self.WelcomeMessage["location"]  # 取出结构列表
            messageList = []  # 定义输出列表
            for raw in location:
                if isinstance(raw, int):  # 如果是整数
                    tempData = data[raw]  # 取出对应的类型
                    match tempData["type"]:  # 判断类型
                        case "variable":  # 如果为变量
                            match tempData["target"]:
                                case "qq":
                                    messageList.append(Plain(qq))
                                case "name":
                                    messageList.append(Plain(name))
                                case "groupId":
                                    messageList.append(Plain(groupId))
                                case "groupName":
                                    messageList.append(Plain(groupName))
                        case "at":  # 如果是at类型
                            if tempData["target"] == "qq":
                                messageList.append(At(qq))
                            else:
                                messageList.append(At(int(tempData["target"])))
                        case "image":  # 如果是图片
                            messageList.append(Image(base64=tempData["target"]))
                else:
                    messageList.append(Plain(raw))
            message = MessageChain(messageList)  # 构造消息链
            logger.info(f"[消息]->群:{groupName}({groupId}):{str(message)}")
            await sleep(uniform(1.0, 0.3))
            await self.__bot.send_group_message(groupId, message)
        except:
            logger.error("发送消息出现错误")

    async def RecallAndMute(self, event: GroupMessage, sendMessage: str) -> None:
        """
        撤回消息并禁言\n
        Args:
            event : 传入群消息事件
            sendMessage: 要发送的消息
        """
        if sendMessage is not None and event.sender.permission == "MEMBER":
            await self.Mute(event.group.id, event.sender.id)
            await self.Recall(event.message_chain.message_id)
            await self.SendMessage(event.group.id, sendMessage, event.group.name, AtTarget=event.sender.id)

    async def Recall(self, targetMessage: int) -> None:
        """
        撤回消息\n
        Args:
            targetMessage: 要撤回的目标消息
        """
        await sleep(uniform(1.0, 0.3))
        await self.__bot.recall(targetMessage)

    async def Mute(self, groupId: int, id: int, time: int = 600) -> None:
        """
        禁言成员\n
        Args:
            groupId: 群号
            id: 目标qq号
            time: 禁言时间，默认600s
        """
        await sleep(uniform(1.0, 0.3))
        await self.__bot.mute(target=groupId, member_id=id, time=time)

    async def SendMessage(self, targetGroup: str, message: str, groupName: str = None, AtTarget: int = None, targetMessage: int = None) -> None:
        """
        向任意群发送消息\n
        Args:
            targetGroup: 发送消息的目标群
            message: 要发送的消息
            groupName: 发送的群名称，可以为空
            AtTarget: @目标，可以为空
            targetMessage: 回复目标，可以为空
        """
        logger.info(f"[消息]->群:{(await self.__bot.get_group(targetGroup)).name if groupName is None else groupName}({targetGroup}):{message}")
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

    @staticmethod
    def MessageDecoding(data: str) -> Union[str, dict]:
        """
        对格式化字符串进行解析\n
        Args:
            data: 要解析的字符串
        Returns:
            str: 如果data不是一个格式化字符串格式，则直接返回原字符串。如果data内有格式化内容，则返回字典{"location":[],1 :{},2:{} ...}
        """
        output: list = []  # 定义结构列表
        result: dict = {}  # 定义映射字典
        count: int = 1  # 定义计数器
        if data.find("{") == -1 or data.find("}") == -1:  # 如果找不到"{"或者"}"则直接返回原字符串
            return data
        while data.find("{") != -1 and data.find("}") != -1:  # 同时包含"{"和"}"
            tempData = data[data.find("{"):data.find("}") + 1]  # 切出大括号包含的内容
            if tempData.find(":") == -1:  # 判断格式
                raise ValueError("消息占位符格式错误!")
            output.append(data[:data.find("{")])  # 推入{前内容
            result[count] = {
                "type": tempData[1:tempData.find(":")],
                "target": tempData[tempData.find(":") + 1:-1]
            }  # 写入映射表
            output.append(count)  # 推入映射Key
            count += 1  # 计数器递增
            data = data[data.find("}") + 1:]  # 切分字符串
        result["location"] = output
        return result

