from module.Class.DataBaseClass import DataBase
from module.BasicModule.Config import config
database = DataBase(config["DataBase"]["database"], config["DataBase"]["host"], config["DataBase"]["username"],
                    config["DataBase"]["password"])
database.Connect()
cursor = database.GetConnectionInfo().cursor()
connection = database.GetConnectionInfo()
