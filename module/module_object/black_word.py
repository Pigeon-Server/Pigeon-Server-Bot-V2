from module.module_base.config import blocking_word_list
from mirai.models.events import GroupMessage, NudgeEvent
from mirai_extensions.trigger import Filter
from module.module_interlining.useful_tools import is_admin_group
from re import match as rematch
from module.module_interlining.bot import control, message, bot
from module.module_base.config import main_config
from asyncio import sleep
from datetime import datetime

exceptList: dict = {}


def check_time(userId: str) -> int:
    if userId in exceptList.keys():
        if exceptList[userId] < 16:
            exceptList[userId] += 1
            return 2 ** exceptList[userId] * 60
        else:
            return 2591999
    else:
        exceptList[userId] = 0
        return 2 ** 0 * 60


@bot.add_background_task()
async def clear():
    global exceptList
    today_finished = False
    while True:
        await sleep(1)
        now = datetime.now()
        if now.hour == 0 and now.minute == 0 and not today_finished:
            exceptList = {}
            today_finished = True
        if now.hour == 0 and now.minute == 1:
            today_finished = False


@Filter(GroupMessage)
def blocking_word_spy(event: GroupMessage):
    msg: str = str(event.message_chain).lower()
    if is_admin_group(event.group.id):
        return False
    if event.sender.permission.value == "MEMBER":  # 如果成员不是管理员或者群主
        for raw in blocking_word_list:  # 遍历屏蔽名单
            if rematch(raw.lower(), msg) is not None:  # 如果有匹配返回true
                return True
        return False


@control.on(blocking_word_spy)
async def blocking_word(event: GroupMessage, recall: bool):
    if recall:
        await message.recall(event.message_chain.message_id)  # 撤回
        await message.mute(event.group.id, event.sender.id, check_time(str(event.sender.id)))
        await message.send_message(event.group.id, "触发违禁词，已撤回消息", event.group.name, event.sender.id)


dataDict = {}


@bot.on(NudgeEvent)
async def fuck(event: NudgeEvent):
    if event.target == main_config.mirai_bot_config.qq:
        if str(event.from_id) not in dataDict.keys():
            dataDict[str(event.from_id)] = 1
        match dataDict[str(event.from_id)]:
            case 1:
                await message.mute(event.subject.id, event.from_id, 3600)
                dataDict[str(event.from_id)] += 1
            case 2:
                await message.mute(event.subject.id, event.from_id, 86400)
                dataDict[str(event.from_id)] += 1
            case 3:
                await message.mute(event.subject.id, event.from_id, 2592000)
                dataDict[str(event.from_id)] += 1
            case 4:
                await bot.kick(event.subject.id, event.from_id, "说了N遍了不听，爪巴")
