from module.module_base.config import module_config

if module_config.check_mc_update:
    from requests import get
    from module.module_base.config import version_check
    from module.module_base.logger import logger
    from time import strftime, localtime
    from module.module_interlining.bot import message

    if version_check.stored_data == {}:  # 初始化data
        version_check.edit_data("", "release")
        version_check.edit_data("", "snapshot")
        logger.debug("成功初始化data")

    async def check_update():
        try:
            logger.debug("开始检查MC更新")
            res = eval(get("https://launchermeta.mojang.com/mc/game/version_manifest.json", timeout=5000).content.decode())
            versionType = res["latest"]
            versions = res['versions']
            for Type in versionType:
                if versionType[Type] != version_check.stored_data[Type]:
                    for version_item in versions:
                        if version_item["id"] == versionType[Type]:
                            Release_date = version_item["releaseTime"]
                            break
                    version_check.edit_data(versionType[Type], Type)
                    await message.send_player_message(f"检测到{Type}新版本: {versionType[Type]}\n发布日期：{Release_date}\n查询时间: {strftime('%Y-%m-%d %H:%M:%S', localtime())}")
            logger.debug("未检查到新版本")
        except:
            logger.error("检查更新失败")
