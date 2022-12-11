from module.module_interlining.websocket import websocket  # 导入ws类实例
from module.module_interlining.bot import bot
from mirai.bot import Shutdown


@bot.add_background_task()  # 添加背景任务
async def websocket():
    await websocket.connect()
    while True:  # 重复运行
        async for msg in websocket.connection:
            data = eval(msg)
            if data['type'] == "OnlineBroadcast":
                websocket.client_info[data['uuid']] = data['name']
            elif data['type'] == "OfflineBroadcast":
                del websocket.client_info[data['uuid']]


@bot.on(Shutdown)
async def disconnection(event: Shutdown):
    await websocket.disconnection()