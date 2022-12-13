from module.module_base.sql_relate import cursor
from module.module_interlining.bot import message, interrupt
from mirai.models.events import GroupMessage
from mirai_extensions.trigger import Filter
from module.module_base.logger import logger
from module.module_interlining.useful_tools import is_at_bot, is_admin_group, is_player_group
from mirai.models.message import Plain
from module.module_class.server_class import MinecraftServer
from module.module_interlining.useful_tools import ping_database, judge_token, segmentation_str
from module.module_base.permission import per
from module.module_base.config import main_config


class WhitelistClass():
    _minecraft_server: MinecraftServer

    def __init__(self, server: MinecraftServer) -> None:
        self._minecraft_server = server

    async def pass_one(self, id_: str, output: bool = True) -> None | dict:
        ping_database()
        if await self._judge(id_):
            cursor.execute(f"Select * from wait where id = '{id_}'")
            data = cursor.fetchone()
            try:
                cursor.execute(f"update wait SET pass = 1 where id = '{id_}'")
                cursor.execute(
                    f"INSERT INTO `whitelist` (`id`, `account`, `PlayerName`, `UserSource`, `GameVersion`, `token`) VALUES ({data[0]}, '{data[1]}', '{data[2]}', '{data[3]}', '{data[8]}', '{data[12]}')")
                if data[8] == "BE":
                    await self._minecraft_server.add_whitelist(('BE_' + data[2])[:16])
                else:
                    await self._minecraft_server.add_whitelist(data[2])
                if output:
                    await message.send_admin_message(f"{data[2]}添加白名单成功")
                    await message.send_player_message(f"添加白名单成功", data[1])
                    logger.success(f"{data[2]}添加白名单成功")
                else:
                    await message.send_player_message(f"添加白名单成功", data[1])
                    logger.success(f"{data[2]}添加白名单成功")
                    return {
                        "name": data[2],
                        "status": True
                    }
            except:
                if output:
                    logger.error("发生未知错误")
                    await message.send_admin_message("发生未知错误！")
                else:
                    logger.error("发生未知错误")
                    return {
                        "name": data[2],
                        "status": False
                    }
            else:
                per.set_player_group(data[1], main_config.permission.common)

    async def refuse_one(self, id_: str, reason: str = None) -> None:
        ping_database()
        if await self._judge(id_):
            cursor.execute(f"select * from wait where id = '{id_}'")
            data = cursor.fetchone()
            try:
                cursor.execute(f"update wait set pass = 0 where id = '{id_}'")
                cursor.execute(f"update wait set passinfo = '{reason}' where id = '{id_}'")
                await message.send_admin_message("成功拒绝白名单")
                if reason is None:
                    await message.send_player_message("您的白名单申请被管理组拒绝", data[1])
                else:
                    await message.send_player_message(f"您的白名单申请被管理组拒绝, 理由:{reason}", data[1])
                logger.success(f"{data[2]}拒绝白名单成功")
            except:
                logger.error("发生未知错误")
                await message.send_admin_message("发生未知错误！")

    async def pass_all(self) -> None:
        ping_database()
        if cursor.execute("select * from wait where pass is null and used is true and locked is not true"):
            msg: str = ""
            data = cursor.fetchall()
            for raw in data:
                msg += f"序号: {raw[0]}\n玩家名: {raw[2]}\n"
            await segmentation_str(message.send_admin_message, msg)
            await message.send_admin_message("即将通过以上玩家的白名单申请，是否继续？(是/否)")

            @Filter(GroupMessage)
            def wait_commit(tempMsg: GroupMessage):
                if tempMsg.message_chain.has(Plain):
                    if "是" in tempMsg.message_chain.get_first(Plain).text:
                        return 1
                    elif "否" in tempMsg.message_chain.get_first(Plain).text:
                        return 2

            match await interrupt.wait(wait_commit, timeout=300):
                case 1:
                    success: str = ""
                    fail: str = ""
                    for raw in data:
                        respond = await self.pass_one(raw[0], False)
                        if respond["status"]:
                            success += f"[{respond['name']}]"
                        else:
                            fail += f"[{respond['name']}]"
                    await message.send_admin_message(f"成功: \n{success}\n"
                                                     f"失败: \n{fail}")
                case 2:
                    await message.send_admin_message("操作已取消")
        else:
            await message.send_admin_message("待审核列表为空~")

    async def change_name(self, new_name: str, account: str) -> None:
        ping_database()
        if cursor.execute(f"select * from wait where account = {account}"):
            data = cursor.fetchone()
            if data[2] == new_name:
                await message.send_player_message("要修改的名字与原名相同")
            elif cursor.execute(f"select * from usedname where PlayerName = '{new_name}'"):
                await message.send_player_message(f"{new_name}已被使用过了")
            elif cursor.execute(f"select * from wait where PlayerName = '{new_name}'"):
                await message.send_player_message(f"{new_name}已被他人绑定")
            else:
                match data[8]:
                    case "Java":
                        await message.send_player_message(f"正在进行改名操作：{data[2]} -> {new_name}\n"
                                                          f"确认无误后@机器人并回复确认")
                    case "BE":
                        await message.send_player_message(
                            f"正在进行改名操作：{('BE_' + data[2])[:16]} -> {('BE_' + new_name)[:16]}\n"
                            f"确认无误后@机器人并回复确认")

                @Filter(GroupMessage)
                def wait_commit_player(msg: GroupMessage):
                    if msg.message_chain.has(Plain):
                        if is_at_bot(msg.message_chain) and \
                                msg.sender.id == account and "确认" in msg.message_chain.get_first(Plain).text \
                                and is_player_group(msg.group.id):
                            return True

                if await interrupt.wait(wait_commit_player):
                    await message.send_admin_message(f"有一个正在进行的改名操作：{data[2]} -> {new_name}\n"
                                                     f"是否同意？(是/否)")

                    @Filter(GroupMessage)
                    def wait_commit_admin(msg: GroupMessage):
                        if msg.message_chain.has(Plain):
                            if is_admin_group(msg.group.id):
                                if "是" == msg.message_chain.get_first(Plain).text:
                                    return 1
                                elif "否" == msg.message_chain.get_first(Plain).text:
                                    return 2

                    match await interrupt.wait(wait_commit_admin):
                        case 1:
                            try:
                                match data[8]:
                                    case "BE":
                                        await self._minecraft_server.server_run_command(
                                            f"kick {('BE_' + data[2])[:16]}")
                                        await self._minecraft_server.server_run_command(f"ban {('BE_' + data[2])[:16]}")
                                        await self._minecraft_server.del_whitelist(('BE_' + data[2])[:16])
                                        await self._minecraft_server.add_whitelist(('BE_' + new_name)[:16])
                                        cursor.execute(
                                            f"INSERT INTO `usedname` (`PlayerName`, `account`) values ('{data[2]}', '{account}')")
                                        cursor.execute(
                                            f"update wait set PlayerName = '{new_name}' where account = '{account}'")
                                    case "Java":
                                        await self._minecraft_server.server_run_command(f"kick {data[2]}")
                                        await self._minecraft_server.server_run_command(f"ban {data[2]}")
                                        await self._minecraft_server.del_whitelist(data[2])
                                        await self._minecraft_server.add_whitelist(new_name)
                                        cursor.execute(
                                            f"INSERT INTO `usedname` (`PlayerName`, `account`) values ('{data[2]}', '{account}')")
                                        cursor.execute(
                                            f"update wait set PlayerName = '{new_name}' where account = '{account}'")
                                await message.send_player_message(f"改名成功", account)
                                await message.send_admin_message("改名成功")
                            except:
                                await message.send_player_message("改名失败", account)
                                await message.send_admin_message("改名发生错误")
                        case 2:
                            await message.send_admin_message("成功拒绝改名")
                            await message.send_player_message("改名申请被管理组拒绝", account)
        else:
            await message.send_player_message("您的账户下未绑定角色", account)

    @staticmethod
    async def _judge(id_: str) -> bool:
        respond = judge_token(int(id_))
        match respond["status"]:
            case False:
                logger.error(respond["info"])
                await message.send_admin_message(f"{respond['info']}")
                return False
            case True:
                return True

    @staticmethod
    async def get_whitelist(target_message: str, token: str, QQ: str) -> None:
        ping_database()
        if cursor.execute(f"select * from blacklist where token = '{token}'"):
            await message.send_player_message("此token已被列入黑名单")
        elif cursor.execute(f"SELECT * from wait where token = '{token}'"):
            data = cursor.fetchone()
            if data[16]:
                await message.send_player_message("此token已被锁定，请联系管理员", target_message=target_message)
            else:
                match data[3]:
                    case "KOOK":
                        await message.send_player_message(
                            "此token记录的平台为KOOK，请前往KOOK频道申请\nhttps://kook.top/DgVnJN",
                            target_message=target_message)
                    case "QQ":
                        if data[1] != QQ:
                            await message.send_player_message("此token不属于你！请不要尝试使用他人的Token！此token已被锁定",
                                                              target_message=target_message)
                            cursor.execute(f"UPDATE wait SET locked = 1 where token = '{token}'")
                        else:
                            if data[15]:
                                if data[17] is None:
                                    await message.send_player_message("您的白名单申请正在审核中，请耐心等待",
                                                                      target_message=target_message)
                                elif data[17]:
                                    await message.send_player_message("您已拥有白名单权限",
                                                                      target_message=target_message)
                                else:
                                    await message.send_player_message(f"您的白名单申请被管理组拒绝\n原因：{data[18]}",
                                                                      target_message=target_message)
                            else:
                                await message.send_player_message("请确认您的游戏名及游戏版本:\n"
                                                                  f"游戏名:{data[2][:16] if data[8] == 'Java' else ('BE_'+data[2][:16])}\n"
                                                                  f"游戏版本:{data[8]}\n"
                                                                  f"确认无误后请@机器人并回复\"确认\"",
                                                                  target_message=target_message)
                                # match data[8]:
                                    # case "Java":
                                    #     await message.send_player_message("请确认您的游戏名及游戏版本:\n"
                                    #                                       f"游戏名:{data[2][:16]}\n"
                                    #                                       f"游戏版本:{data[8]}\n"
                                    #                                       f"确认无误后请@机器人并回复\"确认\"",
                                    #                                       target_message=target_message)
                                    # case "BE":
                                    #     await message.send_player_message("请确认您的游戏名及游戏版本:\n"
                                    #                                       f"游戏名:{('BE_' + data[2])[:16]}\n"
                                    #                                       f"游戏版本:{data[8]}\n"
                                    #                                       f"确认无误后请@机器人并回复\"确认\"",
                                    #                                       target_message=target_message)

                                @Filter(GroupMessage)
                                def wait_commit(msg: GroupMessage):
                                    if msg.message_chain.has(Plain):
                                        if is_at_bot(msg.message_chain) and str(
                                                msg.sender.id) == QQ and "确认" in msg.message_chain.get_first(
                                            Plain).text and is_player_group(msg.group.id):
                                            return True

                                if await interrupt.wait(wait_commit, timeout=300):
                                    await message.send_player_message("白名单申请已提交至管理组审核，请耐心等待",
                                                                      target_message=target_message)
                                    cursor.execute(f"UPDATE wait SET used = 1 where token = '{token}'")
                                    await message.send_admin_message("收到一条新的白名单申请:\n"
                                                                     f"审核序号:{data[0]}\n"
                                                                     f"游戏名:{data[2][:16]}\n"
                                                                     f"游戏版本:{data[8]}\n"
                                                                     f"答题分数:{data[13]}\n"
                                                                     f"Token:{token}\n"
                                                                     f"个人简介:\n"
                                                                     f"{data[9]}\n"
                                                                     f"输入/pass {data[0]}以通过该请求")
        else:
            await message.send_player_message("未能找到此Token，请检查是否正确", target_message=target_message)
