from module.BasicModule.Config import ModuleConfig
if ModuleConfig.CheckMCUpdate:
    from requests import get
    from module.BasicModule.Config import VersionCheck
    from module.BasicModule.Logger import logger
    from module.Interlining.Bot import message
    from time import strftime, localtime

    async def CheckUpdate():
        try:
            logger.debug("开始检查MC更新")
            versionType = eval(get("https://launchermeta.mojang.com/mc/game/version_manifest.json").content.decode())["latest"]
            for Type in versionType:
                if versionType[Type] != VersionCheck.Data[Type]:
                    VersionCheck.EditData(versionType[Type], Type)
                    await message.PlayerMessage(f"检测到{Type}新版本: {versionType[Type]}\n"
                                                f"查询时间: {strftime('%Y-%m-%d %H:%M:%S', localtime())}")
            logger.debug("未检查到新版本")
        except:
            logger.error("检查更新失败")
