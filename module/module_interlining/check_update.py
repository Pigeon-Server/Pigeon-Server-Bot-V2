from module.module_base.config import module_config

if module_config.check_mc_update:
    from requests import get
    from module.module_base.config import version_check
    from module.module_base.logger import logger
    from time import strftime, localtime
    from module.module_interlining.bot import message

    async def check_update():
        try:
            logger.debug("开始检查MC更新")
            versionType = eval(get("https://launchermeta.mojang.com/mc/game/version_manifest.json").content.decode())[
                "latest"]
            for Type in versionType:
                if versionType[Type] != version_check.stored_data[Type]:
                    version_check.edit_data(versionType[Type], Type)
                    await message.send_player_message(f"检测到{Type}新版本: {versionType[Type]}\n查询时间: {strftime('%Y-%m-%d %H:%M:%S', localtime())}")
            logger.debug("未检查到新版本")
        except:
            logger.error("检查更新失败")
