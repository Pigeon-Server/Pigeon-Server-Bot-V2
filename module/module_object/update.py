from module.module_interlining.check_update import check_update
from asyncio import sleep
from module.module_interlining.bot import bot
from module.module_base.config import main_config


@bot.add_background_task()
async def check_update_task():
    while True:
        await sleep(main_config.update_check_interval)
        await check_update()
