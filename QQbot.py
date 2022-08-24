from re import match as rematch
from mirai.bot import Startup, Shutdown
from mirai.models.events import GroupMessage
from mirai_extensions.trigger import Filter
from module.BasicModule.config import config
from module.Interlining.Bot import bot, control, message
from module.BasicModule.sqlrelated import cursor, database
from module.BasicModule.logger import logger
from module.Interlining.UsefulTools import IsAdminGroup, IsPlayerGroup, FindAnswer, Segmentation, PingDataBase, IsAtBot
from module.Interlining.Objectification import whitelist, server, blacklist, query
from asyncio.tasks import sleep
from random import uniform
# from websockets.legacy.client import connect
# from module.Interlining.WebSocket import websocket

@bot.on(Startup)
async def Startup(event: Startup):
    await message.init()

@bot.on(Shutdown)
async def Shutdown(event: Shutdown):
    database.Disconnect()

# @bot.add_background_task()
# async def Websocket():
#     while True:
#         async for msg in await connect(websocket.hostname):
#             data = eval(msg)
#             if data["type"] == "QQ":
#                 print(data["message"])

@bot.on(GroupMessage)
async def MessageRecord(event: GroupMessage):
    logger.info(f"[消息]<-{event.group.name}({event.sender.group.id})-{event.sender.member_name}({event.sender.id}):{str(event.message_chain)}")

@Filter(GroupMessage)
def CheckServerStatusSpy(event: GroupMessage):
    msg = str(event.message_chain)
    command = msg[1:].rsplit(" ")[0]
    if msg.startswith('/') and (command == "服务器" or command == "online" or command == "server" or command == "player" or command == "info"):
        return True

@Filter(GroupMessage)
def ShutupSpy(event: GroupMessage):
    msg = str(event.message_chain)
    if IsAtBot(event.message_chain) and ("shutup" in msg or "闭嘴" in msg):
        return True

@Filter(GroupMessage)
def BlockingWordSpy(event: GroupMessage):
    forbiddenWordList: list = config.word["word"]
    msg: str = str(event.message_chain)
    exceptPeople: list = config.word["except"]
    if event.sender.permission.value == "MEMBER":
        if str(event.sender.id) in exceptPeople:
            return False
        for raw in forbiddenWordList:
            if rematch(raw, msg) is not None:
                return True
        return False

@Filter(GroupMessage)
def AnswerJudge(event: GroupMessage):
    for raw in config.exception:
        if raw == event.sender.id:
            return None
    if str(event.message_chain).startswith('/'):
        return None
    respond = FindAnswer(event)
    if respond is None:
        return None
    elif respond is not None:
        return respond

@Filter(GroupMessage)
def PlayerGroupCommandParsing(event: GroupMessage):
    msg = str(event.message_chain)
    if msg.startswith('/') and IsPlayerGroup(event.group.id):
        return msg[1:].rsplit(" ")

@Filter(GroupMessage)
def AdminGroupCommandParsing(event: GroupMessage):
    msg = str(event.message_chain)
    if msg.startswith('/') and IsAdminGroup(event.group.id):
        return msg[1:].rsplit(" ")

@control.on(ShutupSpy)
async def Shutup(event: GroupMessage, execute: bool):
    if execute:
        if await config.WriteException(event.sender.id):
            await message.SendMessage((await bot.get_group(event.group.id)).name, event.group.id, "是否屏蔽:是")
        else:
            await message.SendMessage((await bot.get_group(event.group.id)).name, event.group.id, "是否屏蔽:否")

@control.on(CheckServerStatusSpy)
async def CheckServer(event: GroupMessage, execute: bool):
    if execute:
        await message.SendMessage((await bot.get_group(event.group.id)).name, event.group.id, await server.GetOnlinePlayer())

@control.on(BlockingWordSpy)
async def BlockingWord(event: GroupMessage, recall: bool):
    if recall:
        await sleep(uniform(1.0, 0.3))
        await bot.recall(event.message_chain.message_id)
        await message.SendMessage((await bot.get_group(event.group.id)).name, event.group.id, "触发违禁词，已撤回消息", event.sender.id)

@control.on(AnswerJudge)
async def Answer(event: GroupMessage, respond: str):
    if respond is not None:
        await message.SendMessage((await bot.get_group(event.group.id)).name, event.group.id, respond, targetMessage=event.message_chain.message_id)

@control.on(PlayerGroupCommandParsing)
async def PlayerCommand(event: GroupMessage, command: str):
    commandLen = len(command)
    targetMessage = event.message_chain.message_id
    if commandLen > 0:
        if command[0] == "apply" or command[0] == "白名单":
            match commandLen:
                case 1:
                    await message.PlayerMessage("缺少必要参数Token", targetMessage=targetMessage)
                case 2:
                    token = command[1]
                    tokenLen = len(command[1])
                    if tokenLen > 16:
                        await message.PlayerMessage("Token过长", targetMessage=targetMessage)
                    elif tokenLen < 16:
                        await message.PlayerMessage("Token过短", targetMessage=targetMessage)
                    else:
                        if rematch('^[A-Z]+$', token) is None:
                            await message.PlayerMessage("Token应为十六位大写字母", targetMessage=targetMessage)
                        else:
                            await whitelist.GetWhitelist(targetMessage, token, str(event.sender.id))
        elif command[0] == "blacklist" or command[0] == "黑名单":
            if commandLen == 1:
                PingDataBase()
                number = cursor.execute("select * from blacklist")
                if number == 0:
                    await message.PlayerMessage("未查询到黑名单玩家", targetMessage=targetMessage)
                else:
                    tempMessage = ""
                    data = cursor.fetchall()
                    for raw in data:
                        tempMessage += f"序号：{raw[0]}\n玩家名：{raw[2]}\n理由:{raw[6]}\n"
                    await Segmentation(message.PlayerMessage, tempMessage)
            elif commandLen == 2:
                if rematch('^\\w+$', command[1]) is None or len(command[1]) < 4 or len(command[1]) > 16:
                    await message.PlayerMessage("非法玩家名", targetMessage=targetMessage)
                else:
                    PingDataBase()
                    if cursor.execute(f"select * from blacklist where PlayerName = '{command[1]}'"):
                        await message.PlayerMessage("该玩家已被封禁", targetMessage=targetMessage)
                    else:
                        await message.PlayerMessage("该玩家未被封禁", targetMessage=targetMessage)
        elif command[0] == "change" or command[0] == "改名":
            if commandLen == 2:
                if rematch('^\\w+$', command[1]) is None or len(command[1]) < 4 or len(command[1]) > 16:
                    await message.PlayerMessage("非法玩家名", targetMessage=targetMessage)
                else:
                    await whitelist.ChangeName(command[1], event.sender.id)
        elif command[0] == "token":
            PingDataBase()
            if cursor.execute(f"select * from wait where account = {event.sender.id}"):
                data = cursor.fetchone()
                await message.PlayerMessage(f"你的token为:\n"
                                            f"{data[12]}", targetMessage=targetMessage)


@control.on(AdminGroupCommandParsing)
async def AdminCommand(event: GroupMessage, command: str):
    commandLen = len(command)
    if commandLen > 0:
        if command[0] == "pass" or command[0] == "通过":
            match commandLen:
                case 1:
                    await message.AdminMessage("命令缺少参数")
                case 2:
                    await whitelist.PassOne(command[1])
        elif command[0] == "refuse" or command[0] == "拒绝":
            match commandLen:
                case 1:
                    await message.AdminMessage("命令缺少参数")
                case 3:
                    await whitelist.RefuseOne(command[1])
                case 4:
                    await whitelist.RefuseOne(command[1], command[2])
        elif command[0] == "ban" or command[0] == "封禁":
            if commandLen < 2:
                await message.AdminMessage("缺少参数")
            elif rematch('^\\w+$', command[1]) is None or len(command[1]) < 4 or len(command[1]) > 16:
                await message.AdminMessage("非法玩家名")
            else:
                match commandLen:
                    case 2:
                        await blacklist.AddBlackList(command[1])
                    case 3:
                        await blacklist.AddBlackList(command[1], command[2])
        elif command[0] == "unban" or command[0] == "解封":
            if commandLen < 2:
                await message.AdminMessage("缺少参数")
            elif rematch('^\\w+$', command[1]) is None or len(command[1]) < 4 or len(command[1]) > 16:
                await message.AdminMessage("非法玩家名")
            else:
                if commandLen == 2:
                    await blacklist.DelBlackList(command[1])
        elif command[0] == "list" or command[0] == "查询":
            if commandLen == 2:
                if command[1] == "wait" or command[1] == "待审核":
                    await Segmentation(message.AdminMessage, query.WaitList())
        elif command[0] == "lock" or command[0] == "锁定":
            if commandLen == 2:
                PingDataBase()
                if cursor.execute(f"SELECT * from wait where token = '{command[1]}'"):
                    data = cursor.fetchone()
                    if not data[16]:
                        try:
                            cursor.execute(f"UPDATE wait SET locked = 1 where token = '{command[1]}'")
                            await message.AdminMessage("锁定token成功")
                        except:
                            await message.AdminMessage("锁定token失败")
                    else:
                        await message.AdminMessage("此token已被上锁")
                else:
                    await message.AdminMessage("无法找到此Token，请确认Token是否正确")
        elif command[0] == "unlock" or command[0] == "解锁":
            if commandLen == 2:
                PingDataBase()
                if cursor.execute(f"SELECT * from wait where token = '{command[1]}'"):
                    data = cursor.fetchone()
                    if data[16]:
                        try:
                            cursor.execute(f"UPDATE wait SET locked = 0 where token = '{command[1]}'")
                            await message.AdminMessage("解锁成功")
                        except:
                            await message.AdminMessage("解锁失败")
                    else:
                        await message.AdminMessage("此token未被上锁")
                else:
                    await message.AdminMessage("无法找到此Token，请确认Token是否正确")
        elif command[0] == "reload" or command[0] == "重载":
            if commandLen == 1:
                await message.AdminMessage("正在重载配置文件")
                if await config.reloadConfig():
                    await message.AdminMessage("重载配置文件成功")
                else:
                    await message.AdminMessage("重载配置文件出错")
        elif command[0] == "passall" or command[0] == "全部通过":
            if commandLen == 1:
                await whitelist.PassAll()

bot.run(port=config.Config["MiraiBotConfig"]["WebSocketPort"])
