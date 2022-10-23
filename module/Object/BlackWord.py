from module.BasicModule.Config import BlockingWordList
from mirai.models.events import GroupMessage
from mirai_extensions.trigger import Filter
from module.Interlining.UsefulTools import IsAdminGroup
from re import match as rematch
from module.Interlining.Bot import control, message


@Filter(GroupMessage)
def BlockingWordSpy(event: GroupMessage):
    msg: str = str(event.message_chain)
    if IsAdminGroup(event.group.id):
        return False
    if event.sender.permission.value == "MEMBER":  # 如果成员不是管理员或者群主
        for raw in BlockingWordList:  # 遍历屏蔽名单
            if rematch(raw, msg) is not None:  # 如果有匹配返回true
                return True
        return False


@control.on(BlockingWordSpy)
async def BlockingWord(event: GroupMessage, recall: bool):
    if recall:
        await message.Recall(event.message_chain.message_id)  # 撤回
        await message.Mute(event.group.id, event.sender.id, 60)
        await message.SendMessage(event.group.id, "触发违禁词，已撤回消息", event.group.name, event.sender.id)