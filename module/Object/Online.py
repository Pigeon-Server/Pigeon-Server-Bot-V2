from module.Interlining.Objectification import server  # 导入查询实例
from module.Interlining.Bot import message, control
from mirai.models.events import GroupMessage
from mirai_extensions.trigger import Filter
from module.BasicModule.Config import ModuleConfig


@Filter(GroupMessage)
def CheckServerStatusSpy(event: GroupMessage):
    msg = str(event.message_chain)
    command = msg[1:].rsplit(" ")[0]  # 按空格切分命令
    if (msg.startswith('/') or msg.startswith('!')) and (command == "服务器" or command == "online" or command == "server" or command == "player" or command == "info"):
        return True


@control.on(CheckServerStatusSpy)
async def CheckServer(event: GroupMessage, execute: bool):
    if execute:
        await message.SendMessage(event.group.id, await server.GetOnlinePlayer(), groupName=event.group.name)


if ModuleConfig.TPS:
    from module.Interlining.Objectification import MCSM

    @Filter(GroupMessage)
    def TpsSpy(event: GroupMessage):
        msg = str(event.message_chain)
        command = msg[1:].rsplit(" ")  # 按空格切分命令
        if (msg.startswith('/') or msg.startswith('!')) and command[0] == "tps" and len(command) > 1:
            return True


    @control.on(TpsSpy)
    async def Tps(event: GroupMessage, execute: bool):
        if execute:
            command = str(event.message_chain)[1:].rsplit(" ")
            temp = (await MCSM.RunCommand(command[1], "Server1", "forge tps")).rsplit("\n")
            await message.SendMessage(event.group.id, temp[len(temp) - 1], groupName=event.group.name)
