from module.BasicModule.Permission import per
from module.Interlining.Bot import bot, message
from mirai.models.events import GroupMessage
from mirai.models.message import At
from module.Interlining.UsefulTools import Segmentation


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

