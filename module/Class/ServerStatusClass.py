from mcstatus import JavaServer
from module.Class.ExceptionClass import IncomingParametersError, NoParametersError
from module.BasicModule.Logger import logger

class ServerStatus:
    Server: dict
    outputMessage: str
    playerOnline: int = 0
    playerMax: int = 0

    def __init__(self, serverList: dict = None) -> None:
        if serverList is None:
            raise NoParametersError("serverList参数不能是None")
        elif not isinstance(serverList, dict):
            raise IncomingParametersError("serveList必须是dict类型")
        else:
            self.Server = serverList

    async def CheckServer(self) -> None:
        self.outputMessage = "[服务器状态]\n在线人数: {online}/{max}\n在线玩家列表: \n"
        self.playerMax = 0
        self.playerOnline = 0
        serverName: str
        for raw in self.Server:
            serverName = raw
            try:
                serverStatus = JavaServer.lookup(self.Server[raw]).status()
                self.playerMax += serverStatus.players.max
                self.playerOnline += serverStatus.players.online
                outputMessage = serverName + f"({serverStatus.players.online}): "
                if len(serverStatus.players.sample) == 0:
                    outputMessage += "服务器内无玩家"
                else:
                    for player in serverStatus.players.sample:
                        outputMessage += f"[{player.name}] "
                outputMessage += "\n"
                self.outputMessage += outputMessage
                del serverStatus, outputMessage
            except Exception as error:
                logger.error(serverName)
                logger.error(error)
                self.outputMessage += serverName + "(0): 服务器连接失败\n"
            del serverName

    async def GetOnlinePlayer(self) -> str:
        await self.CheckServer()
        return self.outputMessage.format(online=self.playerOnline, max=self.playerMax).removesuffix("\n")
