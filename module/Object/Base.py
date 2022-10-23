from module.Interlining.Bot import bot, message
from mirai.bot import Startup, Shutdown
from module.BasicModule.Logger import logger
from module.BasicModule.SqlRelate import connected
from mirai.models.events import MemberJoinEvent, GroupMessage


@bot.on(Startup)
async def Startup(event: Startup):
    await message.init()  # 初始化消息发送模块
    logger.info("\n  _____  _                               _____                               \n"
                " |  __ \\(_)                             / ____|                              \n"
                " | |__) |_   __ _   ___   ___   _ __   | (___    ___  _ __ __   __ ___  _ __ \n"
                " |  ___/| | / _` | / _ \\ / _ \\ | '_ \\   \\___ \\  / _ \\| '__|\\ \\ / // _ \\| '__|\n"
                " | |    | || (_| ||  __/| (_) || | | |  ____) ||  __/| |    \\ V /|  __/| |   \n"
                " |_|    |_| \\__, | \\___| \\___/ |_| |_| |_____/  \\___||_|     \\_/  \\___||_|   \n"
                "             __/ |                                                           \n"
                "            |___/                                                            "
                "\n\n[Github源码库地址，欢迎贡献&完善&Debug]\nhttps://github.com/Pigeon-Server/Pigeon-Server-Bot-V2.git")


@bot.on(Shutdown)
async def Shutdown(event: Shutdown):
    connected.close()


@bot.on(MemberJoinEvent)
async def WelcomeMessage(event: MemberJoinEvent):
    await message.SendWelcomeMessage(event.member.id, event.member.member_name, event.member.group.id,
                                     event.member.group.name)


@bot.on(GroupMessage)
async def MessageRecord(event: GroupMessage):
    logger.info(f"[消息]<-{event.group.name}({event.sender.group.id})-{event.sender.member_name}({event.sender.id}):{str(event.message_chain)}")