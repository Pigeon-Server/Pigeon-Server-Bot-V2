from module.BasicModule.config import config
from module.BasicModule.sqlrelated import connected, cursor
from mirai.models.message import MessageChain, At
from mirai.models.events import GroupMessage

def IsAdminGroup(Group: str) -> bool:

    """
    判断所给出的是否是管理员群\n
    :param Group: 群号
    :return: true/false
    """

    return Group == config.Config["MiraiBotConfig"]["GroupConfig"]["AdminGroup"]

def IsPlayerGroup(Group: str) -> bool:

    """
    判断所给出的是否是玩家群\n
    :param Group: 群号
    :return: true/false
    """

    return Group == config.Config["MiraiBotConfig"]["GroupConfig"]["PlayerGroup"]

def PingDataBase() -> None:

    """
    ping数据库，并且自动重连\n
    """

    connected.ping(reconnect=True)

def IsAtBot(chain: MessageChain) -> bool:

    """
    判断是否艾特了机器人\n
    :param chain: 消息链，传入要判断的消息链
    :return: true/false
    """

    if chain.has(At):
        return chain.get_first(At).target == config.Config["MiraiBotConfig"]["QQ"]

def FindAnswer(event: GroupMessage) -> str | None:

    """
    匹配关键词回复的答案\n
    :param event: 消息事件
    :return: 找到返回字符串，未找到返回None
    """

    message: str = str(event.message_chain)  # 将消息转换成消息链
    if event.group.id in config.FAQ.keys():  # 如果群号在字典内出现
        answer: dict = config.FAQ[str(event.group.id)]  # 提取该群的回答
        for raw in answer:  # 循环关键字
            if raw in answer:  # 如果匹配
                return answer[raw]  # 返回结果
        return None  # 无匹配结果返回None
    else:  # 群号没有在字典内出现
        Global: dict = config.FAQ["global"]  # 提取出全局问答
        for raw in Global:  # 循环关键字
            if raw in message:  # 如果匹配
                return Global[raw]  # 返回结果
        return None  # 无匹配结果返回None

async def Segmentation(send, message: str) -> None:

    """
    切分消息并输出\n
    :param send: 发送使用的函数(传入的是一个函数！)
    :param message: 要发送的消息
    :return: None
    """

    if len(message) > 1000:
        number: int = config.Config["infolimit"]  # 获取行数限制
        count: int = 0  # 初始化计数器
        data = message[:-1].rsplit("\n")  # 分隔字符串
        tempMessage: str = ""  # 初始化输出变量
        for raw in data:  # 遍历字符串
            tempMessage = tempMessage + raw + "\n"  # 推入输出变量
            count += 1  # 计数器加一
            if count == number:  # 如果达到行数限制
                await send(tempMessage.removesuffix("\n"))  # 移除换行符，发送
                tempMessage = ""  # 重置输出字符串
                count = 0  # 重置计数器
        if count != 0:  # 遍历结束，如果计数器不为零
            await send(tempMessage.removesuffix("\n"))  # 说明输出变量有内容，发送一次
    else:
        await send(message.removesuffix("\n"))

def CheckSendType(AtTarget, targetMessage) -> int:
    if AtTarget is None and targetMessage is None:
        return 0
    elif AtTarget is None and targetMessage is not None:
        return 1
    elif AtTarget is not None and targetMessage is None:
        return 2
    elif AtTarget is not None and targetMessage is not None:
        return 3

def JudgeToken(id: int) -> dict:
    if cursor.execute(f"select * from wait where id = {id}"):
        data = cursor.fetchone()
        if data[16]:
            return {
                "status": False,
                "info": "此玩家token已被锁定"
            }
        elif data[17]:
            return {
                "status": False,
                "info": "玩家已获得白名单"
            }
        elif data[17] is False:
            return {
                "status": False,
                "info": "玩家的白名单已被拒绝"
            }
        elif not data[15]:
            return {
                "status": False,
                "info": "玩家还未申请白名单"
            }
        return {
            "status": True
        }
    else:
        return {
            "status": False,
            "info": "未查询到玩家"
        }
