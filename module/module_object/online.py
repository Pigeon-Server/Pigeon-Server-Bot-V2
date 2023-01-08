from module.module_interlining.objectification import server  # 导入查询实例
from module.module_interlining.bot import message, control
from mirai.models.events import GroupMessage
from mirai_extensions.trigger import Filter
from module.module_base.config import module_config


@Filter(GroupMessage)
def check_server_status_spy(event: GroupMessage):
    msg = str(event.message_chain)
    command = msg[1:].rsplit(" ")[0]  # 按空格切分命令
    if (msg.startswith('/') or msg.startswith('!')) and (command == "服务器" or command == "online" or command == "server" or command == "player" or command == "info"):
        return True


@control.on(check_server_status_spy)
async def check_server(event: GroupMessage, execute: bool):
    if execute:
        await message.send_message(event.group.id, await server.get_online_player(), group_name=event.group.name)


if module_config.tps:
    from module.module_interlining.objectification import MCSM

    @Filter(GroupMessage)
    def tps_spy(event: GroupMessage):
        msg = str(event.message_chain)
        command = msg[1:].rsplit(" ")  # 按空格切分命令
        if (msg.startswith('/') or msg.startswith('!')) and command[0] == "tps" and len(command) > 1:
            return True


    @control.on(tps_spy)
    async def tps(event: GroupMessage, execute: bool):
        if execute:
            command = str(event.message_chain)[1:].rsplit(" ")
            await message.send_message(event.group.id, (await MCSM.run_command(command[1], "Server1", "forge tps")).rsplit("\n")[-1], group_name=event.group.name)
