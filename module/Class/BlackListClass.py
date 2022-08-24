from module.BasicModule.sqlrelated import cursor
from module.Interlining.Bot import message
from module.Class.ServerClass import MinecraftServer
from module.Interlining.UsefulTools import PingDataBase

class BlackListClass:

    __MinecraftServer: MinecraftServer

    def __init__(self, server: MinecraftServer) -> None:

        """
        构造函数\n
        """

        self.__MinecraftServer = server

    async def AddBlackList(self, playerName: str, reason: str = "None") -> None:

        """
        添加黑名单\n
        :param playerName: 玩家名（必填)
        :param reason: 封禁理由,默认为None
        """

        PingDataBase()
        if cursor.execute(f"select * from wait where PlayerName = '{playerName}'"):
            try:
                data = cursor.fetchone()
                cursor.execute(f"update wait set locked = 1 where PlayerName = '{playerName}'")
                cursor.execute(
                    f"INSERT INTO `blacklist` (`id`, `account`, `PlayerName`, `UserSource`, `GameVersion`, `token`, `reason`) VALUES ({data[0]}, '{data[1]}', '{data[2]}', '{data[3]}', '{data[8]}', '{data[12]}', '{reason}')")
                await self.__MinecraftServer.AddBan(playerName, reason)
                await message.AdminMessage(f"玩家{playerName}加入黑名单成功")
                await message.PlayerMessage(f"玩家{playerName}已被加入黑名单，原因{reason}\n"
                                                f"请各位引以为鉴")
            except:
                await message.AdminMessage("加入黑名单失败")
        else:
            await message.AdminMessage("该玩家不存在，请确认玩家名")

    async def DelBlackList(self, playerName: str) -> None:

        """
        移除黑名单\n
        :param playerName: 玩家名
        """

        PingDataBase()
        if cursor.execute(f"select * from wait where PlayerName = '{playerName}'"):
            try:
                cursor.execute(f"update wait set locked = 0 where PlayerName = '{playerName}'")
                cursor.execute(f"DELETE FROM `blacklist` WHERE `PlayerName` = '{playerName}'")

                await self.__MinecraftServer.DelBan(playerName)
                await message.AdminMessage(f"玩家{playerName}移除黑名单成功")
                await message.PlayerMessage(f"玩家{playerName}已被移除黑名单")
            except:
                await message.AdminMessage("移除黑名单失败")
        else:
            await message.AdminMessage("该玩家不存在，请确认玩家名")
