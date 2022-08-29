from module.Class.WhitelistClass import WhitelistClass
from module.Class.ServerClass import MinecraftServer
from module.BasicModule.Config import config
from module.Class.ServerStatusClass import ServerStatus
from module.Class.BlackListClass import BlackListClass
from module.Class.QueryClass import QueryClass
from asyncio.runners import run

if config.module["WhiteList"] or config.module["BlackList"]:
    vanillaServer = MinecraftServer(config.server["VanillaServer"]["ServerName"], config.server["VanillaServer"]["RconConfig"], config.server["VanillaServer"]["Command"])
    testServer = MinecraftServer(config.server["TestServer"]["ServerName"], config.server["TestServer"]["RconConfig"], config.server["TestServer"]["Command"])
    run(vanillaServer.TestConnection())
    run(testServer.TestConnection())
if config.module["WhiteList"]:
    whitelist = WhitelistClass(vanillaServer)
if config.module["BlackList"]:
    blacklist = BlackListClass(vanillaServer)
if config.module["Online"]:
    server = ServerStatus(config.Config["ServerList"])
query = QueryClass()
