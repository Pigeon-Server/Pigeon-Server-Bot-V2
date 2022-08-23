from module.BasicModule.Config import config
from module.BasicModule.Logger import logger

class Whitelist:

    """
    白名单类\n
    父类：Database MinecraftServer\n
    """
    __cursor = None
    __DataBaseClass = None
    __ServerClass = None
    __MessageClass = None

    def __init__(self, Database, Server, Message) -> None:

        """
        构造函数\n
        :param Database: Database连接
        :param Server: MinecraftServer类
        """

        self.__DataBaseClass = Database
        self.__ServerClass = Server
        self.__MessageClass = Message
        self.__cursor = self.__DataBaseClass.GetConnectionInfo().cursor()

    async def GetWhitelist(self, msg, token: str) -> None:
        username = msg.author.username + '#' + msg.author.identify_num
        if len(token) > 16:
            await self.__MessageClass.ReplyMessage(msg, username, "token长度过长！")
        elif len(token) < 16:
            await self.__MessageClass.ReplyMessage(msg, username, "token长度过短！")
        elif token.isupper() is False:
            await self.__MessageClass.ReplyMessage(msg, username, "token应全为大写字母！")
        else:
            self.__DataBaseClass.Ping()
            logger.info(f"用户{username}({msg.author.id})正在申请白名单，申请秘钥为：{token}")
            result = self.__cursor.execute(f"select * from wait where token = '{token}'")
            if result == 1:
                output = self.__cursor.fetchone()
                print(output)
                if output[16]:
                    await self.__MessageClass.ReplyMessage(msg, username, "此token已被锁定，请联系管理员！")
                else:
                    if output[1] == username:
                        if output[3] == "QQ":
                            await self.__MessageClass.ReplyMessage(msg, username, "请前往QQ群申请")
                        elif output[15] and output[17] is None:
                            await self.__MessageClass.ReplyMessage(msg, username, "您的白名单申请正在处理中，请耐心等待")
                        elif output[17]:
                            await self.__MessageClass.ReplyMessage(msg, username, "你已获取过白名单")
                        elif output[17] == 0:
                            if output[18] is None:
                                await self.__MessageClass.ReplyMessage(msg, username, "你的白名单申请已被拒绝")
                            else:
                                await self.__MessageClass.ReplyMessage(msg, username, f"你的白名单申请已被拒绝，理由为：{output[18]}")
                        else:
                            self.__cursor.execute(f"update wait set kookid = '{msg.author.id}' where token = '{token}' and account = '{username}'")
                            self.__cursor.execute(f"update wait set used = true where token = '{token}' and account = '{username}'")
                            await self.__MessageClass.ReplyMessage(msg, username, "您的白名单申请已提交至管理组，请耐心等待")
                            await self.__MessageClass.SendMessage(config["channel"]["admin"], "[白名单申请]:\n"
                                                                                              "收到一条新的白名单申请\n"
                                                                                              f"审核ID：{output[0]}\n"
                                                                                              f"申请人账号:{output[1]}({msg.author.id})\n"
                                                                                              f"申请玩家名:{output[2]}\n"
                                                                                              f"申请人年龄：{output[5]}\n"
                                                                                              f"答题分数：{output[13]}\n"
                                                                                              f"自我介绍：{output[9]}")
                            self.__DataBaseClass.GetConnectionInfo().commit()
                            del output
                    else:
                        await self.__MessageClass.ReplyMessage(msg, username, "这不是你的token，此token已被锁定。")
                        self.__cursor.execute(f"update wait set locked = true where token = '{token}'")
                        self.__DataBaseClass.GetConnectionInfo().commit()
            elif result > 1:
                await self.__MessageClass.ReplyMessage(msg, username, "token发生重复！请联系管理员！")
            else:
                await self.__MessageClass.ReplyMessage(msg, username, "token不存在，请检查您的token是否正确")

    async def PassOne(self, id: str):
        self.__DataBaseClass.Ping()
        if self.__cursor.execute(f"select * from wait where id = '{id}'"):
            output = self.__cursor.fetchone()
            if output[15]:
                self.__cursor.execute(f"update wait set pass = true where id = '{id}'")
                await self.__ServerClass.WhitelistAdd(output[2])
                self.__cursor.execute(f"INSERT INTO whitelist(id,account,PlayerName,UserSource,GameVersion,token) VALUES({output[0]},'{output[1]}','{output[2]}','{output[3]}','{output[8]}','{output[12]}')")
                await self.__MessageClass.SendMessage(config["channel"]["admin"], f"ID:{output[0]}添加白名单成功")
                await self.__MessageClass.SendMessage(config["channel"]["player"], f"(met){output[4]}(met)白名单审核通过")
                self.__DataBaseClass.GetConnectionInfo().commit()
                del output
            else:
                await self.__MessageClass.SendMessage(config["channel"]["admin"], "用户还未申请白名单！")
        else:
            await self.__MessageClass.SendMessage(config["channel"]["admin"], "审核ID不存在，请确认ID是否正确")

    async def RefuseOne(self, id: str, reason: str = None):
        self.__DataBaseClass.Ping()
        if self.__cursor.execute(f"select * from wait where id = '{id}'"):
            output = self.__cursor.fetchone()
            if output[15]:
                if reason is None:
                    self.__cursor.execute(f"update wait set pass = false where id = '{id}'")
                    await self.__MessageClass.SendMessage(config["channel"]["admin"], f"ID:{output[0]}拒绝白名单成功")
                    await self.__MessageClass.SendMessage(config["channel"]["player"], f"(met){output[4]}(met)白名单申请被管理组拒绝")
                else:
                    self.__cursor.execute(f"update wait set pass = false where id = '{id}'")
                    self.__cursor.execute(f"update wait set passinfo = '{reason}' where id = '{id}'")
                    await self.__MessageClass.SendMessage(config["channel"]["admin"], f"ID:{output[0]}拒绝白名单成功")
                    await self.__MessageClass.SendMessage(config["channel"]["player"], f"(met){output[4]}(met)白名单申请被管理组拒绝,理由是{reason}")
                self.__DataBaseClass.GetConnectionInfo().commit()
                del output
            else:
                await self.__MessageClass.SendMessage(config["channel"]["admin"], "用户还未申请白名单！")
        else:
            await self.__MessageClass.SendMessage(config["channel"]["admin"], "审核ID不存在，请确认ID是否正确")

    async def GetWaitList(self):
        self.__DataBaseClass.Ping()
        success = self.__cursor.execute(f"select * from wait where pass is null")
        if success >= 1:
            tempStr = "---\n"
            UserInfo = self.__cursor.fetchall()
            for raw in UserInfo:
                tempStr += f"审核序号：{raw[0]}\n玩家账号：{raw[1]}\n玩家名: {raw[2]}\nToken:{raw[12]}\n---"
            await self.__MessageClass.SendMessage(config["channel"]["admin"], tempStr)
        else:
            await self.__MessageClass.SendMessage(config["channel"]["admin"], "未查询到待审核玩家")
