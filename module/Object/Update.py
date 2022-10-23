from module.Interlining.CheckUpdate import CheckUpdate
from asyncio import sleep
from module.Interlining.Bot import bot
from module.BasicModule.Config import MainConfig


@bot.add_background_task()
async def CheckUpdateTask():
    while True:
        await sleep(MainConfig.UpdateCheckInterval)
        await CheckUpdate()
