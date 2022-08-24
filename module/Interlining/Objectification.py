from module.Class.WhitelistClass import WhitelistClass
from module.Class.ServerClass import MinecraftServer
from module.BasicModule.config import config
from module.Class.ServerStatusClass import ServerStatus
from module.Class.BlackListClass import BlackListClass
from module.Class.QueryClass import QueryClass
from asyncio.runners import run

vanillaServer = MinecraftServer(config.server["VanillaServer"]["ServerName"], config.server["VanillaServer"]["RconConfig"], config.server["VanillaServer"]["Command"])
testServer = MinecraftServer(config.server["TestServer"]["ServerName"], config.server["TestServer"]["RconConfig"], config.server["TestServer"]["Command"])
run(vanillaServer.TestConnection())
run(testServer.TestConnection())
whitelist = WhitelistClass(vanillaServer)
server = ServerStatus(config.Config["ServerList"])
blacklist = BlackListClass(vanillaServer)
query = QueryClass()
