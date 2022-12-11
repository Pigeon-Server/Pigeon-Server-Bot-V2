from module.module_interlining.useful_tools import download_file  # 下载文件方法
from module.module_interlining.cos_relate import cos_client  # 导入cos类实例
from mirai.models.message import Image  # 导入Image类
from module.module_base.config import image_list, main_config
from module.module_interlining.bot import message, bot
from mirai.models.events import GroupMessage


@bot.on(GroupMessage)
async def image_review(event: GroupMessage):
    if event.message_chain.has(Image):  # 如果消息链里面有Image消息
        await download_file(list(image.url for image in event.message_chain.get(Image)), "image", True,
                            lambda recall: message.recall_and_mute(event, recall),
                            lambda fileList: cos_client.upload_file(fileList,
                                                                    enable_md5=True) if cos_client.connected else None)
        if image_list.stored_data["Wait"]:
            await cos_client.files_content_recognition(image_list.stored_data["Wait"], main_config.cos_config.biz_type,
                                                       callback=lambda recall: message.recall_and_mute(event, recall))