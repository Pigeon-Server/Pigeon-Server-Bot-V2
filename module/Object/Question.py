from module.Interlining.UsefulTools import FindAnswer  # 搜索答案方法
from module.BasicModule.Config import ExceptList, ModuleConfig
from module.Interlining.Bot import message, control
from mirai.models.events import GroupMessage
from mirai_extensions.trigger import Filter
from module.BasicModule.Permission import per


@Filter(GroupMessage)
def AnswerJudge(event: GroupMessage):
    if not per.CheckPlayerPermission(event.sender.id, per.Question.GetAnswer):
        return None
    if ModuleConfig.Shutup:  # 如果排除列表启用，则排除
        if event.sender.id in ExceptList.Data:
            return None
    if str(event.message_chain).startswith('/') or str(event.message_chain).startswith("!"):  # 去除/
        return None
    respond = FindAnswer(event)  # 搜寻答案
    if respond is None:  # 如果返回值是空的，则返回None
        return None
    elif respond is not None:
        return respond


@control.on(AnswerJudge)
async def Answer(event: GroupMessage, respond: str):
    if respond is not None:
        await message.SendMessage(event.group.id, respond, groupName=event.group.name, targetMessage=event.message_chain.message_id)