from module.Interlining.UsefulTools import DownloadFile  # 下载文件方法
from module.Interlining.CosRelate import CosClient  # 导入cos类实例
from mirai.models.message import Image  # 导入Image类
from module.BasicModule.Config import ImageList, MainConfig
from module.Interlining.Bot import message, bot
from mirai.models.events import GroupMessage


@bot.on(GroupMessage)
async def ImageReview(event: GroupMessage):
    if event.message_chain.has(Image):  # 如果消息链里面有Image消息
        await DownloadFile(list(image.url for image in event.message_chain.get(Image)), "image", True,
                           lambda recall: message.RecallAndMute(event, recall),
                           lambda fileList: CosClient.UploadFile(fileList, EnableMD5=True) if CosClient.connected else None)
        if ImageList.Data["Wait"]:
            await CosClient.FilesContentRecognition(ImageList.Data["Wait"], MainConfig.CosConfig.BizType,
                                                    callback=lambda recall: message.RecallAndMute(event, recall))