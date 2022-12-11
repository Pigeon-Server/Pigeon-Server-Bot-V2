from module.module_interlining.useful_tools import find_answer  # 搜索答案方法
from module.module_base.config import except_list, module_config
from module.module_interlining.bot import message, control
from mirai.models.events import GroupMessage
from mirai_extensions.trigger import Filter
from module.module_base.permission import per


@Filter(GroupMessage)
def answer_judge(event: GroupMessage):
    if not per.check_player_permission(event.sender.id, per.Question.GetAnswer):
        return None
    if module_config.shutup:  # 如果排除列表启用，则排除
        if event.sender.id in except_list.stored_data:
            return None
    if str(event.message_chain).startswith('/') or str(event.message_chain).startswith("!"):  # 去除/
        return None
    respond = find_answer(event)  # 搜寻答案
    if respond is None:  # 如果返回值是空的，则返回None
        return None
    elif respond is not None:
        return respond


@control.on(answer_judge)
async def answer(event: GroupMessage, respond: str):
    if respond is not None:
        await message.send_message(event.group.id, respond, group_name=event.group.name, target_message=event.message_chain.message_id)