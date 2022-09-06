from module.BasicModule.Config import MainConfig, FAQConfig, ModuleConfig
from module.BasicModule.SqlRelate import connected, cursor
from mirai.models.message import MessageChain, At
from mirai.models.events import GroupMessage
from requests import get
from filetype import guess
from hashlib import md5
from module.BasicModule.Logger import logger
from os.path import exists, join
from typing import Union
if ModuleConfig.ImageReview:
    from module.BasicModule.Config import ImageList

def IsAdminGroup(Group: str) -> bool:
    """
    判断所给出的是否是管理员群\n
    :param Group: 群号
    :return: true/false
    """

    return Group == MainConfig.MiraiBotConfig.GroupConfig.AdminGroup


def IsPlayerGroup(Group: str) -> bool:
    """
    判断所给出的是否是玩家群\n
    :param Group: 群号
    :return: true/false
    """

    return Group == MainConfig.MiraiBotConfig.GroupConfig.PlayerGroup


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
        return chain.get_first(At).target == MainConfig.MiraiBotConfig.QQ


def FindAnswer(event: GroupMessage) -> Union[str, None]:
    """
    匹配关键词回复的答案\n
    :param event: 消息事件
    :return: 找到返回字符串，未找到返回None
    """

    message: str = str(event.message_chain)  # 将消息链转换成文本
    respond: str = None

    if str(event.group.id) in FAQConfig.keys():  # 如果群号在字典内出现
        answer: dict = FAQConfig[str(event.group.id)]  # 提取该群的回答
        for raw in answer:  # 循环关键字
            if raw in message:  # 如果匹配
                respond = answer[raw]  # 返回结果
    if respond is None:  # 如果第一层循环没有找到答案
        if event.group.id == MainConfig.MiraiBotConfig.GroupConfig.AdminGroup:
            return None
        Global: dict = FAQConfig["global"]  # 提取出全局问答
        for raw in Global:  # 循环关键字
            if raw in message:  # 如果匹配
                return Global[raw]  # 返回结果
        return None  # 两遍循环都没找到则返回None
    else:
        return respond  # 如果第一层循环找到答案就直接返回


async def Segmentation(send, message: str) -> None:

    """
    切分消息并输出\n
    :param send: 发送使用的函数(传入的是一个函数！)
    :param message: 要发送的消息
    :return: None
    """

    if len(message) > 1000:
        number: int = MainConfig.infoLimit  # 获取行数限制
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


def CheckSendType(AtTarget: Union[int, None] = None, targetMessage: Union[int, None] = None) -> int:

    """
    判断应该使用的发送模式\n
    :param AtTarget: @目标，可以为空
    :param targetMessage: 回复目标，可以为空
    :return: int 0:没有@没有回复 1:没有@有回复 2:有@没有回复 3:既有@也有回复
    """

    if AtTarget is None and targetMessage is None:
        return 0
    elif AtTarget is None and targetMessage is not None:
        return 1
    elif AtTarget is not None and targetMessage is None:
        return 2
    elif AtTarget is not None and targetMessage is not None:
        return 3


def JudgeToken(id: int) -> dict:

    """
    判断次Token是否能操作\n
    :param id: 唯一id
    :return: {"status":True/False,"info":具体消息}
    """

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

async def DownloadFile(urls: list, Path: str, FileName: Union[list, bool], recall, callback=None) -> Union[list, None]:

    """
    从url下载文件\n
    Args:
        urls: 文件列表
        Path: 保存的目录
        FileName: 文件名
        recall: 撤回回调函数
        callback: 回调函数,可为空
    """

    SuccessList: list = []
    for index, url in enumerate(urls, 0):
        try:
            logger.debug("准备下载文件，URL：" + url)
            fileio = get(url)
        except:
            logger.error("下载失败，URL：" + url)
        else:
            FileType = guess(fileio.content)  # 文件类型识别
            if isinstance(FileName, bool) and FileName:
                fileMd5 = md5(fileio.content).hexdigest()  # md5生成
                if FileType:  # 文件名拼接
                    fileName = join(Path, f"{fileMd5}.{FileType.extension}")
                else:
                    fileName = join(Path, fileMd5)
                if ImageList.QueryData(f"{fileMd5}.{FileType.extension}", "NoPass"):
                    logger.debug("已记录为违规图片，撤回")
                    return await recall("违规图片")
                if not exists(fileName):
                    if ImageList.QueryData(f"{fileMd5}.{FileType.extension}", "Pass"):
                        logger.debug("已判断通过,不保存")
                        continue
                    SuccessList.append(fileName)
                    open(fileName, "wb").write(fileio.content)
                    logger.debug(f"文件保存为{fileName}")
                fileio.close()
            else:
                if FileType:  # 文件名拼接
                    fileName = join(Path, f"{FileName[index]}.{FileType.extension}")
                else:
                    fileName = join(Path, FileName[index])
                if not exists(fileName):
                    SuccessList.append(fileName)
                    open(fileName, "wb").write(fileio.content)
                    logger.debug(f"文件保存为{fileName}")
                fileio.close()
    return SuccessList if callback is None else callback(SuccessList)


