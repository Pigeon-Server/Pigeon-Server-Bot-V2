from module.module_base.permission import per
from module.module_interlining.bot import bot, message
from mirai.models.events import GroupMessage
from mirai.models.message import At
from module.module_interlining.useful_tools import segmentation_str


@bot.on(GroupMessage)
async def permission(event: GroupMessage):
    async def send(sendMessage: str) -> None:
        await message.send_message(event.group.id, sendMessage, event.group.name)

    def check_player(permission_: str) -> bool:
        return per.check_player_permission(str(event.sender.id), permission_)

    msg = str(event.message_chain)
    if msg.startswith('/permission') or msg.startswith('!permission') or msg.startswith('/ps') or msg.startswith('!ps'):
        command = msg[1:].rsplit(" ")
        command_len = len(command)
        if command_len == 1:
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
                if command_len >= 4:
                    match len(event.message_chain.get(At)):
                        case 2:
                            if command[3] == "clone":
                                if check_player(per.Permission.Player.Clone):
                                    temp = event.message_chain.get(At)
                                    await send(per.clone_player_permission(str(temp[1].target), str(temp[0].target)))
                                else:
                                    await send("你无权这么做")
                        case 1:
                            match command[3]:
                                case "add":
                                    if check_player(per.Permission.Player.Give):
                                        if command_len == 5:
                                            await send(per.add_player_permission(str(event.message_chain.get_first(At).target), command[4]))
                                        else:
                                            await send("命令参数不正确")
                                    else:
                                        await send("你无权这么做")
                                case "remove":
                                    if check_player(per.Permission.Player.Remove):
                                        if command_len == 5:
                                            await send(per.remove_player_permission(str(event.message_chain.get_first(At).target), command[4]))
                                        else:
                                            await send("命令参数不正确")
                                    else:
                                        await send("你无权这么做")
                                case "check":
                                    if check_player(per.Permission.Player.Check):
                                        if command_len == 5:
                                            await send(per.check_player_permission(str(event.message_chain.get_first(At).target), command[4]))
                                        else:
                                            await send("命令参数不正确")
                                    else:
                                        await send("你无权这么做")
                                case "list":
                                    if check_player(per.Permission.Player.List):
                                        msg = f"{event.message_chain.get_first(At).target}拥有的权限为：\n"
                                        for raw in per.get_player_permission(str(event.message_chain.get_first(At).target)):
                                            msg += f"{raw}\n"
                                        await send(msg.removesuffix("\n"))
                                    else:
                                        await send("你无权这么做")
                                case "info":
                                    if check_player(per.Permission.Player.Info):
                                        data = per.get_player_info(str(event.message_chain.get_first(At).target))
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
                                    if check_player(per.Permission.Player.Create):
                                        if command_len == 4:
                                            await send(per.creat_player(str(event.message_chain.get_first(At).target)))
                                        elif command_len == 5:
                                            await send(per.creat_player(str(event.message_chain.get_first(At).target), command[4]))
                                        else:
                                            await send("命令参数不正确")
                                    else:
                                        await send("你无权这么做")
                                case "inherit":
                                    if command_len >= 6:
                                        match command[4]:
                                            case "add":
                                                if check_player(per.Permission.Player.Inherit.Add):
                                                    await send(per.add_player_parent(str(event.message_chain.get_first(At).target), command[5]))
                                                else:
                                                    await send("你无权这么做")
                                            case "remove":
                                                if check_player(per.Permission.Player.Inherit.delete):
                                                    await send(per.remove_player_parent(str(event.message_chain.get_first(At).target), command[5]))
                                                else:
                                                    await send("你无权这么做")
                                            case "set":
                                                if check_player(per.Permission.Player.Inherit.Set):
                                                    if command_len == 6:
                                                        await send(per.set_player_group(str(event.message_chain.get_first(At).target), command[5]))
                                                    elif command_len > 6:
                                                        temp = []
                                                        for x in range(6, command_len):
                                                            temp += x
                                                        await send(per.set_player_group(str(event.message_chain.get_first(At).target), temp))
                                                else:
                                                    await send("你无权这么做")
                                    else:
                                        await send("命令参数不正确")
                        case 0:
                            match command[3]:
                                case "add":
                                    if check_player(per.Permission.Player.Give):
                                        if command_len == 5:
                                            await send(per.add_player_permission(command[2], command[4]))
                                        else:
                                            await send("命令参数错误")
                                    else:
                                        await send("你无权这么做")
                                case "remove":
                                    if check_player(per.Permission.Player.Remove):
                                        if command_len == 5:
                                            await send(per.remove_player_permission(command[2], command[4]))
                                        else:
                                            await send("命令参数错误")
                                    else:
                                        await send("你无权这么做")
                                case "check":
                                    if check_player(per.Permission.Player.Check):
                                        if command_len == 5:
                                            await send(per.check_player_permission(command[2], command[4]))
                                        else:
                                            await send("命令参数错误")
                                    else:
                                        await send("你无权这么做")
                                case "clone":
                                    if check_player(per.Permission.Player.Clone):
                                        if command_len == 5:
                                            await send(per.clone_player_permission(command[2], command[4]))
                                        else:
                                            await send("命令参数错误")
                                    else:
                                        await send("你无权这么做")
                                case "list":
                                    if check_player(per.Permission.Player.List):
                                        msg = f"{command[2]}拥有的权限为：\n"
                                        for raw in per.get_player_permission(command[2]):
                                            msg += f"{raw}\n"
                                        await send(msg.removesuffix("\n"))
                                    else:
                                        await send("你无权这么做")
                                case "info":
                                    if check_player(per.Permission.Player.Info):
                                        data = per.get_player_info(command[2])
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
                                    if check_player(per.Permission.Player.Create):
                                        if command_len == 4:
                                            await send(per.creat_player(command[3]))
                                        elif command_len == 5:
                                            await send(per.creat_player(command[3], command[4]))
                                        else:
                                            await send("命令参数不正确")
                                    else:
                                        await send("你无权这么做")
                                case "inherit":
                                    if command_len >= 6:
                                        match command[4]:
                                            case "add":
                                                if check_player(per.Permission.Player.Inherit.Add):
                                                    await send(per.add_player_parent(command[2], command[5]))
                                                else:
                                                    await send("你无权这么做")
                                            case "remove":
                                                if check_player(per.Permission.Player.Inherit.delete):
                                                    await send(per.remove_player_parent(command[2], command[5]))
                                                else:
                                                    await send("你无权这么做")
                                            case "set":
                                                if check_player(per.Permission.Player.Inherit.Set):
                                                    if command_len == 6:
                                                        await send(per.set_player_group(command[2], command[5]))
                                                    elif command_len > 6:
                                                        temp = []
                                                        for x in range(6, command_len):
                                                            temp += x
                                                        await send(per.set_player_group(command[2], temp))
                                                else:
                                                    await send("你无权这么做")
                                    else:
                                        await send("命令参数不正确")
                else:
                    await send("命令缺少参数")
            elif command[1] == "group":
                if command_len >= 4:
                    match command[3]:
                        case "add":
                            if check_player(per.Permission.Group.Give):
                                if command_len == 5:
                                    await send(per.add_group_permission(command[2]))
                                else:
                                    await send("命令参数错误")
                            else:
                                await send("你无权这么做")
                        case "remove":
                            if check_player(per.Permission.Group.delete):
                                if command_len == 5:
                                    await send(per.reload_group_permission(command[2]))
                                else:
                                    await send("命令参数错误")
                            else:
                                await send("你无权这么做")
                        case "check":
                            if check_player(per.Permission.Group.Check):
                                if command_len == 5:
                                    await send(per.check_group_permission(command[2]))
                                else:
                                    await send("命令参数错误")
                            else:
                                await send("你无权这么做")
                        case "clone":
                            if check_player(per.Permission.Group.Clone):
                                if command_len == 5:
                                    await send(per.clone_group_permission(command[2], command[4]))
                                else:
                                    await send("命令参数错误")
                            else:
                                await send("你无权这么做")
                        case "list":
                            if check_player(per.Permission.Group.List):
                                msg = f"{command[2]}拥有的权限为：\n"
                                for raw in per.get_group_permission(command[2]):
                                    msg += f"{raw}\n"
                                await send(msg.removesuffix("\n"))
                            else:
                                await send("你无权这么做")
                        case "info":
                            if check_player(per.Permission.Group.Info):
                                data = per.get_group_info(command[2])
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
                            if check_player(per.Permission.Group.Create):
                                if command_len == 4:
                                    await send(per.creat_group(command[3]))
                                else:
                                    await send("命令参数不正确")
                            else:
                                await send("你无权这么做")
                        case "inherit":
                            if command_len == 6:
                                match command[4]:
                                    case "add":
                                        if check_player(per.Permission.Group.Inherit.Add):
                                            await send(per.add_group_parent(command[2], command[5]))
                                        else:
                                            await send("你无权这么做")
                                    case "remove":
                                        if check_player(per.Permission.Group.Inherit.delete):
                                            await send(per.remove_group_parent(command[2], command[5]))
                                        else:
                                            await send("你无权这么做")
                            else:
                                await send("命令参数不正确")
            elif command[1] == "list":
                if check_player(per.Permission.ShowList):
                    if command_len == 2:
                        data = per.get_permission_node()
                        msg = "所有权限节点: \n"
                        for raw in data:
                            msg += f"{raw}\n"
                    elif command_len == 3:
                        data = per.get_permission_node()
                        msg = f"{command[2]}权限节点: \n"
                        for raw in data:
                            if command[2] in raw:
                                msg += f"{raw}\n"
                        await segmentation_str(send, msg)
                else:
                    await send("你无权这么做")
            elif command[1] == "reload":
                if command_len == 2:
                    if check_player(per.Permission.Reload.Common):
                        await send(per.reload_group_permission())
                    else:
                        await send("你无权这么做")
                elif command_len == 3 and command[2] == "true":
                    if check_player(per.Permission.Reload.Force):
                        await send(per.reload_group_permission(True))
                    else:
                        await send("你无权这么做")
