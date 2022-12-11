from module.module_base.sql_relate import cursor
from module.module_interlining.bot import message
from module.module_class.server_class import MinecraftServer
from module.module_interlining.useful_tools import ping_database
from module.module_base.config import main_config
from module.module_base.permission import per


class BlackListClass:

    _minecraft_server: MinecraftServer

    def __init__(self, server: MinecraftServer) -> None:

        """
        构造函数\n
        """

        self._minecraft_server = server

    async def add_black_list(self, player_name: str, reason: str = "None") -> None:

        """
        添加黑名单\n
        :param player_name: 玩家名（必填)
        :param reason: 封禁理由,默认为None
        """

        ping_database()
        if cursor.execute(f"select * from wait where PlayerName = '{player_name}'"):
            try:
                data = cursor.fetchone()
                cursor.execute(f"update wait set locked = 1 where PlayerName = '{player_name}'")
                cursor.execute(
                    f"INSERT INTO `blacklist` (`id`, `account`, `PlayerName`, `UserSource`, `GameVersion`, `token`, `reason`) VALUES ({data[0]}, '{data[1]}', '{data[2]}', '{data[3]}', '{data[8]}', '{data[12]}', '{reason}')")
                await self._minecraft_server.add_ban(player_name, reason)
                await message.send_admin_message(f"玩家{player_name}加入黑名单成功")
                await message.send_player_message(f"玩家{player_name}已被加入黑名单，原因{reason}\n"
                                                f"请各位引以为鉴")
            except:
                await message.send_admin_message("加入黑名单失败")
            else:
                per.set_player_group(data[1], main_config.permission.ban)
        else:
            await message.send_admin_message("该玩家不存在，请确认玩家名")

    async def del_blacklist(self, player_name: str) -> None:

        """
        移除黑名单\n
        :param player_name: 玩家名
        """

        ping_database()
        if cursor.execute(f"select * from wait where PlayerName = '{player_name}'"):
            try:
                data = cursor.fetchone()
                cursor.execute(f"update wait set locked = 0 where PlayerName = '{player_name}'")
                cursor.execute(f"DELETE FROM `blacklist` WHERE `PlayerName` = '{player_name}'")
                await self._minecraft_server.del_ban(player_name)
                await message.send_admin_message(f"玩家{player_name}移除黑名单成功")
                await message.send_player_message(f"玩家{player_name}已被移除黑名单")
            except:
                await message.send_admin_message("移除黑名单失败")
            else:
                per.set_player_group(data[1], main_config.permission.default)
        else:
            await message.send_admin_message("该玩家不存在，请确认玩家名")
