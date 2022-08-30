from module.BasicModule.Config import config
from module.Class.CosClass import CosClass

if config.module["ImageReview"]:
    CosConfig = config.Config["CosConfig"]
    ConnectConfig = config.Config["CosConfig"]["ConnectConfig"]
    CosClient = CosClass(
        SecretId=ConnectConfig["SecretId"],
        SecretKey=ConnectConfig["SecretKey"],
        region=ConnectConfig["Region"],
        token=None if ConnectConfig["Token"] == "" else ConnectConfig["Token"],
        SSL=ConnectConfig["SSL"],
        Path=CosConfig["Path"],
        Bucket=CosConfig["Bucket"],
        proxies=CosConfig["enableAgent"],
        agentAddress=CosConfig["agentAddress"] if CosConfig["enableAgent"] else None)
    CosClient.Connect()

