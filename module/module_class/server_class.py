from module.module_class.exception_class import IncomingParametersError, CommandNotFoundError, ConnectServerError
from module.module_base.logger import logger
from rcon.source import rcon
from typing import Optional


class MinecraftServer:
    _command: dict
    server_name: str
    _rcon_host: str
    _rcon_port: int
    _rcon_password: str

    def __init__(self, servet_name: str, rcon_config: dict, command_config: dict) -> None:
        if isinstance(servet_name, str) and isinstance(rcon_config, dict) and isinstance(command_config, dict):
            self.server_name = servet_name
            for item in command_config:
                command_config[item] = vars(command_config[item])
            self._command = command_config
            self._rcon_host = rcon_config["rcon_host"]
            self._rcon_port = rcon_config["rcon_port"]
            self._rcon_password = rcon_config["rcon_password"]
        else:
            raise IncomingParametersError()

    async def test_connection(self) -> None:
        logger.debug(f"正在测试到服务器{self.server_name}的连接")
        try:
            if await rcon("list", host=self._rcon_host, port=self._rcon_port, passwd=self._rcon_password):
                logger.success(f"成功连接到服务器{self.server_name}")
        except:
            logger.error(f"无法连接到{self.server_name}")
            raise ConnectServerError(f"无法连接到{self.server_name}")

    async def server_run_command(self, command: str) -> Optional[str]:
        logger.debug(f"服务器{self.server_name}执行命令: {command}")
        try:
            respond = await rcon(command, host=self._rcon_host, port=self._rcon_port, passwd=self._rcon_password)
            logger.success(f"命令执行成功")
            return respond
        except:
            logger.error(f"服务器{self.server_name}执行命令时发生错误")

    async def add_whitelist(self, player_name: str) -> bool:
        if "whitelist" in self._command.keys():
            if "add" in self._command["whitelist"].keys():
                logger.debug(f"服务器{self.server_name}添加白名单{player_name}")
                try:
                    respond = await self.server_run_command(self._command["whitelist"]["add"].format(player=player_name))
                    if "Added" in respond or "already" in respond:
                        logger.success(f"服务器{self.server_name}添加{player_name}白名单成功")
                        return True
                    else:
                        logger.error(f"服务器{self.server_name}添加{player_name}白名单失败")
                except:
                    logger.error(f"{self.server_name}: 执行命令时发生错误")
            else:
                raise CommandNotFoundError("没有在Whitelist配置里面找到Add命令")
        else:
            raise CommandNotFoundError("没有找到Whitelist配置")

    async def del_whitelist(self, player_name: str) -> bool:
        if "whitelist" in self._command.keys():
            if "delete" in self._command["whitelist"].keys():
                logger.debug(f"服务器{self.server_name}移除白名单{player_name}")
                try:
                    respond = await self.server_run_command(self._command["whitelist"]["delete"].format(player=player_name))
                    if "Removed" in respond or "not" in respond:
                        logger.success(f"服务器{self.server_name}移除{player_name}白名单成功")
                        return True
                    else:
                        logger.error(f"服务器{self.server_name}移除{player_name}白名单出现未知错误")
                except:
                    logger.error(f"{self.server_name}: 执行命令时发生错误")
            else:
                raise CommandNotFoundError("没有在Whitelist配置里面找到Del命令")
        else:
            raise CommandNotFoundError("没有找到Whitelist配置")

    async def add_ban(self, player_name: str, reason: str = None) -> bool:
        if "ban" in self._command.keys():
            if "add" in self._command["ban"].keys():
                logger.debug(f"服务器{self.server_name}封禁玩家{player_name}")
                try:
                    respond = await self.server_run_command(self._command["ban"]["add"].format(player=player_name, reason=reason))
                    if "Banned" in respond or "banned" in respond:
                        logger.success(f"服务器{self.server_name}封禁{player_name}成功")
                        return True
                    else:
                        logger.error(f"服务器{self.server_name}封禁{player_name}发生错误")
                except:
                    logger.error(f"{self.server_name}: 执行命令时发生错误")
            else:
                raise CommandNotFoundError("没有在Ban配置里面找到Add命令")
        else:
            raise CommandNotFoundError("没有找到Ban配置")

    async def del_ban(self, player_name: str) -> bool:
        if "ban" in self._command.keys():
            if "delete" in self._command["ban"].keys():
                logger.debug(f"服务器{self.server_name}解封玩家{player_name}")
                try:
                    respond = await self.server_run_command(self._command["ban"]["delete"].format(player=player_name))
                    if "Unbanned" in respond or "isn't" in respond:
                        logger.success(f"服务器{self.server_name}解封{player_name}成功")
                        return True
                    else:
                        logger.error(f"服务器{self.server_name}解封{player_name}发生错误")
                except:
                    logger.error(f"{self.server_name}: 执行命令时发生错误")
            else:
                raise CommandNotFoundError("没有在Ban配置里面找到Del命令")
        else:
            raise CommandNotFoundError("没有找到Ban配置")
