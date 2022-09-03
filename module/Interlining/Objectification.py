from module.Class.WhitelistClass import WhitelistClass
from module.Class.ServerClass import MinecraftServer
from module.BasicModule.Config import MainConfig, ModuleConfig
from module.Class.ServerStatusClass import ServerStatus
from module.Class.BlackListClass import BlackListClass
from module.Class.QueryClass import QueryClass
from asyncio.runners import run
from sys import exit

if ModuleConfig.WhiteList or ModuleConfig.BlackList:
    from module.BasicModule.Config import ServerConfig
    try:
        vanillaServer = MinecraftServer(ServerConfig.VanillaServer.ServerName, vars(ServerConfig.VanillaServer.RconConfig), vars(ServerConfig.VanillaServer.Command))
        run(vanillaServer.TestConnection())
    except:
        exit()
    try:
        testServer = MinecraftServer(ServerConfig.TestServer.ServerName, vars(ServerConfig.TestServer.RconConfig), vars(ServerConfig.TestServer.Command))
        run(testServer.TestConnection())
    except:
        exit()
if ModuleConfig.WhiteList:
    whitelist = WhitelistClass(vanillaServer)
if ModuleConfig.BlackList:
    blacklist = BlackListClass(vanillaServer)
if ModuleConfig.Online:
    server = ServerStatus(vars(MainConfig.ServerList))
query = QueryClass()
