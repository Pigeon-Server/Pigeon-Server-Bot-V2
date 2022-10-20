# 基础模块导入
from module.Interlining.Bot import bot, message, control, interrupt  # 导入bot基类，消息发送模块，事件控制器模块
from module.BasicModule.Config import MainConfig, ModuleConfig  # 配置类示例导入
from mirai_extensions.trigger import Filter  # 导入过滤器模块
from mirai.bot import Startup, Shutdown  # 导入机器人启动关闭事件
from re import match as rematch  # 导入正则表达式并重命名（与match冲突）
from mirai.models.message import Plain, At
from mirai.models.events import GroupMessage, MemberJoinRequestEvent, MemberJoinEvent  # 导入群组消息模型
from module.BasicModule.SqlRelate import cursor  # 导入数据库事务和连接实例
from module.BasicModule.Logger import logger  # 导入日志记录模块
from module.Interlining.UsefulTools import IsAdminGroup, IsPlayerGroup, Segmentation, PingDataBase  # 判断是否是管理群或玩家群，消息切分，ping数据库
from module.Interlining.Objectification import query  # 导入查询类实例
from module.BasicModule.SqlRelate import connected
from module.BasicModule.Permission import per

# 是否查询MC更新
if ModuleConfig.CheckMCUpdate:
    from module.Interlining.CheckUpdate import CheckUpdate
    from asyncio import sleep


    @bot.add_background_task()
    async def CheckUpdateTask():
        while True:
            await sleep(MainConfig.UpdateCheckInterval)
            await CheckUpdate()

# 是否启用WebSocket上报（未完成）
if ModuleConfig.WebsocketReport:
    from module.Interlining.WebSocket import websocket  # 导入ws类实例


    @bot.add_background_task()  # 添加背景任务
    async def Websocket():
        await websocket.Connect()
        while True:  # 重复运行
            async for msg in websocket.connection:
                data = eval(msg)
                if data['type'] == "OnlineBroadcast":
                    websocket.clientInfo[data['uuid']] = data['name']
                elif data['type'] == "OfflineBroadcast":
                    del websocket.clientInfo[data['uuid']]


    @bot.on(Shutdown)
    async def DisConnection(event: Shutdown):
        await websocket.DisConnection()

# 是否启用图片审查（未完成）
if ModuleConfig.ImageReview:
    from module.Interlining.UsefulTools import DownloadFile  # 下载文件方法
    from module.Interlining.CosRelate import CosClient  # 导入cos类实例
    from mirai.models.message import Image  # 导入Image类
    from module.BasicModule.Config import ImageList


    @bot.on(GroupMessage)
    async def ImageReview(event: GroupMessage):
        if event.message_chain.has(Image):  # 如果消息链里面有Image消息
            await DownloadFile(list(image.url for image in event.message_chain.get(Image)), "image", True,
                               lambda recall: message.RecallAndMute(event, recall),
                               lambda fileList: CosClient.UploadFile(fileList,
                                                                     EnableMD5=True) if CosClient.connected else None)
            if ImageList.Data["Wait"]:
                await CosClient.FilesContentRecognition(ImageList.Data["Wait"], MainConfig.CosConfig.BizType,
                                                        callback=lambda recall: message.RecallAndMute(event,
                                                                                                      recall))

# 是否启用问答模块
if ModuleConfig.Questions:
    from module.Interlining.UsefulTools import FindAnswer  # 搜索答案方法
    from module.BasicModule.Config import ExceptList

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
            await message.SendMessage(event.group.id, respond, groupName=event.group.name,
                                      targetMessage=event.message_chain.message_id)
# 是否允许玩家自主设置屏蔽
if ModuleConfig.Shutup and ModuleConfig.Questions:
    from module.Interlining.UsefulTools import IsAtBot  # 判断是否艾特了机器人


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

# 是否开启在线人数查询
if ModuleConfig.Online:
    from module.Interlining.Objectification import server  # 导入查询实例


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

# 是否开启触发关键词撤回
if ModuleConfig.BlockWord:
    from module.BasicModule.Config import BlockingWordList

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

# 是否启用白名单模块
if ModuleConfig.WhiteList:
    from module.Interlining.Objectification import whitelist

# 是否启用黑名单模块
if ModuleConfig.BlackList:
    from module.Interlining.Objectification import blacklist

if ModuleConfig.AutomaticReview:
    count: int = 1
    processing: int = 1


    @bot.on(MemberJoinRequestEvent)
    async def ReviewJoin(event: MemberJoinRequestEvent):
        memberId = event.from_id
        groupId = event.group_id
        if not IsAdminGroup(groupId):
            memberInfo = await bot.user_profile(memberId)
            global count, processing
            temp = count
            send = "[{groupName}]有一条入群申请:\n" + f"QQ名: {memberInfo.nickname}\nQQ号: {memberId}\n等级: {memberInfo.level}\n" \
                   f"年龄: {memberInfo.age}\n入群信息：\n{event.message}\n个性签名: {memberInfo.sign}\n" + "处理结果：{result}"
            if (MainConfig.AutomaticReview.age.min <= memberInfo.age <= MainConfig.AutomaticReview.age.max) and \
                    memberInfo.level >= MainConfig.AutomaticReview.level:
                await bot.allow(event)
                await message.AdminMessage(send.format(groupName=message.PlayerName if IsPlayerGroup(groupId) else (await bot.get_group(groupId)).name,
                                                       result="满足入群条件，已同意"))
            elif MainConfig.AutomaticReview.Refuse:
                await message.AdminMessage(send.format(groupName=message.PlayerName if IsPlayerGroup(groupId) else (await bot.get_group(groupId)).name,
                                                       result="未满足入群条件，已自动拒绝"))
                await bot.decline(event, "未达到入群要求", ban=MainConfig.AutomaticReview.BlackList)
            else:
                await message.AdminMessage(send.format(groupName=message.PlayerName if IsPlayerGroup(groupId) else (await bot.get_group(groupId)).name,
                                                       result="未满足入群条件，需人工审核(是/否/拉黑/忽略)"))
                count += 1

                @Filter(GroupMessage)
                def WaitCommit(msg: GroupMessage):
                    if msg.message_chain.has(Plain) and IsAdminGroup(msg.group.id) and temp == processing:
                        res = msg.message_chain.get_first(Plain).text
                        if res.startswith("是"):
                            return {
                                "code": 1
                            }
                        elif res.startswith("否"):
                            if len(res) > 1:
                                return {
                                    "code": 2,
                                    "message": res[2:]
                                }
                            else:
                                return {
                                    "code": 3
                                }
                        elif res.startswith("忽略"):
                            if len(res) > 2:
                                return {
                                    "code": 4,
                                    "message": res[3:]
                                }
                            else:
                                return {
                                    "code": 5
                                }
                        elif res.startswith("忽略"):
                            return {
                                    "code": 6
                                }

                data = await interrupt.wait(WaitCommit)
                match data["code"]:
                    case 1:
                        await message.AdminMessage("已同意")
                        await bot.allow(event)
                    case 2:
                        await message.AdminMessage(f"已拒绝, 理由:{data['message']}")
                        await bot.decline(event, data["message"])
                    case 3:
                        await message.AdminMessage(f"已拉黑")
                        await bot.decline(event, "未达到入群标准")
                    case 4:
                        await message.AdminMessage("已拉黑")
                        await bot.decline(event, data["message"], ban=True)
                    case 5:
                        await message.AdminMessage("已拒绝")
                        await bot.decline(event, "未达到入群标准", ban=True)
                    case 6:
                        await message.AdminMessage("已忽略")
                        await bot.ignore(event)
                processing += 1

# MCSM模块
if ModuleConfig.MCSMModule:
    from threading import Thread
    from asyncio.tasks import sleep
    from module.Interlining.Objectification import MCSM
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
                            await send(MCSM.RunCommand(command[1], command[2], cmd))
                        else:
                            await send("你无权这么做")


@bot.on(GroupMessage)
async def Permission(event: GroupMessage):
    async def send(sendMessage: str) -> None:
        await message.SendMessage(event.group.id, sendMessage, event.group.name)

    def checkPlayer(permission: str) -> bool:
        return per.CheckPlayerPermission(str(event.sender.id), permission)

    msg = str(event.message_chain)
    if msg.startswith('/permission') or msg.startswith('!permission') or msg.startswith('/ps') or msg.startswith('!ps'):
        command = msg[1:].rsplit(" ")
        commandLen = len(command)
        if commandLen == 1:
            await send(f"Permission模块帮助: \n"
                       f"/permission player (At | id) add (permission)\n"
                       f"/permission player (At | id) remove (permission)\n"
                       f"/permission player (At | id) clone (At | id)\n"
                       f"/permission player (At | id) check (permission)\n"
                       f"/permission player (At | id) inherit add (groupName)\n"
                       f"/permission player (At | id) inherit remove (groupName)\n"
                       f"/permission player (At | id) inherit set (groupName)\n"
                       f"/permission player (At | id) del\n"
                       f"/permission player (At | id) list\n"
                       f"/permission player (At | id) info\n"
                       f"/permission player (At | id) create [groupName]\n"
                       f"/permission group (groupName) add (permission)\n"
                       f"/permission group (groupName) remove (permission)\n"
                       f"/permission group (groupName) clone (groupName)\n"
                       f"/permission group (groupName) check (permission)\n"
                       f"/permission group (groupName) inherit add (groupName)\n"
                       f"/permission group (groupName) inherit remove (groupName)\n"
                       f"/permission group (groupName) del\n"
                       f"/permission group (groupName) list\n"
                       f"/permission group (groupName) info\n"
                       f"/permission group (groupName) create\n"
                       f"/permission reload [true]\n"
                       f"/permission list [word]")
        else:
            if command[1] == "player":
                if commandLen >= 4:
                    match len(event.message_chain.get(At)):
                        case 2:
                            if command[3] == "clone":
                                if checkPlayer(per.Permission.Player.Clone):
                                    temp = event.message_chain.get(At)
                                    await send(per.ClonePlayerPermission(str(temp[1].target), str(temp[0].target)))
                                else:
                                    await send("你无权这么做")
                        case 1:
                            match command[3]:
                                case "add":
                                    if checkPlayer(per.Permission.Player.Give):
                                        if commandLen == 5:
                                            await send(per.AddPlayerPermission(str(event.message_chain.get_first(At).target), command[4]))
                                        else:
                                            await send("命令参数不正确")
                                    else:
                                        await send("你无权这么做")
                                case "remove":
                                    if checkPlayer(per.Permission.Player.Remove):
                                        if commandLen == 5:
                                            await send(per.RemovePlayerPermission(str(event.message_chain.get_first(At).target), command[4]))
                                        else:
                                            await send("命令参数不正确")
                                    else:
                                        await send("你无权这么做")
                                case "check":
                                    if checkPlayer(per.Permission.Player.Check):
                                        if commandLen == 5:
                                            await send(per.CheckPlayerPermission(str(event.message_chain.get_first(At).target), command[4]))
                                        else:
                                            await send("命令参数不正确")
                                    else:
                                        await send("你无权这么做")
                                case "list":
                                    if checkPlayer(per.Permission.Player.List):
                                        msg = f"{event.message_chain.get_first(At).target}拥有的权限为：\n"
                                        for raw in per.GetPlayerPermission(str(event.message_chain.get_first(At).target)):
                                            msg += f"{raw}\n"
                                        await send(msg.removesuffix("\n"))
                                    else:
                                        await send("你无权这么做")
                                case "info":
                                    if checkPlayer(per.Permission.Player.Info):
                                        data = per.GetPlayerInfo(str(event.message_chain.get_first(At).target))
                                        if data is None:
                                            await send("未查询到权限记录")
                                        else:
                                            msg = f"{event.message_chain.get_first(At).target}的信息如下:\n"
                                            if "group" in data.keys():
                                                temp = "权限组: \n"
                                                for raw in data["group"]:
                                                    temp += f"{raw}\n"
                                                msg += temp
                                            if "permission" in data.keys():
                                                temp = "权限: \n"
                                                for raw in data["permission"]:
                                                    temp += f"{raw}\n"
                                                msg += temp
                                            await send(msg.removesuffix("\n"))
                                    else:
                                        await send("你无权这么做")
                                case "create":
                                    if checkPlayer(per.Permission.Player.Create):
                                        if commandLen == 4:
                                            await send(per.CreatPlayer(str(event.message_chain.get_first(At).target)))
                                        elif commandLen == 5:
                                            await send(per.CreatPlayer(str(event.message_chain.get_first(At).target), command[4]))
                                        else:
                                            await send("命令参数不正确")
                                    else:
                                        await send("你无权这么做")
                                case "inherit":
                                    if commandLen >= 6:
                                        match command[4]:
                                            case "add":
                                                if checkPlayer(per.Permission.Player.Inherit.Add):
                                                    await send(per.AddPlayerParent(str(event.message_chain.get_first(At).target), command[5]))
                                                else:
                                                    await send("你无权这么做")
                                            case "remove":
                                                if checkPlayer(per.Permission.Player.Inherit.Del):
                                                    await send(per.RemovePlayerParent(str(event.message_chain.get_first(At).target), command[5]))
                                                else:
                                                    await send("你无权这么做")
                                            case "set":
                                                if checkPlayer(per.Permission.Player.Inherit.Set):
                                                    if commandLen == 6:
                                                        await send(per.SetPlayerGroup(str(event.message_chain.get_first(At).target), command[5]))
                                                    elif commandLen > 6:
                                                        temp = []
                                                        for x in range(6, commandLen):
                                                            temp += x
                                                        await send(per.SetPlayerGroup(str(event.message_chain.get_first(At).target), temp))
                                                else:
                                                    await send("你无权这么做")
                                    else:
                                        await send("命令参数不正确")
                        case 0:
                            match command[3]:
                                case "add":
                                    if checkPlayer(per.Permission.Player.Give):
                                        if commandLen == 5:
                                            await send(per.AddPlayerPermission(command[2], command[4]))
                                        else:
                                            await send("命令参数错误")
                                    else:
                                        await send("你无权这么做")
                                case "remove":
                                    if checkPlayer(per.Permission.Player.Remove):
                                        if commandLen == 5:
                                            await send(per.RemovePlayerPermission(command[2], command[4]))
                                        else:
                                            await send("命令参数错误")
                                    else:
                                        await send("你无权这么做")
                                case "check":
                                    if checkPlayer(per.Permission.Player.Check):
                                        if commandLen == 5:
                                            await send(per.CheckPlayerPermission(command[2], command[4]))
                                        else:
                                            await send("命令参数错误")
                                    else:
                                        await send("你无权这么做")
                                case "clone":
                                    if checkPlayer(per.Permission.Player.Clone):
                                        if commandLen == 5:
                                            await send(per.ClonePlayerPermission(command[2], command[4]))
                                        else:
                                            await send("命令参数错误")
                                    else:
                                        await send("你无权这么做")
                                case "list":
                                    if checkPlayer(per.Permission.Player.List):
                                        msg = f"{command[2]}拥有的权限为：\n"
                                        for raw in per.GetPlayerPermission(command[2]):
                                            msg += f"{raw}\n"
                                        await send(msg.removesuffix("\n"))
                                    else:
                                        await send("你无权这么做")
                                case "info":
                                    if checkPlayer(per.Permission.Player.Info):
                                        data = per.GetPlayerInfo(command[2])
                                        if data is None:
                                            await send("未查询到权限记录")
                                        else:
                                            msg = f"{command[2]}的信息如下:\n"
                                            if "group" in data.keys():
                                                temp = "权限组: \n"
                                                for raw in data["group"]:
                                                    temp += f"{raw}\n"
                                                msg += temp
                                            if "permission" in data.keys():
                                                temp = "权限: \n"
                                                for raw in data["permission"]:
                                                    temp += f"{raw}\n"
                                                msg += temp
                                            await send(msg.removesuffix("\n"))
                                    else:
                                        await send("你无权这么做")
                                case "create":
                                    if checkPlayer(per.Permission.Player.Create):
                                        if commandLen == 4:
                                            await send(per.CreatPlayer(command[3]))
                                        elif commandLen == 5:
                                            await send(per.CreatPlayer(command[3], command[4]))
                                        else:
                                            await send("命令参数不正确")
                                    else:
                                        await send("你无权这么做")
                                case "inherit":
                                    if commandLen >= 6:
                                        match command[4]:
                                            case "add":
                                                if checkPlayer(per.Permission.Player.Inherit.Add):
                                                    await send(per.AddPlayerParent(command[2], command[5]))
                                                else:
                                                    await send("你无权这么做")
                                            case "remove":
                                                if checkPlayer(per.Permission.Player.Inherit.Del):
                                                    await send(per.RemovePlayerParent(command[2], command[5]))
                                                else:
                                                    await send("你无权这么做")
                                            case "set":
                                                if checkPlayer(per.Permission.Player.Inherit.Set):
                                                    if commandLen == 6:
                                                        await send(per.SetPlayerGroup(command[2], command[5]))
                                                    elif commandLen > 6:
                                                        temp = []
                                                        for x in range(6, commandLen):
                                                            temp += x
                                                        await send(per.SetPlayerGroup(command[2], temp))
                                                else:
                                                    await send("你无权这么做")
                                    else:
                                        await send("命令参数不正确")
                else:
                    await send("命令缺少参数")
            elif command[1] == "group":
                if commandLen >= 4:
                    match command[3]:
                        case "add":
                            if checkPlayer(per.Permission.Group.Give):
                                if commandLen == 5:
                                    await send(per.AddGroupPermission(command[2]))
                                else:
                                    await send("命令参数错误")
                            else:
                                await send("你无权这么做")
                        case "remove":
                            if checkPlayer(per.Permission.Group.Del):
                                if commandLen == 5:
                                    await send(per.ReloadGroupPermission(command[2]))
                                else:
                                    await send("命令参数错误")
                            else:
                                await send("你无权这么做")
                        case "check":
                            if checkPlayer(per.Permission.Group.Check):
                                if commandLen == 5:
                                    await send(per.CheckGroupPermission(command[2]))
                                else:
                                    await send("命令参数错误")
                            else:
                                await send("你无权这么做")
                        case "clone":
                            if checkPlayer(per.Permission.Group.Clone):
                                if commandLen == 5:
                                    await send(per.CloneGroupPermission(command[2], command[4]))
                                else:
                                    await send("命令参数错误")
                            else:
                                await send("你无权这么做")
                        case "list":
                            if checkPlayer(per.Permission.Group.List):
                                msg = f"{command[2]}拥有的权限为：\n"
                                for raw in per.GetGroupPermission(command[2]):
                                    msg += f"{raw}\n"
                                await send(msg.removesuffix("\n"))
                            else:
                                await send("你无权这么做")
                        case "info":
                            if checkPlayer(per.Permission.Group.Info):
                                data = per.GetGroupInfo(command[2])
                                if data is None:
                                    await send("此权限组不存在")
                                else:
                                    msg = f"{command[2]}的信息如下:\n"
                                    if "parent" in data.keys():
                                        temp = "权限组: \n"
                                        for raw in data["parent"]:
                                            temp += f"{raw}\n"
                                        msg += temp
                                    if "permission" in data.keys():
                                        temp = "权限: \n"
                                        for raw in data["permission"]:
                                            temp += f"{raw}\n"
                                        msg += temp
                                    await send(msg)
                            else:
                                await send("你无权这么做")
                        case "create":
                            if checkPlayer(per.Permission.Group.Create):
                                if commandLen == 4:
                                    await send(per.CreatGroup(command[3]))
                                else:
                                    await send("命令参数不正确")
                            else:
                                await send("你无权这么做")
                        case "inherit":
                            if commandLen == 6:
                                match command[4]:
                                    case "add":
                                        if checkPlayer(per.Permission.Group.Inherit.Add):
                                            await send(per.AddGroupParent(command[2], command[5]))
                                        else:
                                            await send("你无权这么做")
                                    case "remove":
                                        if checkPlayer(per.Permission.Group.Inherit.Del):
                                            await send(per.RemoveGroupParent(command[2], command[5]))
                                        else:
                                            await send("你无权这么做")
                            else:
                                await send("命令参数不正确")
            elif command[1] == "list":
                if checkPlayer(per.Permission.ShowList):
                    if commandLen == 2:
                        data = per.GetPermissionNode()
                        msg = "所有权限节点: \n"
                        for raw in data:
                            msg += f"{raw}\n"
                    elif commandLen == 3:
                        data = per.GetPermissionNode()
                        msg = f"{command[2]}权限节点: \n"
                        for raw in data:
                            if command[2] in raw:
                                msg += f"{raw}\n"
                        await Segmentation(send, msg)
                else:
                    await send("你无权这么做")
            elif command[1] == "reload":
                if commandLen == 2:
                    if checkPlayer(per.Permission.Reload.Common):
                        await send(per.ReloadGroupPermission())
                    else:
                        await send("你无权这么做")
                elif commandLen == 3 and command[2] == "true":
                    if checkPlayer(per.Permission.Reload.Force):
                        await send(per.ReloadGroupPermission(True))
                    else:
                        await send("你无权这么做")


@bot.on(Startup)
async def Startup(event: Startup):
    await message.init()  # 初始化消息发送模块
    logger.info("\n  _____  _                               _____                               \n"
                " |  __ \\(_)                             / ____|                              \n"
                " | |__) |_   __ _   ___   ___   _ __   | (___    ___  _ __ __   __ ___  _ __ \n"
                " |  ___/| | / _` | / _ \\ / _ \\ | '_ \\   \\___ \\  / _ \\| '__|\\ \\ / // _ \\| '__|\n"
                " | |    | || (_| ||  __/| (_) || | | |  ____) ||  __/| |    \\ V /|  __/| |   \n"
                " |_|    |_| \\__, | \\___| \\___/ |_| |_| |_____/  \\___||_|     \\_/  \\___||_|   \n"
                "             __/ |                                                           \n"
                "            |___/                                                            "
                "\n\n[Github源码库地址，欢迎贡献&完善&Debug]\nhttps://github.com/Pigeon-Server/Pigeon-Server-Bot-V2.git")


@bot.on(Shutdown)
async def Shutdown(event: Shutdown):
    connected.close()


@bot.on(MemberJoinEvent)
async def WelcomeMessage(event: MemberJoinEvent):
    await message.SendWelcomeMessage(event.member.id, event.member.member_name, event.member.group.id,
                                     event.member.group.name)


@bot.on(GroupMessage)
async def MessageRecord(event: GroupMessage):
    logger.info(
        f"[消息]<-{event.group.name}({event.sender.group.id})-{event.sender.member_name}({event.sender.id}):{str(event.message_chain)}")


@Filter(GroupMessage)
def CommandParsing(event: GroupMessage):
    msg = str(event.message_chain)
    if msg.startswith('/') or msg.startswith('!'):
        return msg[1:].rsplit(" ")


@control.on(CommandParsing)
async def CommandSpy(event: GroupMessage, command: list):
    commandLen = len(command)
    targetMessage = event.message_chain.message_id
    per.CreatPlayer(event.sender.id, MainConfig.Permission.default if IsPlayerGroup(event.group.id) else MainConfig.Permission.common)
    if commandLen > 0:
        if ModuleConfig.WhiteList and IsPlayerGroup(event.group.id):
            if command[0] == "apply" or command[0] == "白名单":
                if per.CheckPlayerPermission(event.sender.id, per.Whitelist.Apply):
                    match commandLen:
                        case 1:
                            await message.PlayerMessage("缺少必要参数Token", targetMessage=targetMessage)
                        case 2:
                            token = command[1]
                            tokenLen = len(command[1])
                            if tokenLen > 16:
                                await message.PlayerMessage("Token过长", targetMessage=targetMessage)
                            elif tokenLen < 16:
                                await message.PlayerMessage("Token过短", targetMessage=targetMessage)
                            else:
                                if rematch('^[A-Z]+$', token) is None:
                                    await message.PlayerMessage("Token应为十六位大写字母", targetMessage=targetMessage)
                                else:
                                    await whitelist.GetWhiteList(targetMessage, token, str(event.sender.id))
                else:
                    await message.PlayerMessage("你无权这么做")
            elif command[0] == "change" or command[0] == "改名":
                if per.CheckPlayerPermission(event.sender.id, per.Whitelist.Change):
                    if commandLen == 2:
                        if rematch('^\\w+$', command[1]) is None or len(command[1]) < 4 or len(command[1]) > 16:
                            await message.PlayerMessage("非法玩家名", targetMessage=targetMessage)
                        else:
                            await whitelist.ChangeName(command[1], event.sender.id)
                else:
                    await message.PlayerMessage("你无权这么做")
            elif command[0] == "token":
                if per.CheckPlayerPermission(event.sender.id, per.Token.Check):
                    PingDataBase()
                    if cursor.execute(f"select * from wait where account = {event.sender.id}"):
                        data = cursor.fetchone()
                        await message.PlayerMessage(f"你的token为:\n"
                                                    f"{data[12]}", targetMessage=targetMessage)
                else:
                    await message.PlayerMessage("你无权这么做")
            elif command[0] == "pass" or command[0] == "通过":
                if per.CheckPlayerPermission(event.sender.id, per.Whitelist.Agree):
                    match commandLen:
                        case 1:
                            await message.AdminMessage("命令缺少参数")
                        case 2:
                            await whitelist.PassOne(command[1])
                else:
                    await message.PlayerMessage("你无权这么做")
            elif command[0] == "refuse" or command[0] == "拒绝":
                if per.CheckPlayerPermission(event.sender.id, per.Whitelist.Refuse):
                    match commandLen:
                        case 1:
                            await message.AdminMessage("命令缺少参数")
                        case 3:
                            await whitelist.RefuseOne(command[1])
                        case 4:
                            await whitelist.RefuseOne(command[1], command[2])
                else:
                    await message.PlayerMessage("你无权这么做")
            elif command[0] == "list" or command[0] == "查询":
                if per.CheckPlayerPermission(event.sender.id, per.Whitelist.List.Wait):
                    if commandLen == 2:
                        if command[1] == "wait" or command[1] == "待审核":
                            await Segmentation(message.AdminMessage, query.WaitList())
                else:
                    await message.PlayerMessage("你无权这么做")
            elif command[0] == "lock" or command[0] == "锁定":
                if per.CheckPlayerPermission(event.sender.id, per.Token.Lock):
                    if commandLen == 2:
                        PingDataBase()
                        if cursor.execute(f"SELECT * from wait where token = '{command[1]}'"):
                            data = cursor.fetchone()
                            if not data[16]:
                                try:
                                    cursor.execute(f"UPDATE wait SET locked = 1 where token = '{command[1]}'")
                                    await message.AdminMessage("锁定token成功")
                                except:
                                    await message.AdminMessage("锁定token失败")
                            else:
                                await message.AdminMessage("此token已被上锁")
                        else:
                            await message.AdminMessage("无法找到此Token，请确认Token是否正确")
                else:
                    await message.PlayerMessage("你无权这么做")
            elif command[0] == "unlock" or command[0] == "解锁":
                if per.CheckPlayerPermission(event.sender.id, per.Token.Unlock):
                    if commandLen == 2:
                        PingDataBase()
                        if cursor.execute(f"SELECT * from wait where token = '{command[1]}'"):
                            data = cursor.fetchone()
                            if data[16]:
                                try:
                                    cursor.execute(f"UPDATE wait SET locked = 0 where token = '{command[1]}'")
                                    await message.AdminMessage("解锁成功")
                                except:
                                    await message.AdminMessage("解锁失败")
                            else:
                                await message.AdminMessage("此token未被上锁")
                        else:
                            await message.AdminMessage("无法找到此Token，请确认Token是否正确")
                else:
                    await message.PlayerMessage("你无权这么做")
            elif command[0] == "passall" or command[0] == "全部通过":
                if per.CheckPlayerPermission(event.sender.id, per.Whitelist.AgreeALL):
                    if commandLen == 1:
                        await whitelist.PassAll()
                else:
                    await message.PlayerMessage("你无权这么做")
        elif ModuleConfig.BlackList:
            if command[0] == "blacklist" or command[0] == "黑名单":
                if commandLen == 1:
                    if per.CheckPlayerPermission(event.sender.id, per.Blacklist.List):
                        PingDataBase()
                        number = cursor.execute("select * from blacklist")
                        if number == 0:
                            await message.PlayerMessage("未查询到黑名单玩家", targetMessage=targetMessage)
                        else:
                            tempMessage = ""
                            data = cursor.fetchall()
                            for raw in data:
                                tempMessage += f"序号：{raw[0]}\n玩家名：{raw[2]}\n理由:{raw[6]}\n"
                            await Segmentation(message.PlayerMessage, tempMessage)
                    else:
                        await message.PlayerMessage("你无权这么做")
                elif commandLen == 2:
                    if per.CheckPlayerPermission(event.sender.id, per.Blacklist.Check):
                        if rematch('^\\w+$', command[1]) is None or len(command[1]) < 4 or len(command[1]) > 16:
                            await message.PlayerMessage("非法玩家名", targetMessage=targetMessage)
                        else:
                            PingDataBase()
                            if cursor.execute(f"select * from blacklist where PlayerName = '{command[1]}'"):
                                await message.PlayerMessage("该玩家已被封禁", targetMessage=targetMessage)
                            else:
                                await message.PlayerMessage("该玩家未被封禁", targetMessage=targetMessage)
                    else:
                        await message.PlayerMessage("你无权这么做")
                elif command[0] == "ban" or command[0] == "封禁":
                    if per.CheckPlayerPermission(event.sender.id, per.Blacklist.Add):
                        if commandLen < 2:
                            await message.AdminMessage("缺少参数")
                        elif rematch('^\\w+$', command[1]) is None or len(command[1]) < 4 or len(command[1]) > 16:
                            await message.AdminMessage("非法玩家名")
                        else:
                            match commandLen:
                                case 2:
                                    await blacklist.AddBlackList(command[1])
                                case 3:
                                    await blacklist.AddBlackList(command[1], command[2])
                    else:
                        await message.PlayerMessage("你无权这么做")
                elif command[0] == "unban" or command[0] == "解封":
                    if per.CheckPlayerPermission(event.sender.id, per.Blacklist.Remove):
                        if commandLen < 2:
                            await message.AdminMessage("缺少参数")
                        elif rematch('^\\w+$', command[1]) is None or len(command[1]) < 4 or len(command[1]) > 16:
                            await message.AdminMessage("非法玩家名")
                        else:
                            if commandLen == 2:
                                await blacklist.DelBlackList(command[1])
                    else:
                        await message.PlayerMessage("你无权这么做")

bot.run(port=MainConfig.MiraiBotConfig.WebSocketPort)
