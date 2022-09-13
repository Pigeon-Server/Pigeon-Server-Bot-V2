from module.BasicModule.Config import MainConfig, ModuleConfig
from module.Class.CosClass import CosClass

if ModuleConfig.ImageReview:
    CosConfig = MainConfig.CosConfig
    ConnectConfig = MainConfig.CosConfig.ConnectConfig
    CosClient = CosClass(
        SecretId=ConnectConfig.SecretId,
        SecretKey=ConnectConfig.SecretKey,
        region=ConnectConfig.Region,
        token=None if ConnectConfig.Token == "" else ConnectConfig.Token,
        SSL=ConnectConfig.SSL,
        Path=CosConfig.Path,
        Bucket=CosConfig.Bucket,
        proxies=CosConfig.enableAgent,
        agentAddress=CosConfig.agentAddress if CosConfig.enableAgent else None)
    CosClient.Connect()

