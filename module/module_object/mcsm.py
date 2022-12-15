from threading import Thread
from asyncio.tasks import sleep
from module.module_interlining.objectification import MCSM
from module.module_interlining.bot import bot, message
from module.module_base.config import main_config
from mirai.models.api import GroupMessage
from module.module_base.permission import per
from module.module_interlining.useful_tools import is_player_group, segmentation_str

MCSM.get_mcsm_info()


@bot.add_background_task()
async def check_status():
    while True:
        Thread(target=MCSM.update_instance_status).start()
        await sleep(main_config.mcsm_config.update_time)


@bot.on(GroupMessage)
async def mcsm_command(event: GroupMessage):
    async def send(send_message: str) -> None:
        await message.send_message(event.group.id, send_message, event.group.name)

    def check_player(permission: str) -> bool:
        return per.check_player_permission(str(event.sender.id), permission)

    per.creat_player(str(event.sender.id), main_config.permission.default if is_player_group(
        event.group.id) else main_config.permission.common)
    msg = str(event.message_chain)
    if msg.startswith('/mcsm') or msg.startswith('!mcsm'):
        command = msg[6:].rsplit(" ")
        commandLen = len(command)
        if command[0] == "":
            await send("MCSM模块帮助：\n"
                       "/mcsm check (InstanceName) [ServerName] 查询指定实例信息\n"
                       "/mcsm list [ServerName] 列出某一守护进程的所有实例名称\n"
                       "/mcsm rename (OriginalName) (NewName) 重命名某一守护进程或实例\n"
                       "/mcsm update [true] （强制）更新实例信息\n"
                       "/mcsm stop (InstanceName) [ServerName] 停止某一实例\n"
                       "/mcsm kill (InstanceName) [ServerName] 强行停止某一实例\n"
                       "/mcsm start (InstanceName) [ServerName] 开启某一实例\n"
                       "/mcsm restart (InstanceName) [ServerName] 重启某一实例\n"
                       "/mcsm command (InstanceName) (ServerName) (Command) 向某一实例执行命令")
        elif commandLen >= 1:
            match command[0]:
                case "check":
                    if check_player(per.Mcsm.Check):
                        if commandLen == 2:
                            await send(MCSM.check_instance_status(command[1]))
                        elif commandLen == 3:
                            await send(MCSM.check_instance_status(command[1], command[2]))
                    else:
                        await send("你无权这么做")
                case "list":
                    if check_player(per.Mcsm.List):
                        if commandLen == 1:
                            await send(MCSM.list_instance())
                        elif commandLen == 2:
                            await send(MCSM.list_instance(command[1]))
                    else:
                        await send("你无权这么做")
                case "rename":
                    if check_player(per.Mcsm.Rename):
                        if commandLen == 3:
                            await send(MCSM.rename(command[1], command[2]))
                    else:
                        await send("你无权这么做")
                case "update":
                    if commandLen == 1:
                        if check_player(per.Mcsm.Update.Common):
                            if MCSM.get_mcsm_info() is None:
                                await send("UUID更新成功")
                            else:
                                await send("UUID更新失败")
                        else:
                            await send("你无权这么做")
                    elif commandLen == 2 and command[1] == "true":
                        if check_player(per.Mcsm.Update.Force):
                            if MCSM.get_mcsm_info(True) is None:
                                await send("初始化信息成功")
                            else:
                                await send("初始化信息失败")
                        else:
                            await send("你无权这么做")
                case "stop":
                    if check_player(per.Mcsm.Stop):
                        if commandLen == 2:
                            await send(MCSM.stop(command[1]))
                        elif commandLen == 3:
                            await send(MCSM.stop(command[1], command[2]))
                    else:
                        await send("你无权这么做")
                case "kill":
                    if check_player(per.Mcsm.Kill):
                        if commandLen == 2:
                            await send(MCSM.stop(command[1], force_kill=True))
                        elif commandLen == 3:
                            await send(MCSM.stop(command[1], command[2], force_kill=True))
                    else:
                        await send("你无权这么做")
                case "start":
                    if check_player(per.Mcsm.Start):
                        if commandLen == 2:
                            await send(MCSM.start(command[1]))
                        elif commandLen == 3:
                            await send(MCSM.start(command[1], command[2]))
                    else:
                        await send("你无权这么做")
                case "restart":
                    if check_player(per.Mcsm.Restart):
                        if commandLen == 2:
                            await send(MCSM.restart(command[1]))
                        elif commandLen == 3:
                            await send(MCSM.restart(command[1], command[2]))
                    else:
                        await send("你无权这么做")
                case "command":
                    if check_player(per.Mcsm.Command):
                        cmd = ""
                        for x in range(3, commandLen):
                            cmd = cmd + command[x] + " "
                        await segmentation_str(send, await MCSM.run_command(command[1], command[2], cmd.removesuffix(" ")))
                    else:
                        await send("你无权这么做")
