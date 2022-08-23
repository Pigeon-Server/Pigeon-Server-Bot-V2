from module.Class.ServerClass import MinecraftServer
from module.BasicModule.Config import config

VanillaServer = MinecraftServer(config["RCON"]["port"], config["RCON"]["host"], config["RCON"]["password"],
                                config["RCON"]["name"], config["Command"]["WhitelistAdd"],
                                config["Command"]["WhitelistDel"])
