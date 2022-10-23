from module.Interlining.Objectification import server  # 导入查询实例
from module.Interlining.Bot import message, control
from mirai.models.events import GroupMessage
from mirai_extensions.trigger import Filter


@Filter(GroupMessage)
def CheckServerStatusSpy(event: GroupMessage):
    msg = str(event.message_chain)
    command = msg[1:].rsplit(" ")[0]  # 按空格切分命令
    if (msg.startswith('/') or msg.startswith('!')) and (
            command == "服务器" or command == "online" or command == "server" or command == "player" or command == "info"):
        return True


@control.on(CheckServerStatusSpy)
async def CheckServer(event: GroupMessage, execute: bool):
    if execute:
        await message.SendMessage(event.group.id, await server.GetOnlinePlayer(), groupName=event.group.name)