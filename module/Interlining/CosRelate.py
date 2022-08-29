from module.BasicModule.Logger import logger
from module.BasicModule.Config import config
from qcloud_cos.cos_exception import CosClientError
from module.Class.CosClass import CosClass


if config.module["ImageReview"]:
    CosConfig = config.Config["CosConfig"]
    ConnectConfig = config.Config["CosConfig"]["ConnectConfig"]
    logger.debug("正在尝试登录Cos")
    try:
        CosClient = CosClass(
            SecretId=ConnectConfig["SecretId"],
            SecretKey=ConnectConfig["SecretKey"],
            region=ConnectConfig["Region"],
            token=ConnectConfig["Token"] == "" if None else ConnectConfig["Token"],
            SSL=ConnectConfig["SSL"],
            Path=CosConfig["Path"],
            Bucket=CosConfig["Bucket"]
        )
    except CosClientError as err:
        logger.error(f"尝试Cos登录时发生错误：{err}")
    else:
        logger.success("Cos登录成功")
