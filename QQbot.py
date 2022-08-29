# 基础模块导入
from module.Interlining.Bot import bot, message, control  # 导入bot基类，消息发送模块，事件控制器模块
from module.BasicModule.Config import config  # 配置类示例导入
from mirai_extensions.trigger import Filter  # 导入过滤器模块
from mirai.bot import Startup, Shutdown  # 导入机器人启动关闭事件
from re import match as rematch  # 导入正则表达式并重命名（与match冲突）
from mirai.models.events import GroupMessage  # 导入群组消息模型
from module.BasicModule.SqlRelate import cursor, database  # 导入数据库事务和连接实例
from module.BasicModule.Logger import logger  # 导入日志记录模块
from module.Interlining.UsefulTools import IsAdminGroup, IsPlayerGroup, Segmentation, PingDataBase  # 判断是否是管理群或玩家群，消息切分，ping数据库
from module.Interlining.Objectification import query  # 导入查询类实例

# 是否启用Kook互通（未完成）
if config.module["KookInterflow"]:
    from websockets.legacy.client import connect  # 导入connect方法
    from module.Interlining.WebSocket import websocket  # 导入ws类实例

    @bot.add_background_task()  # 添加背景任务
    async def Websocket():
        while True:  # 重复运行
            async for msg in await connect(websocket.hostname):
                data = eval(msg)  # 获取消息并编码成字典
                if data["type"] == "QQ":
                    print(data["message"])

# 是否启用图片审查（未完成）
if config.module["ImageReview"]:
    from module.Interlining.UsefulTools import DownloadFile  # 下载文件方法
    from module.Interlining.CosRelate import CosClient  # 导入cos类实例
    from mirai.models.message import Image  # 导入Image类

    @bot.on(GroupMessage)
    async def download_images(event: GroupMessage):
        if event.message_chain.has(Image):  # 如果消息链里面有Image消息
            await DownloadFile(list(image.url for image in event.message_chain.get(Image)), "image", True,
                               lambda fileList: CosClient.UploadFile(fileList, EnableMD5=True) if CosClient.connected else None)

# 是否启用问答模块
if config.module["Questions"]:
    from module.Interlining.UsefulTools import FindAnswer  # 搜索答案方法

    @Filter(GroupMessage)
    def AnswerJudge(event: GroupMessage):
        if config.module["Shutup"]:  # 如果排除列表启用，则排除
            for raw in config.exception:
                if raw == event.sender.id:
                    return None
        if str(event.message_chain).startswith('/'):  # 去除/
            return None
        respond = FindAnswer(event)  # 搜寻答案
        if respond is None:  # 如果返回值是空的，则返回None
            return None
        elif respond is not None:
            return respond

    @control.on(AnswerJudge)
    async def Answer(event: GroupMessage, respond: str):
        if respond is not None:
            await message.SendMessage(event.group.id, respond, targetMessage=event.message_chain.message_id)
# 是否允许玩家自主设置屏蔽
if config.module["Shutup"]:
    from module.Interlining.UsefulTools import IsAtBot  # 判断是否艾特了机器人

    @Filter(GroupMessage)
    def ShutupSpy(event: GroupMessage):
        msg = str(event.message_chain)
        if IsAtBot(event.message_chain) and ("shutup" in msg or "闭嘴" in msg):
            return True

    @control.on(ShutupSpy)
    async def Shutup(event: GroupMessage, execute: bool):
        if execute:
            if await config.WriteException(event.sender.id):
                await message.SendMessage(event.group.id, "是否屏蔽:是")
            else:
                await message.SendMessage(event.group.id, "是否屏蔽:否")

# 是否开启在线人数查询
if config.module["Online"]:
    from module.Interlining.Objectification import server  # 导入查询实例

    @Filter(GroupMessage)
    def CheckServerStatusSpy(event: GroupMessage):
        msg = str(event.message_chain)
        command = msg[1:].rsplit(" ")[0]  # 按空格切分命令
        if msg.startswith('/') and (command == "服务器" or command == "online" or command == "server" or command == "player" or command == "info"):
            return True

    @control.on(CheckServerStatusSpy)
    async def CheckServer(event: GroupMessage, execute: bool):
        if execute:
            await message.SendMessage(event.group.id, await server.GetOnlinePlayer())

# 是否开启触发关键词撤回
if config.module["BlockWord"]:
    from random import uniform
    from asyncio.tasks import sleep

    @Filter(GroupMessage)
    def BlockingWordSpy(event: GroupMessage):
        msg: str = str(event.message_chain)
        if event.sender.permission.value == "MEMBER":  # 如果成员不是管理员或者群主
            for raw in config.word:  # 遍历屏蔽名单
                if rematch(raw, msg) is not None:  # 如果有匹配返回true
                    return True
            return False

    @control.on(BlockingWordSpy)
    async def BlockingWord(event: GroupMessage, recall: bool):
        if recall:
            await sleep(uniform(1.0, 0.3))  # 延迟
            await bot.recall(event.message_chain.message_id)  # 撤回
            await message.SendMessage(event.group.id, "触发违禁词，已撤回消息", event.sender.id)

# 是否启用白名单模块
if config.module["WhiteList"]:
    from module.Interlining.Objectification import whitelist

# 是否启用黑名单模块
if config.module["BlackList"]:
    from module.Interlining.Objectification import blacklist

@bot.on(Startup)
async def Startup(event: Startup):
    await message.init()  # 初始化消息发送模块

@bot.on(Shutdown)
async def Shutdown(event: Shutdown):
    database.Disconnect()  # 关闭前断开数据库连接

@bot.on(GroupMessage)
async def MessageRecord(event: GroupMessage):
    logger.info(f"[消息]<-{event.group.name}({event.sender.group.id})-{event.sender.member_name}({event.sender.id}):{str(event.message_chain)}")

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

@control.on(PlayerGroupCommandParsing)
async def PlayerCommand(event: GroupMessage, command: str):
    commandLen = len(command)
    targetMessage = event.message_chain.message_id
    if commandLen > 0:
        if config.module["WhiteList"] and (command[0] == "apply" or command[0] == "白名单"):
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
                            await whitelist.GetWhiteList(targetMessage, token, str(event.sender.id))
        elif config.module["BlackList"] and (command[0] == "blacklist" or command[0] == "黑名单"):
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
        elif config.module["WhiteList"] and (command[0] == "change" or command[0] == "改名"):
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
        if config.module["WhiteList"] and (command[0] == "pass" or command[0] == "通过"):
            match commandLen:
                case 1:
                    await message.AdminMessage("命令缺少参数")
                case 2:
                    await whitelist.PassOne(command[1])
        elif config.module["WhiteList"] and (command[0] == "refuse" or command[0] == "拒绝"):
            match commandLen:
                case 1:
                    await message.AdminMessage("命令缺少参数")
                case 3:
                    await whitelist.RefuseOne(command[1])
                case 4:
                    await whitelist.RefuseOne(command[1], command[2])
        elif config.module["BlackList"] and (command[0] == "ban" or command[0] == "封禁"):
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
        elif config.module["BlackList"] and (command[0] == "unban" or command[0] == "解封"):
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
        elif config.module["WhiteList"] and (command[0] == "passall" or command[0] == "全部通过"):
            if commandLen == 1:
                await whitelist.PassAll()


bot.run(port=config.Config["MiraiBotConfig"]["WebSocketPort"])
