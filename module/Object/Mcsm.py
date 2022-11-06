from threading import Thread
from asyncio.tasks import sleep
from module.Interlining.Objectification import MCSM
from module.Interlining.Bot import bot, message
from module.BasicModule.Config import MainConfig
from mirai.models.api import GroupMessage
from module.BasicModule.Permission import per
from module.Interlining.UsefulTools import IsPlayerGroup

MCSM.GetMCSMInfo()


@bot.add_background_task()
async def CheckStatus():
    while True:
        Thread(target=MCSM.UpdateInstanceStatus).start()
        await sleep(MainConfig.MCSMConfig.updateTime)


@bot.on(GroupMessage)
async def MCSMCommand(event: GroupMessage):
    async def send(sendMessage: str) -> None:
        await message.SendMessage(event.group.id, sendMessage, event.group.name)

    def checkPlayer(permission: str) -> bool:
        return per.CheckPlayerPermission(str(event.sender.id), permission)

    per.CreatPlayer(str(event.sender.id), MainConfig.Permission.default if IsPlayerGroup(
        event.group.id) else MainConfig.Permission.common)
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
                    if checkPlayer(per.Mcsm.Check):
                        if commandLen == 2:
                            await send(MCSM.CheckInstanceStatus(command[1]))
                        elif commandLen == 3:
                            await send(MCSM.CheckInstanceStatus(command[1], command[2]))
                    else:
                        await send("你无权这么做")
                case "list":
                    if checkPlayer(per.Mcsm.List):
                        if commandLen == 1:
                            await send(MCSM.ListInstance())
                        elif commandLen == 2:
                            await send(MCSM.ListInstance(command[1]))
                    else:
                        await send("你无权这么做")
                case "rename":
                    if checkPlayer(per.Mcsm.Rename):
                        if commandLen == 3:
                            await send(MCSM.ReName(command[1], command[2]))
                    else:
                        await send("你无权这么做")
                case "update":
                    if commandLen == 1:
                        if checkPlayer(per.Mcsm.Update.Common):
                            if MCSM.GetMCSMInfo() is None:
                                await send("UUID更新成功")
                            else:
                                await send("UUID更新失败")
                        else:
                            await send("你无权这么做")
                    elif commandLen == 2 and command[1] == "true":
                        if checkPlayer(per.Mcsm.Update.Force):
                            if MCSM.GetMCSMInfo(True) is None:
                                await send("初始化信息成功")
                            else:
                                await send("初始化信息失败")
                        else:
                            await send("你无权这么做")
                case "stop":
                    if checkPlayer(per.Mcsm.Stop):
                        if commandLen == 2:
                            await send(MCSM.Stop(command[1]))
                        elif commandLen == 3:
                            await send(MCSM.Stop(command[1], command[2]))
                    else:
                        await send("你无权这么做")
                case "kill":
                    if checkPlayer(per.Mcsm.Kill):
                        if commandLen == 2:
                            await send(MCSM.Stop(command[1], forceKill=True))
                        elif commandLen == 3:
                            await send(MCSM.Stop(command[1], command[2], forceKill=True))
                    else:
                        await send("你无权这么做")
                case "start":
                    if checkPlayer(per.Mcsm.Start):
                        if commandLen == 2:
                            await send(MCSM.Start(command[1])["info"])
                        elif commandLen == 3:
                            await send(MCSM.Start(command[1], command[2])["info"])
                    else:
                        await send("你无权这么做")
                case "restart":
                    if checkPlayer(per.Mcsm.Restart):
                        if commandLen == 2:
                            await send(MCSM.Restart(command[1]))
                        elif commandLen == 3:
                            await send(MCSM.Restart(command[1], command[2]))
                    else:
                        await send("你无权这么做")
                case "command":
                    if checkPlayer(per.Mcsm.Command):
                        cmd = ""
                        for x in range(3, commandLen):
                            cmd = cmd + command[x] + " "
                        await send(MCSM.RunCommand(command[1], command[2], cmd.removesuffix(" ")))
                    else:
                        await send("你无权这么做")
