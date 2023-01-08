from module.module_interlining.useful_tools import is_at_bot  # 判断是否艾特了机器人
from module.module_interlining.bot import message, control
from mirai.models.events import GroupMessage
from mirai_extensions.trigger import Filter
from module.module_base.permission import per
from module.module_base.config import except_list


@Filter(GroupMessage)
def shutup_spy(event: GroupMessage):
    msg = str(event.message_chain)
    if (is_at_bot(event.message_chain) and ("shutup" in msg or "闭嘴" in msg)) or "气人机你闭嘴" == msg or "气人姬你闭嘴" == msg:
        return True


@control.on(shutup_spy)
async def Shutup(event: GroupMessage, execute: bool):
    if execute:
        if per.check_player_permission(event.sender.id, per.Question.Shutup):
            if event.sender.id in except_list.stored_data:
                except_list.edit_data(event.sender.id, del_data=True)
                await message.send_message(event.group.id, "坏了，我嘴闭不上了", group_name=event.group.name)
            else:
                except_list.edit_data(event.sender.id)
                await message.send_message(event.group.id, "好了，我闭嘴了", group_name=event.group.name)
        else:
            await message.send_message(event.group.id, "你无权这么做", group_name=event.group.name)
