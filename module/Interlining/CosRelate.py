from module.BasicModule.Logger import logger
from module.BasicModule.Config import config
from module.Class.CosClass import CosClass

if config.module["ImageReview"]:
    CosConfig = config.Config["CosConfig"]
    ConnectConfig = config.Config["CosConfig"]["ConnectConfig"]
    logger.debug("正在尝试登录Cos")
    CosClient = CosClass(
        SecretId=ConnectConfig["SecretId"],
        SecretKey=ConnectConfig["SecretKey"],
        region=ConnectConfig["Region"],
        token=ConnectConfig["Token"] == "" if None else ConnectConfig["Token"],
        SSL=ConnectConfig["SSL"],
        Path=CosConfig["Path"],
        Bucket=CosConfig["Bucket"],
        proxies=CosConfig["enableAgent"],
        agentAddress=CosConfig["agentAddress"] if CosConfig["enableAgent"] else None)
    CosClient.Connect()

