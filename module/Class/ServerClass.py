from module.Class.ExceptionClass import IncomingParametersError, CommandNotFoundError, ConnectServerError
from module.BasicModule.Logger import logger
from rcon.source import rcon

class MinecraftServer:
    _Command: dict
    ServerName: str
    _Host: str
    _Port: int
    _Password: str

    def __init__(self, ServerName: str, RconConfig: dict, Command: dict) -> None:
        if isinstance(ServerName, str) and isinstance(RconConfig, dict) and isinstance(Command, dict):
            self.ServerName = ServerName
            self._Command = Command
            self._Host = RconConfig["RconHost"]
            self._Port = RconConfig["RconPort"]
            self._Password = RconConfig["RconPassword"]
        else:
            raise IncomingParametersError()

    async def TestConnection(self) -> None:
        logger.debug(f"正在测试到服务器{self.ServerName}的连接")
        try:
            if await rcon("list", host=self._Host, port=self._Port, passwd=self._Password):
                logger.success(f"成功连接到服务器{self.ServerName}")
        except:
            logger.error(f"连接到{self.ServerName}时出错")
            raise ConnectServerError(f"连接到服务器{self.ServerName}出错")

    async def ServerRunCommand(self, command: str) -> str:
        logger.debug(f"服务器{self.ServerName}执行命令: {command}")
        try:
            respond = await rcon(command, host=self._Host, port=self._Port, passwd=self._Password)
            logger.success(f"命令执行成功")
            return respond
        except:
            logger.error(f"服务器{self.ServerName}执行命令出错")

    async def AddWhitelist(self, PlayerName: str) -> bool:
        if "Whitelist" in self._Command.keys():
            if "Add" in self._Command["Whitelist"].keys():
                logger.debug(f"服务器{self.ServerName}添加白名单{PlayerName}")
                try:
                    respond = await self.ServerRunCommand(self._Command["Whitelist"]["Add"].format(player=PlayerName))
                    if "Added" in respond or "already" in respond:
                        logger.success(f"服务器{self.ServerName}添加{PlayerName}白名单成功")
                        return True
                    else:
                        logger.error(f"服务器{self.ServerName}添加{PlayerName}白名单失败")
                except:
                    logger.error(f"{self.ServerName}: 执行命令时出错")
            else:
                raise CommandNotFoundError("没有在Whitelist配置里面找到Add命令")
        else:
            raise CommandNotFoundError("没有找到Whitelist配置")

    async def DelWhitelist(self, PlayerName: str) -> bool:
        if "Whitelist" in self._Command.keys():
            if "Del" in self._Command["Whitelist"].keys():
                logger.debug(f"服务器{self.ServerName}移除白名单{PlayerName}")
                try:
                    respond = await self.ServerRunCommand(self._Command["Whitelist"]["Del"].format(player=PlayerName))
                    if "Removed" in respond or "not" in respond:
                        logger.success(f"服务器{self.ServerName}移除{PlayerName}白名单成功")
                        return True
                    else:
                        logger.error(f"服务器{self.ServerName}移除{PlayerName}白名单出现未知错误")
                except:
                    logger.error(f"{self.ServerName}: 执行命令时出错")
            else:
                raise CommandNotFoundError("没有在Whitelist配置里面找到Del命令")
        else:
            raise CommandNotFoundError("没有找到Whitelist配置")

    async def AddBan(self, PlayerName: str, reason: str = None) -> bool:
        if "Ban" in self._Command.keys():
            if "Add" in self._Command["Ban"].keys():
                logger.debug(f"服务器{self.ServerName}封禁玩家{PlayerName}")
                try:
                    respond = await self.ServerRunCommand(self._Command["Ban"]["Add"].format(player=PlayerName, reason=reason))
                    if "Banned" in respond or "banned" in respond:
                        logger.success(f"服务器{self.ServerName}封禁{PlayerName}成功")
                        return True
                    else:
                        logger.error(f"服务器{self.ServerName}封禁{PlayerName}发生错误")
                except:
                    logger.error(f"{self.ServerName}: 执行命令出错")
            else:
                raise CommandNotFoundError("没有在Ban配置里面找到Add命令")
        else:
            raise CommandNotFoundError("没有找到Ban配置")

    async def DelBan(self, PlayerName: str) -> bool:
        if "Ban" in self._Command.keys():
            if "Del" in self._Command["Ban"].keys():
                logger.debug(f"服务器{self.ServerName}解封玩家{PlayerName}")
                try:
                    respond = await self.ServerRunCommand(self._Command["Ban"]["Del"].format(player=PlayerName))
                    if "Unbanned" in respond or "isn't" in respond:
                        logger.success(f"服务器{self.ServerName}解封{PlayerName}成功")
                        return True
                    else:
                        logger.error(f"服务器{self.ServerName}解封{PlayerName}发生错误")
                except:
                    logger.error(f"{self.ServerName}: 执行命令出错")
            else:
                raise CommandNotFoundError("没有在Ban配置里面找到Del命令")
        else:
            raise CommandNotFoundError("没有找到Ban配置")
