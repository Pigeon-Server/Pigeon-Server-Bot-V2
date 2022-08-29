from urllib import parse

from module.BasicModule.logger import logger
from module.BasicModule.config import config
from qcloud_cos import CosConfig, CosS3Client
from qcloud_cos.cos_exception import CosClientError, CosServiceError
import sys
import logging
import os
import filetype
import requests
import hashlib
import asyncio

Cos_success = False  # Cos是否登录成功

async def download_files(urls: list, path: str, files_name, callback=None):
    """
    下载文件
    urls：文件列表
    path：保存的目录（须提前创建，如果目录不存在会报错）
    files_name：文件名（列表形式，与urls对应，如为字符串并为“md5”会将文件名改为文件的md5）
    callback：回调函数，输出成功的文件名（列表），如果为空将直接输出
    """

    success_file_list = []
    for index, url in enumerate(urls, 0):
        try:
            fileio = requests.get(url)
        except:
            logger.error("下载失败，URL：" + url)
        else:
            file_type = filetype.guess(fileio.content)  # 文件类型识别
            Status = False
            if isinstance(files_name, str) and files_name == "md5":
                md5 = hashlib.md5(fileio.content).hexdigest()  # md5生成
                if file_type:  # 文件名拼接
                    file_name = os.path.join(path, md5 + "." + file_type.extension)
                else:
                    file_name = os.path.join(path, md5)
                if os.path.exists(file_name) is not True:
                    Status = True
                    open(file_name, "wb").write(fileio.content)
                fileio.close()
            else:
                if file_type:  # 文件名拼接
                    file_name = os.path.join(path, files_name[index] + "." + file_type.extension)
                else:
                    file_name = os.path.join(path, files_name[index])
                if os.path.exists(file_name) is not True:
                    Status = True
                    open(file_name, "wb").write(fileio.content)
                fileio.close()
            if Status:
                success_file_list.append(file_name)
    if callback is not None:  # 有回调时回调，没回调直接返回
        return callback(success_file_list)
    else:
        return success_file_list


class cos_tools():  # Cos属于付费接口，尽量少调用
    __connect_config = None
    __client = None

    def __init__(self, secret_id, secret_key, region, token=None, SSL=True):
        global Cos_success
        # 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在CosConfig中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
        if SSL:  # 指定使用 http/https 协议来访问 COS，默认为 https，可不填
            scheme = 'https'
        else:
            scheme = 'http'
        self.__connect_config = CosConfig(
            Region=region,
            SecretId=secret_id,
            SecretKey=secret_key,
            Token=token,
            Scheme=scheme
        )
        self.__client = CosS3Client(self.__connect_config)
        Cos_success = True

        # 正常情况日志级别使用INFO，需要定位时可以修改为DEBUG，此时SDK会打印和服务端的通信信息
        # logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    def upload_files(self, files: list, Bucket: str, path: str, EnableMD5: bool):
        """
        上传文件至cos
        """
        success_all = []
        for file in files:
            if os.path.exists(file) is True:  # 判断本地文件是否存在
                if self.__client.object_exists(Bucket, Key=path + "/" + os.path.split(file)[-1]) is False:  # 判断Cos上是否存在该文件
                    for i in range(0, 3):  # 使用高级接口断点续传，失败重试时不会上传已成功的分块(这里重试10次)
                        try:
                            response = self.__client.upload_file(
                                Bucket=Bucket,
                                LocalFilePath=file,  # 本地文件的路径
                                Key=path + "/" + os.path.split(file)[-1],  # 上传到桶之后的文件名
                                PartSize=1,  # 上传分成几部分
                                MAXThread=10,  # 支持最多的线程数
                                EnableMD5=EnableMD5  # 是否支持MD5
                            )
                            logger.debug(response['ETag'])
                            success_all.append(os.path.join(path, file.rsplit("/")[-1]))
                            break
                        except CosClientError or CosServiceError as err:
                            logger.error(f"[{i}]尝试上传文件时发生错误：{err}")
                else:
                    logger.error(f"{file}已在Cos存在")
            else:
                logger.error("文件不存在：" + file)
        return success_all

    def del_files(self, Bucket: str, files: list, VersionId=None):
        """
        删除cos中的文件
        """
        success_all = []
        for file in files:
            res = None
            if VersionId is None:
                res = self.__client.delete_object(
                    Bucket=Bucket,
                    Key=file
                )
            else:
                res = self.__client.delete_object(
                    Bucket=Bucket,
                    Key=file,
                    VersionId=VersionId
                )
            if res.get("x-cos-delete-marker") is True:
                success_all.append(file)
                if VersionId is True:
                    logger.debug(f"删除{file}成功，版本：{res.get('x-cos-version-id')}")
                else:
                    logger.debug(f"删除{file}成功")
            else:
                logger.debug(f"删除{file}失败")
        return success_all

    # async def review_images(self):
    #     """
    #     审核Cos中的图片
    #     """

Cos_Config = config.Config["CosConfig"]
Cos_Connect_Config = config.Config["CosConfig"]["Connect_Config"]
if Cos_Connect_Config["SecretId"] != "" and Cos_Connect_Config["SecretKey"] != "" and Cos_Connect_Config["Region"] != "":
    logger.info("正在尝试登录Cos")
    try:
        Cos_Tools = cos_tools(
            secret_id=Cos_Connect_Config["SecretId"],
            secret_key=Cos_Connect_Config["SecretKey"],
            region=Cos_Connect_Config["Region"],
            token=Cos_Connect_Config["Token"] == "" if None else Cos_Connect_Config["Token"],
            SSL=bool(Cos_Connect_Config["SSL"])
        )
    except CosClientError as err:
        logger.error(f"尝试Cos登录时发生错误：{err}")
    else:
        logger.success("Cos登录成功")
else:
    logger.debug("缺少必要参数，将不会激活Cos")
