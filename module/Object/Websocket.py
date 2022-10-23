from module.Interlining.WebSocket import websocket  # 导入ws类实例
from module.Interlining.Bot import bot
from mirai.bot import Shutdown


@bot.add_background_task()  # 添加背景任务
async def Websocket():
    await websocket.Connect()
    while True:  # 重复运行
        async for msg in websocket.connection:
            data = eval(msg)
            if data['type'] == "OnlineBroadcast":
                websocket.clientInfo[data['uuid']] = data['name']
            elif data['type'] == "OfflineBroadcast":
                del websocket.clientInfo[data['uuid']]


@bot.on(Shutdown)
async def DisConnection(event: Shutdown):
    await websocket.DisConnection()