from module.module_base.config import main_config, module_config
from module.module_base.sql_relate import connected, cursor
from mirai.models.message import MessageChain, At
from mirai.models.events import GroupMessage
from requests import get
from filetype import guess
from hashlib import md5
from module.module_base.logger import logger
from os.path import exists, join
from typing import Union, Optional
if module_config.image_review:
    from module.module_base.config import image_list
from re import match as rematch

def is_admin_group(Group: int) -> bool:
    """
    判断所给出的是否是管理员群\n
    :param Group: 群号
    :return: true/false
    """

    return Group == main_config.mirai_bot_config.group_config.admin_group


def is_player_group(Group: int) -> bool:
    """
    判断所给出的是否是玩家群\n
    :param Group: 群号
    :return: true/false
    """

    return Group == main_config.mirai_bot_config.group_config.player_group


def ping_database() -> None:
    """
    ping数据库，并且自动重连\n
    """

    connected.ping(reconnect=True)


def is_at_bot(chain: MessageChain) -> bool:
    """
    判断是否艾特了机器人\n
    :param chain: 消息链，传入要判断的消息链
    :return: true/false
    """

    if chain.has(At):
        return chain.get_first(At).target == main_config.mirai_bot_config.qq


if module_config.questions:
    from module.module_base.config import faq_answer


    def find_answer(event: GroupMessage) -> Union[str, None]:
        """
        匹配关键词回复的答案\n
        :param event: 消息事件
        :return: 找到返回字符串，未找到返回None
        """

        message: str = str(event.message_chain).lower()  # 将消息链转换成文本
        respond: str | None = None

        if str(event.group.id) in faq_answer.keys():  # 如果群号在字典内出现
            answer: dict = faq_answer[str(event.group.id)]  # 提取该群的回答
            for raw in answer:  # 循环关键字
                if rematch('^.*\|.*[^|]$', raw):  # 列表处理
                    logger.debug("问答列表模式：True")
                    for key in raw.split("|"):
                        logger.debug(key)
                        if key.lower() in message:  # 如果匹配
                            respond = answer[raw]  # 返回结果
                else:
                    if raw.lower() in message:  # 如果匹配
                        respond = answer[raw]  # 返回结果
        if respond is None:  # 如果第一层循环没有找到答案
            if event.group.id == main_config.mirai_bot_config.group_config.admin_group:
                return None
            Global: dict = faq_answer["global"]  # 提取出全局问答
            for raw in Global:  # 循环关键字
                if rematch('^.*\|.*[^|]$', raw):  # 列表处理
                    logger.debug("问答列表模式：True")
                    for key in raw.split("|"):
                        logger.debug(key)
                        if key.lower() in message:  # 如果匹配
                            return Global[raw]  # 返回结果
                else:
                    if raw.lower() in message:  # 如果匹配
                        return Global[raw]  # 返回结果
            return None  # 两遍循环都没找到则返回None
        else:
            return respond  # 如果第一层循环找到答案就直接返回


async def segmentation_str(send, message: str) -> None:

    """
    切分消息并输出\n
    :param send: 发送使用的函数(传入的是一个函数！)
    :param message: 要发送的消息
    :return: None
    """

    if len(message) > 1000:
        number: int = main_config.info_limit  # 获取行数限制
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


def check_send_type(at_target: Union[int, None] = None, target_message: Union[int, None] = None) -> int:

    """
    判断应该使用的发送模式\n
    :param at_target: @目标，可以为空
    :param target_message: 回复目标，可以为空
    :return: int 0:没有@没有回复 1:没有@有回复 2:有@没有回复 3:既有@也有回复
    """

    if at_target is None and target_message is None:
        return 0
    elif at_target is None and target_message is not None:
        return 1
    elif at_target is not None and target_message is None:
        return 2
    elif at_target is not None and target_message is not None:
        return 3


def judge_token(id_: int) -> dict:

    """
    判断次Token是否能操作\n
    :param id_: 唯一id
    :return: {"status":True/False,"info":具体消息}
    """

    if cursor.execute(f"select * from wait where id = {id_}"):
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


async def download_file(urls: list, path: str, recall=None, callback=None) -> Optional[list]:

    """
    从url下载文件\n
    Args:
        urls: 文件列表
        path: 保存的目录
        recall: 撤回回调函数
        callback: 回调函数,可为空
    """

    success_list: list = []
    for url in urls:
        try:
            logger.debug("准备下载文件，URL：" + url)
            fileio = get(url)
        except:
            logger.error("下载失败，URL：" + url)
        else:
            file_type = guess(fileio.content)  # 文件类型识别
            file_md5 = md5(fileio.content).hexdigest()  # md5生成
            if file_type:  # 文件名拼接
                file_name = join(path, f"{file_md5}.{file_type.extension}")
            else:
                file_name = join(path, file_md5)
            if module_config.image_review:
                if "NoPass" in image_list.stored_data.keys() and f"{file_md5}.{file_type.extension}" in image_list.stored_data["NoPass"]:
                    logger.debug(f"{file_name}已记录为违规图片，撤回")
                    return await recall("违规图片")
                if "Pass" in image_list.stored_data.keys() and f"{file_md5}.{file_type.extension}" in image_list.stored_data["Pass"]:
                    logger.debug(f"{file_name}已判断通过,不保存")
                    continue
            if not exists(file_name):
                try:
                    open(file_name, "wb").write(fileio.content)
                except:
                    logger.error(f"保存文件{file_name}失败")
                else:
                    success_list.append(file_name)
                    logger.debug(f"文件保存为{file_name}")
            else:
                logger.debug(f"{file_name}文件已存在")
            fileio.close()
    return success_list if callback is None else callback(success_list)


