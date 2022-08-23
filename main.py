from khl import Message
from module.BasicModule.Logger import logger
from module.BasicModule.SendMessage import message
from module.BasicModule.Whitelist import whitelist
from module.UsefulTools import IsAdminChannel, IsPlayerChannel
from module.bot import bot
from module.WebSocket import ws
# from websockets.legacy.client import connect
# from module.WebSocket import websocket
#
# @bot.task.add_interval(seconds=1)
# async def Websocket():
#     for msg in await connect(websocket.hostname):
#         data = eval(msg)
#         if msg["type"] != "QQ":
#             print(data["message"])

@bot.command(regex=r'[\s\S]*')
async def MessageRecord(msg: Message):
    channelId = msg.ctx.channel.id
    username = msg.author.username + '#' + msg.author.identify_num
    logger.info(f"[{await message.GetChannelName(channelId)}({channelId})]收到消息 <-- {username}({msg.author.id}) : {msg.content}")

@bot.command(name='白名单')
async def GetWhitelist(msg: Message, command: str = None, id: str = None, reason: str = None):
    if IsPlayerChannel(msg.ctx.channel.id) and id is None:
        await whitelist.GetWhitelist(msg, command)
    elif IsAdminChannel(msg.ctx.channel.id):
        if command == "同意":
            await whitelist.PassOne(id)
        elif command == "拒绝":
            await whitelist.RefuseOne(id, reason)
        elif command == "查询":
            await whitelist.GetWaitList()
        else:
            await msg.reply("未知命令")
bot.run()
