from module.Class.WhitelistClass import Whitelist
from module.BasicModule.Server import VanillaServer
from module.BasicModule.SqlRelate import database
from module.BasicModule.SendMessage import message

whitelist = Whitelist(database, VanillaServer, message)
