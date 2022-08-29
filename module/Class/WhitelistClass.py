from module.BasicModule.SqlRelate import cursor
from module.Interlining.Bot import message, interrupt
from mirai.models.events import GroupMessage
from mirai_extensions.trigger import Filter
from module.BasicModule.Logger import logger
from module.Interlining.UsefulTools import IsAtBot, IsAdminGroup, IsPlayerGroup
from mirai.models.message import Plain
from module.Class.ServerClass import MinecraftServer
from module.Interlining.UsefulTools import PingDataBase, JudgeToken, Segmentation

class WhitelistClass:

    __MinecraftServer: MinecraftServer

    def __init__(self, server: MinecraftServer) -> None:
        self.__MinecraftServer = server

    async def PassOne(self, id: str, output: bool = True) -> None | dict:
        PingDataBase()
        if await self.__Judge(id):
            cursor.execute(f"Select * from wait where id = '{id}'")
            data = cursor.fetchone()
            try:
                cursor.execute(f"update wait SET pass = 1 where id = '{id}'")
                cursor.execute(f"INSERT INTO `whitelist` (`id`, `account`, `PlayerName`, `UserSource`, `GameVersion`, `token`) VALUES ({data[0]}, '{data[1]}', '{data[2]}', '{data[3]}', '{data[8]}', '{data[12]}')")
                if data[8] == "BE":
                    await self.__MinecraftServer.AddWhitelist(('BE_' + data[2])[:16])
                else:
                    await self.__MinecraftServer.AddWhitelist(data[2])
                if output:
                    await message.AdminMessage(f"{data[2]}添加白名单成功")
                    await message.PlayerMessage(f"添加白名单成功", data[1])
                    logger.success(f"{data[2]}添加白名单成功")
                else:
                    await message.PlayerMessage(f"添加白名单成功", data[1])
                    logger.success(f"{data[2]}添加白名单成功")
                    return {
                        "name": data[2],
                        "status": True
                    }
            except:
                if output:
                    logger.error("发生未知错误")
                    await message.AdminMessage("发生未知错误！")
                else:
                    logger.error("发生未知错误")
                    return {
                        "name": data[2],
                        "status": False
                    }

    async def RefuseOne(self, id: str, reason: str = None) -> None:
        PingDataBase()
        if await self.__Judge(id):
            cursor.execute(f"select * from wait where id = '{id}'")
            data = cursor.fetchone()
            try:
                cursor.execute(f"update wait set pass = 0 where id = '{id}'")
                cursor.execute(f"update wait set passinfo = '{reason}' where id = '{id}'")
                await message.AdminMessage("成功拒绝白名单")
                if reason is None:
                    await message.PlayerMessage("白名单申请被管理组拒绝", data[1])
                else:
                    await message.PlayerMessage(f"白名单申请被管理组拒绝, 理由:{reason}", data[1])
                logger.success(f"{data[2]}拒绝白名单成功")
            except:
                logger.error("发生未知错误")
                await message.AdminMessage("发生未知错误！")

    async def PassAll(self) -> None:
        PingDataBase()
        if cursor.execute("select * from wait where pass is null and used is true and locked is not true"):
            msg: str = ""
            data = cursor.fetchall()
            for raw in data:
                msg += f"序号: {raw[0]}\n玩家名: {raw[2]}\n"
            await Segmentation(message.AdminMessage, msg)
            await message.AdminMessage("即将通过以上玩家的白名单申请，是否继续？(是/否)")

            @Filter(GroupMessage)
            def WaitCommit(tempMsg: GroupMessage):
                if tempMsg.message_chain.has(Plain):
                    if "是" in tempMsg.message_chain.get_first(Plain).text:
                        return 1
                    elif "否" in tempMsg.message_chain.get_first(Plain).text:
                        return 2

            match await interrupt.wait(WaitCommit, timeout=300):
                case 1:
                    success: str = ""
                    fail: str = ""
                    for raw in data:
                        respond = await self.PassOne(raw[0], False)
                        if respond["status"]:
                            success += f"[{respond['name']}]"
                        else:
                            fail += f"[{respond['name']}]"
                    await message.AdminMessage(f"成功: \n{success}\n"
                                               f"失败: \n{fail}")
                case 2:
                    await message.AdminMessage("操作已取消")
        else:
            await message.AdminMessage("未查询到待审核玩家")

    async def ChangeName(self, newName: str, account: str) -> None:
        PingDataBase()
        if cursor.execute(f"select * from wait where account = {account}"):
            data = cursor.fetchone()
            if data[2] == newName:
                await message.PlayerMessage("要修改的名字与原来相同")
            elif cursor.execute(f"select * from usedname where PlayerName = '{newName}'"):
                await message.PlayerMessage("此名称已被使用过了")
            elif cursor.execute(f"select * from wait where PlayerName = '{newName}'"):
                await message.PlayerMessage("此名称已被占用")
            else:
                match data[8]:
                    case "Java":
                        await message.PlayerMessage(f"正在进行改名操作：{data[2]} -> {newName}\n"
                                                    f"确认无误后@机器人并回复确认")
                    case "BE":
                        await message.PlayerMessage(f"正在进行改名操作：{('BE_' + data[2])[:16]} -> {('BE_' + newName)[:16]}\n"
                                                    f"确认无误后@机器人并回复确认")

                @Filter(GroupMessage)
                def WaitCommitPlayer(msg: GroupMessage):
                    if msg.message_chain.has(Plain):
                        if IsAtBot(
                                msg.message_chain) and msg.sender.id == account and "确认" in msg.message_chain.get_first(
                                Plain).text and IsPlayerGroup(msg.group.id):
                            return True

                if await interrupt.wait(WaitCommitPlayer):
                    await message.AdminMessage(f"玩家{data[2]}正在改名\n"
                                               f"新的玩家名为: {newName}\n"
                                               f"是否同意？(是/否)")

                    @Filter(GroupMessage)
                    def WaitCommitAdmin(msg: GroupMessage):
                        if msg.message_chain.has(Plain):
                            if IsAdminGroup(msg.group.id):
                                if "是" in msg.message_chain.get_first(Plain).text:
                                    return 1
                                elif "否" in msg.message_chain.get_first(Plain).text:
                                    return 2

                    match await interrupt.wait(WaitCommitAdmin):
                        case 1:
                            try:
                                match data[8]:
                                    case "BE":
                                        await self.__MinecraftServer.ServerRunCommand(f"kick {('BE_' + data[2])[:16]}")
                                        await self.__MinecraftServer.ServerRunCommand(f"ban {('BE_' + data[2])[:16]}")
                                        await self.__MinecraftServer.DelWhitelist(('BE_' + data[2])[:16])
                                        await self.__MinecraftServer.AddWhitelist(('BE_' + newName)[:16])
                                        cursor.execute(f"INSERT INTO `usedname` (`PlayerName`, `account`) values ('{data[2]}', '{account}')")
                                        cursor.execute(
                                            f"update wait set PlayerName = '{newName}' where account = '{account}'")
                                    case "Java":
                                        await self.__MinecraftServer.ServerRunCommand(f"kick {data[2]}")
                                        await self.__MinecraftServer.ServerRunCommand(f"ban {data[2]}")
                                        await self.__MinecraftServer.DelWhitelist(data[2])
                                        await self.__MinecraftServer.AddWhitelist(newName)
                                        cursor.execute(
                                            f"INSERT INTO `usedname` (`PlayerName`, `account`) values ('{data[2]}', '{account}')")
                                        cursor.execute(
                                            f"update wait set PlayerName = '{newName}' where account = '{account}'")
                                await message.PlayerMessage(f"改名成功", account)
                                await message.AdminMessage("改名成功")
                            except:
                                await message.PlayerMessage("改名失败", account)
                                await message.AdminMessage("改名发生错误")
                        case 2:
                            await message.AdminMessage("成功拒绝改名")
                            await message.PlayerMessage("改名申请被管理组拒绝", account)
        else:
            await message.PlayerMessage("你的账户下没有查询到角色", account)

    @staticmethod
    async def __Judge(id: str) -> bool:
        respond = JudgeToken(id)
        match respond["status"]:
            case False:
                logger.error(respond["info"])
                await message.AdminMessage(f"{respond['info']}")
                return False
            case True:
                return True

    @staticmethod
    async def GetWhitelist(targetMessage: str, token: str, QQ: str) -> None:
        PingDataBase()
        if cursor.execute(f"select * from blacklist where token = '{token}'"):
            await message.PlayerMessage("此token已被列入黑名单")
        elif cursor.execute(f"SELECT * from wait where token = '{token}'"):
            data = cursor.fetchone()
            if data[16]:
                await message.PlayerMessage("此token已被锁定，请联系管理员", targetMessage=targetMessage)
            else:
                match data[3]:
                    case "KOOK":
                        await message.PlayerMessage("此token记录的平台为KOOK，请前往KOOK频道申请\nhttps://kook.top/DgVnJN",
                                                    targetMessage=targetMessage)
                    case "QQ":
                        if data[1] != QQ:
                            await message.PlayerMessage("此token不属于你！请不要使用他人的Token！此token已被锁定",
                                                        targetMessage=targetMessage)
                            cursor.execute(f"UPDATE wait SET locked = 1 where token = '{token}'")
                        else:
                            if data[15]:
                                if data[17] is None:
                                    await message.PlayerMessage("您的白名单申请正在审核中，请耐心等待",
                                                                targetMessage=targetMessage)
                                elif data[17]:
                                    await message.PlayerMessage("您已获取过白名单",
                                                                targetMessage=targetMessage)
                                else:
                                    await message.PlayerMessage(f"您的白名单申请被管理组拒绝\n原因：{data[18]}",
                                                                targetMessage=targetMessage)
                            else:
                                match data[8]:
                                    case "Java":
                                        await message.PlayerMessage("请确认您的游戏名及游戏版本:\n"
                                                                    f"游戏名:{data[2][:16]}\n"
                                                                    f"游戏版本:{data[8]}\n"
                                                                    f"确认无误后请@机器人并回复\"确认\"",
                                                                    targetMessage=targetMessage)
                                    case "BE":
                                        await message.PlayerMessage("请确认您的游戏名及游戏版本:\n"
                                                                    f"游戏名:{('BE_' + data[2])[:16]}\n"
                                                                    f"游戏版本:{data[8]}\n"
                                                                    f"确认无误后请@机器人并回复\"确认\"",
                                                                    targetMessage=targetMessage)

                                @Filter(GroupMessage)
                                def WaitCommit(msg: GroupMessage):
                                    if msg.message_chain.has(Plain):
                                        if IsAtBot(msg.message_chain) and str(msg.sender.id) == QQ and "确认" in msg.message_chain.get_first(Plain).text and IsPlayerGroup(msg.group.id):
                                            return True

                                if await interrupt.wait(WaitCommit, timeout=300):
                                    await message.PlayerMessage("白名单申请已提交至管理组审核，请耐心等待",
                                                                targetMessage=targetMessage)
                                    cursor.execute(f"UPDATE wait SET used = 1 where token = '{token}'")
                                    await message.AdminMessage("收到一条新的白名单申请:\n"
                                                               f"审核序号:{data[0]}\n"
                                                               f"游戏名:{data[2][:16]}\n"
                                                               f"游戏版本:{data[8]}\n"
                                                               f"答题分数:{data[13]}\n"
                                                               f"Token:{token}\n"
                                                               f"个人简介:\n"
                                                               f"{data[9]}")
        else:
            await message.PlayerMessage("无法找到此Token，请确认Token是否正确", targetMessage=targetMessage)
