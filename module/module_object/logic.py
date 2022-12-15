from module.module_interlining.bot import message, control
from mirai.models.events import GroupMessage
from mirai_extensions.trigger import Filter
from module.module_base.config import main_config, module_config
from module.module_interlining.useful_tools import is_player_group, ping_database, segmentation_str
from module.module_base.permission import per
from re import match as rematch
from module.module_base.sql_relate import cursor

if module_config.white_list:
    from module.module_interlining.objectification import query, whitelist
if module_config.black_list:
    from module.module_interlining.objectification import blacklist


@Filter(GroupMessage)
def command_parsing(event: GroupMessage):
    msg = str(event.message_chain)
    if msg.startswith('/') or msg.startswith('!'):
        return msg[1:].rsplit(" ")


@control.on(command_parsing)
async def command_spy(event: GroupMessage, command: list):

    async def send(msg, target=None):
        if target is not None:
            await message.send_message(event.group.id, msg, event.group.name, target)
        else:
            await message.send_message(event.group.id, msg, event.group.name)

    commandLen = len(command)
    targetMessage = event.message_chain.message_id
    per.creat_player(str(event.sender.id), main_config.permission.default if is_player_group(event.group.id) else main_config.permission.common)
    if commandLen > 0:
        if module_config.white_list:
            if not is_player_group(event.group.id):
                await send(f"请前往原版群({main_config.mirai_bot_config.group_config.player_group})查看！")
            elif command[0] == "apply" or command[0] == "白名单":
                if per.check_player_permission(event.sender.id, per.Whitelist.Apply):
                    match commandLen:
                        case 1:
                            await send("缺少必要参数Token", targetMessage)
                        case 2:
                            token = command[1]
                            tokenLen = len(command[1])
                            if tokenLen > 16:
                                await send("Token过长", targetMessage)
                            elif tokenLen < 16:
                                await send("Token过短", targetMessage)
                            else:
                                if rematch('^[A-Z]+$', token) is None:
                                    await send("Token应为十六位大写字母", targetMessage)
                                else:
                                    await whitelist.get_whitelist(targetMessage, token, str(event.sender.id))
                else:
                    await send("你无权这么做")
                return
            elif command[0] == "change" or command[0] == "改名":
                if per.check_player_permission(event.sender.id, per.Whitelist.Change):
                    if commandLen == 2:
                        if rematch('^\\w+$', command[1]) is None or len(command[1]) < 4 or len(command[1]) > 16:
                            await send("非法玩家名", targetMessage)
                        else:
                            await whitelist.change_name(command[1], event.sender.id)
                else:
                    await send("你无权这么做")
                return
            elif command[0] == "token":
                if per.check_player_permission(event.sender.id, per.Token.Check):
                    ping_database()
                    if cursor.execute(f"select * from wait where account = {event.sender.id}"):
                        data = cursor.fetchone()
                        await send(f"你的token为:\n"
                                                    f"{data[12]}", targetMessage)
                else:
                    await send("你无权这么做")
                return
            elif command[0] == "pass" or command[0] == "通过":
                if per.check_player_permission(event.sender.id, per.Whitelist.Agree):
                    match commandLen:
                        case 1:
                            await send("命令缺少参数")
                        case 2:
                            await whitelist.pass_one(command[1])
                else:
                    await send("你无权这么做")
                return
            elif command[0] == "refuse" or command[0] == "拒绝":
                if per.check_player_permission(event.sender.id, per.Whitelist.Refuse):
                    match commandLen:
                        case 1:
                            await send("命令缺少参数")
                        case 3:
                            await whitelist.refuse_one(command[1])
                        case 4:
                            await whitelist.refuse_one(command[1], command[2])
                else:
                    await send("你无权这么做")
                return
            elif command[0] == "list" or command[0] == "查询":
                if per.check_player_permission(event.sender.id, per.Whitelist.List.Wait):
                    if commandLen == 2:
                        if command[1] == "wait" or command[1] == "待审核":
                            await segmentation_str(send, query.get_wait_list())
                else:
                    await send("你无权这么做")
                return
            elif command[0] == "lock" or command[0] == "锁定":
                if per.check_player_permission(event.sender.id, per.Token.Lock):
                    if commandLen == 2:
                        ping_database()
                        if cursor.execute(f"SELECT * from wait where token = '{command[1]}'"):
                            data = cursor.fetchone()
                            if not data[16]:
                                try:
                                    cursor.execute(f"UPDATE wait SET locked = 1 where token = '{command[1]}'")
                                    await send("锁定token成功")
                                except:
                                    await send("锁定token失败")
                            else:
                                await send("此token已被上锁")
                        else:
                            await send("无法找到此Token，请确认Token是否正确")
                else:
                    await send("你无权这么做")
                return
            elif command[0] == "unlock" or command[0] == "解锁":
                if per.check_player_permission(event.sender.id, per.Token.Unlock):
                    if commandLen == 2:
                        ping_database()
                        if cursor.execute(f"SELECT * from wait where token = '{command[1]}'"):
                            data = cursor.fetchone()
                            if data[16]:
                                try:
                                    cursor.execute(f"UPDATE wait SET locked = 0 where token = '{command[1]}'")
                                    await send("解锁成功")
                                except:
                                    await send("解锁失败")
                            else:
                                await send("此token未被上锁")
                        else:
                            await send("无法找到此Token，请确认Token是否正确")
                else:
                    await send("你无权这么做")
                return
            elif command[0] == "passall" or command[0] == "全部通过":
                if per.check_player_permission(event.sender.id, per.Whitelist.AgreeALL):
                    if commandLen == 1:
                        await whitelist.pass_all()
                else:
                    await send("你无权这么做")
                return
        if module_config.black_list:
            if not is_player_group(event.group.id):
                await send(f"请前往原版群({main_config.mirai_bot_config.group_config.player_group})申请！")
            elif command[0] == "blacklist" or command[0] == "黑名单":
                if commandLen == 1:
                    if per.check_player_permission(event.sender.id, per.Blacklist.List):
                        ping_database()
                        number = cursor.execute("select * from blacklist")
                        if number == 0:
                            await send("未查询到黑名单玩家", targetMessage)
                        else:
                            tempMessage = ""
                            data = cursor.fetchall()
                            for raw in data:
                                tempMessage += f"序号：{raw[0]}\n玩家名：{raw[2]}\n理由:{raw[6]}\n"
                            await segmentation_str(send, tempMessage)
                    else:
                        await send("你无权这么做")
                    return
                elif commandLen == 2:
                    if per.check_player_permission(event.sender.id, per.Blacklist.Check):
                        if rematch('^\\w+$', command[1]) is None or len(command[1]) < 4 or len(command[1]) > 16:
                            await send("非法玩家名", targetMessage)
                        else:
                            ping_database()
                            if cursor.execute(f"select * from blacklist where PlayerName = '{command[1]}'"):
                                await send("该玩家已被封禁", targetMessage)
                            else:
                                await send("该玩家未被封禁", targetMessage)
                    else:
                        await send("你无权这么做")
                    return
                elif command[1] == "ban" or command[1] == "封禁":
                    if per.check_player_permission(event.sender.id, per.Blacklist.Add):
                        if commandLen < 3:
                            await send("缺少参数")
                        elif rematch('^\\w+$', command[2]) is None or len(command[2]) < 4 or len(command[2]) > 16:
                            await send("非法玩家名")
                        else:
                            match commandLen:
                                case 3:
                                    await blacklist.add_black_list(command[2])
                                case 4:
                                    await blacklist.add_black_list(command[2], command[3])
                    else:
                        await send("你无权这么做")
                    return
                elif command[1] == "unban" or command[1] == "解封":
                    if per.check_player_permission(event.sender.id, per.Blacklist.Remove):
                        if commandLen < 3:
                            await send("缺少参数")
                        elif rematch('^\\w+$', command[2]) is None or len(command[2]) < 4 or len(command[2]) > 16:
                            await send("非法玩家名")
                        else:
                            if commandLen == 3:
                                await blacklist.del_blacklist(command[2])
                    else:
                        await send("你无权这么做")
                    return
