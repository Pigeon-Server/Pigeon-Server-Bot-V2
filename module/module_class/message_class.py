from mirai.bot import Mirai
from asyncio.tasks import sleep
from random import uniform
from mirai.models.events import GroupMessage
from mirai.models.message import Plain, MessageChain, At, Image
from module.module_base.logger import logger
from module.module_base.config import main_config
from module.module_interlining.useful_tools import check_send_type
from sys import exit
from typing import Union
from base64 import b64encode


class Message:

    _bot = None
    player_name: str
    admin_name: str
    player_group: int
    admin_group: int
    welcome_message: dict

    def __init__(self, bot_obj: Mirai) -> None:
        """
        构造函数\n
        :param bot_obj: 传入bot实例
        """
        self._bot = bot_obj
        self.player_group = main_config.mirai_bot_config.group_config.player_group
        self.admin_group = main_config.mirai_bot_config.group_config.admin_group

    async def init(self) -> None:
        """
        消息模块初始化\n
        """
        logger.debug("正在初始化消息模块")
        try:
            self.player_name = (await self._bot.get_group(self.player_group)).name
            self.admin_name = (await self._bot.get_group(self.admin_group)).name
            self.welcome_message = self._message_decoding(main_config.welcome_message)
            for raw in self.welcome_message:
                if isinstance(raw, int):
                    data = self.welcome_message[raw]
                    if data["type"] == "image":
                        self.welcome_message[raw]["target"] = b64encode(open(data["target"], "rb").read())  # 提前用base64编码图片，减少后续发送耗时
            logger.success("初始化消息模块成功")
        except:
            logger.error("初始化消息模块失败")
            exit()

    async def send_welcome_message(self, qq: int, name: str, group_id: int, group_name: str = None):
        """
        发送欢迎消息\n
        Args:
            qq: 入群人qq号
            name: qq名
            group_id: 群号
            group_name: 群名
        """
        try:
            if group_name is None:
                group_name = (await self._bot.get_group(group_id)).name
            data = self.welcome_message  # 取出映射字典
            location = self.welcome_message["location"]  # 取出结构列表
            message_list = []  # 定义输出列表
            for raw in location:
                if isinstance(raw, int):  # 如果是整数
                    temp_data = data[raw]  # 取出对应的类型
                    match temp_data["type"]:  # 判断类型
                        case "variable":  # 如果为变量
                            match temp_data["target"]:
                                case "qq":
                                    message_list.append(Plain(qq))
                                case "name":
                                    message_list.append(Plain(name))
                                case "groupId":
                                    message_list.append(Plain(group_id))
                                case "groupName":
                                    message_list.append(Plain(group_name))
                        case "at":  # 如果是at类型
                            if temp_data["target"] == "qq":
                                message_list.append(At(qq))
                            else:
                                message_list.append(At(int(temp_data["target"])))
                        case "image":  # 如果是图片
                            message_list.append(Image(base64=temp_data["target"]))
                else:
                    message_list.append(Plain(raw))
            message = MessageChain(message_list)  # 构造消息链
            logger.info(f"[消息]->群:{group_name}({group_id}):{str(message)}")
            await sleep(uniform(1.0, 0.3))
            await self._bot.send_group_message(group_id, message)
        except:
            logger.error("发送消息时发生错误")

    async def recall_and_mute(self, event: GroupMessage, send_message: str = None) -> None:
        """
        撤回消息并禁言\n
        Args:
            event : 传入群消息事件
            send_message: 要发送的消息
        """
        if send_message is not None:
            await self.send_message(event.group.id, send_message, event.group.name, at_target=event.sender.id)
            if event.sender.permission == "MEMBER":
                await self.mute(event.group.id, event.sender.id)
                await self.recall(event.message_chain.message_id)

    async def recall(self, target_message: int) -> None:
        """
        撤回消息\n
        Args:
            target_message: 要撤回的目标消息
        """
        await sleep(uniform(1.0, 0.3))
        await self._bot.recall(target_message)

    async def mute(self, group_id: int, target_id: int, time: int = 600) -> None:
        """
        禁言成员\n
        Args:
            group_id: 群号
            target_id: 目标qq号
            time: 禁言时间，默认600s
        """
        await sleep(uniform(1.0, 0.3))
        await self._bot.mute(target=group_id, member_id=target_id, time=time)

    async def send_message(self, target_group: int, message: str, group_name: str = None, at_target: int = None, target_message: int = None) -> None:
        """
        向任意群发送消息\n
        Args:
            target_group: 发送消息的目标群
            message: 要发送的消息
            group_name: 发送的群名称，可以为空
            at_target: @目标，可以为空
            target_message: 回复目标，可以为空
        """
        logger.info(f"[消息]->群:{(await self._bot.get_group(target_group)).name if group_name is None else group_name}({target_group}):{message}")
        await sleep(uniform(1.0, 0.3))
        match check_send_type(at_target, target_message):
            case 0:
                try:
                    await self._bot.send_group_message(target_group, MessageChain([
                        Plain(message)
                    ]))
                except:
                    logger.error("发送消息时发生未知错误！")
            case 1:
                try:
                    await self._bot.send_group_message(target_group, MessageChain([
                        Plain(message)
                    ]), target_message)
                except:
                    logger.error("发送消息时发生未知错误！")
            case 2:
                try:
                    await self._bot.send_group_message(target_group, MessageChain([
                        At(at_target), Plain(message)
                    ]))
                except:
                    logger.error("发送消息时发生未知错误！")
            case 3:
                try:
                    await self._bot.send_group_message(target_group, MessageChain([
                        At(at_target), Plain(message)
                    ]), target_message)
                except:
                    logger.error("发送消息时发生未知错误！")

    async def send_player_message(self, message: str, at_target: int = None, target_message: int = None) -> None:
        """
        向配置文件中定义的玩家群发送消息\n
        Args:
            message: 要发送的消息
            at_target: @目标，可以为空
            target_message: 回复目标，可以为空
        """
        logger.info(f"[消息]->群:{self.player_name}({self.player_group}):{message}")
        await sleep(uniform(1.0, 0.3))
        match check_send_type(at_target, target_message):
            case 0:
                try:
                    await self._bot.send_group_message(self.player_group, MessageChain([
                        Plain(message)
                    ]))
                except:
                    logger.error("发送消息时发生未知错误！")
            case 1:
                try:
                    await self._bot.send_group_message(self.player_group, MessageChain([
                        Plain(message)
                    ]), target_message)
                except:
                    logger.error("发送消息时发生未知错误！")
            case 2:
                try:
                    await self._bot.send_group_message(self.player_group, MessageChain([
                        At(at_target), Plain(message)
                    ]))
                except:
                    logger.error("发送消息时发生未知错误！")
            case 3:
                try:
                    await self._bot.send_group_message(self.player_group, MessageChain([
                        At(at_target), Plain(message)
                    ]), target_message)
                except:
                    logger.error("发送消息时发生未知错误！")

    async def send_admin_message(self, message: str, at_target: int = None, target_message: int = None) -> None:
        """
        向配置文件中定义的管理群发送消息\n
        Args:
            message: 要发送的消息
            at_target: @目标，可以为空
            target_message: 回复目标，可以为空
        """
        logger.info(f"[消息]->群:{self.admin_name}({self.admin_group}):{message}")
        await sleep(uniform(1.0, 0.3))
        match check_send_type(at_target, target_message):
            case 0:
                try:
                    await self._bot.send_group_message(self.admin_group, MessageChain([
                        Plain(message)
                    ]))
                except:
                    logger.error("发送消息时发生未知错误！")
            case 1:
                try:
                    await self._bot.send_group_message(self.admin_group, MessageChain([
                        Plain(message)
                    ]), target_message)
                except:
                    logger.error("发送消息时发生未知错误！")
            case 2:
                try:
                    await self._bot.send_group_message(self.admin_group, MessageChain([
                        At(at_target), Plain(message)
                    ]))
                except:
                    logger.error("发送消息时发生未知错误！")
            case 3:
                try:
                    await self._bot.send_group_message(self.admin_group, MessageChain([
                        At(at_target), Plain(message)
                    ]), target_message)
                except:
                    logger.error("发送消息时发生未知错误！")

    @staticmethod
    def _message_decoding(data: str) -> Union[str, dict]:
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
            temp_data = data[data.find("{"):data.find("}") + 1]  # 切出大括号包含的内容
            if temp_data.find(":") == -1:  # 判断格式
                raise ValueError("消息占位符格式错误!")
            output.append(data[:data.find("{")])  # 推入{前内容
            result[count] = {
                "type": temp_data[1:temp_data.find(":")],
                "target": temp_data[temp_data.find(":") + 1:-1]
            }  # 写入映射表
            output.append(count)  # 推入映射Key
            count += 1  # 计数器递增
            data = data[data.find("}") + 1:]  # 切分字符串
        output.append(data)
        result["location"] = output
        return result
