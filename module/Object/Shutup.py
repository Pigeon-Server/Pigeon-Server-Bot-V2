from module.Interlining.UsefulTools import IsAtBot  # 判断是否艾特了机器人
from module.Interlining.Bot import message, control
from mirai.models.events import GroupMessage
from mirai_extensions.trigger import Filter
from module.BasicModule.Permission import per
from module.BasicModule.Config import ExceptList


@Filter(GroupMessage)
def ShutupSpy(event: GroupMessage):
    msg = str(event.message_chain)
    if IsAtBot(event.message_chain) and ("shutup" in msg or "闭嘴" in msg):
        return True


@control.on(ShutupSpy)
async def Shutup(event: GroupMessage, execute: bool):
    if execute:
        if per.CheckPlayerPermission(event.sender.id, per.Question.Shutup):
            if event.sender.id in ExceptList.Data:
                ExceptList.EditData(event.sender.id, delData=True)
                await message.SendMessage(event.group.id, "坏了，我嘴闭不上了", groupName=event.group.name)
            else:
                ExceptList.EditData(event.sender.id)
                await message.SendMessage(event.group.id, "好了，我闭嘴了", groupName=event.group.name)
        else:
            await message.SendMessage(event.group.id, "你无权这么做", groupName=event.group.name)