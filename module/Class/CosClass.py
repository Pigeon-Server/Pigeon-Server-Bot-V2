from module.BasicModule.Logger import logger
from qcloud_cos import CosConfig, CosS3Client
from qcloud_cos.cos_exception import CosClientError, CosServiceError
from qcloud_cos.cos_comm import CiDetectType
from module.Class.ExceptionClass import IncomingParametersError, NoKeyError
from os.path import exists, split, join
from typing import Union


class CosClass:  # Cos属于付费接口，尽量少调用
    __ConnectConfig = None
    __client = None
    __Bucket: str
    __Path: str
    connected: bool = False

    def __init__(self, SecretId: str, SecretKey: str, region: str, Bucket: str, Path: str,
                 token: Union[str, None] = None,
                 SSL: bool = True, proxies: bool = False, agentAddress: dict = None) -> None:

        """
        构造函数\n
        Args:
            SecretId: 用户的SecretId
            SecretKey: 用户的SecretKey
            region: 用户的region
            Bucket: 要使用的储存桶列表
            Path: 上传到储存桶的路径
            token: 如果使用永久密钥不需要填入token，如果使用临时密钥需要填入,默认为None，可不填
            SSL: 指定使用 http/https 协议来访问 COS，默认为 https，可不填
            proxies: 是否使用代理，默认不使用
            agentAddress: 代理地址，只当启用代理的时候才用传入
        """

        scheme = 'https' if SSL else 'http'
        if proxies:
            if not isinstance(agentAddress, dict) or agentAddress is None:
                raise IncomingParametersError("需要一个字典类型的代理配置")
            else:
                if scheme == "https":
                    if "https" not in agentAddress.keys():
                        raise NoKeyError("无法在代理配置里面找到https代理地址")
                elif scheme == "http":
                    if "http" not in agentAddress.keys():
                        raise NoKeyError("无法在代理配置中找到http代理地址")
                self.__ConnectConfig = CosConfig(
                    Region=region,
                    SecretId=SecretId,
                    SecretKey=SecretKey,
                    Token=token,
                    Scheme=scheme,
                    Proxies=agentAddress
                )
        else:
            self.__ConnectConfig = CosConfig(
                Region=region,
                SecretId=SecretId,
                SecretKey=SecretKey,
                Token=token,
                Scheme=scheme
            )
        self.__Bucket = Bucket
        self.__Path = Path

    def Connect(self) -> None:

        """
        连接到cos\n
        """

        logger.debug("正在连接到cos")
        try:
            self.__client = CosS3Client(self.__ConnectConfig)
            self.connected = True
            logger.success("成功连接到cos")
        except CosServiceError as error:
            logger.error(f"连接cos失败: {error}")
        except CosClientError as error:
            logger.error(f"连接cos失败: {error}")

    def UploadFile(self, files: list, Bucket: str = None, Path: str = None, EnableMD5: bool = False) -> list:

        """
        上传文件至cos\n
        Args:
            files: 要上传的文件列表
            Bucket: 使用的储存桶，不传入时使用构造时传入的储存桶
            Path: 存储到cos的路径，不传入时使用构造时传入的路径
            EnableMD5: 是否在上传时计算md5, 默认不计算
        """

        Bucket = self.__Bucket if Bucket is None else Bucket
        Path = self.__Path if Path is None else Path
        SuccessList: list = []
        if not isinstance(files, list):
            raise IncomingParametersError("传入的files参数不是一个列表")
        for file in files:
            if exists(file):  # 判断本地文件是否存在
                if not self.__client.object_exists(Bucket, Key=f"{Path}/{split(file)[-1]}"):  # 判断Cos上是否存在该文件
                    for i in range(0, 3):  # 使用高级接口断点续传，失败重试时不会上传已成功的分块(这里重试3次)
                        try:
                            response = self.__client.upload_file(
                                Bucket=Bucket,
                                LocalFilePath=file,  # 本地文件的路径
                                Key=f"{Path}/{split(file)[-1]}",  # 上传到桶之后的文件名
                                PartSize=1,  # 分块大小
                                MAXThread=10,  # 支持最多的线程数
                                EnableMD5=EnableMD5  # 是否计算md5
                            )
                            logger.debug(response['ETag'])
                            SuccessList.append(join(Path, file.rsplit("/")[-1]))
                            break
                        except CosClientError or CosServiceError as err:
                            logger.error(f"第[{i}]次上传文件发生错误：{err}")
                else:
                    logger.info(f"{file}已在Cos存在")
            else:
                logger.error("文件不存在：" + file)
        return SuccessList

    def DelFile(self, Bucket: str, files: list, VersionId=None) -> list:

        """
        删除cos中的文件\n
        Args:
            Bucket: 使用的储存桶，不传入时使用构造时传入的储存桶
            files: 要删除的文件列表
            VersionId: 指定删除的版本
        """

        Bucket = self.__Bucket if Bucket is None else Bucket
        SuccessList: list = []
        for file in files:
            respond = self.__client.delete_object(
                Bucket=Bucket,
                Key=file
            ) if VersionId is None else self.__client.delete_object(
                Bucket=Bucket,
                Key=file,
                VersionId=VersionId
            )
            if respond.get("x-cos-delete-marker"):
                SuccessList.append(file)
                if VersionId is True:
                    logger.debug(f"删除{file}成功，版本：{respond.get('x-cos-version-id')}")
                else:
                    logger.debug(f"删除{file}成功")
            else:
                logger.debug(f"删除{file}失败")
        return SuccessList

    def Get_File_URL(self, file, Bucket=None):

        """
        获取存储桶中文件访问URL
        Args:
            file:文件名
            Bucket:使用的储存桶，不传入时使用构造时传入的储存桶
        """

        Bucket = self.__Bucket if Bucket is None else Bucket
        if self.__client.object_exists(Bucket, Key=file):
            return self.__client.get_object_url(Bucket, Key=file)
        else:
            return False

    def Files_Content_Recognition(self, Files: list, BizType: str, Interval=3, MaxFrames=5, Bucket=None, Compression=False):
        """
        :param Bucket: 存储桶
        :param Files: 文件名列表，如果文件名为URL将无需填写存储桶
        :param BizType: 审核策略的唯一标识，由后台自动生成，在控制台中对应为 Biztype 值。
        :param Interval: 审核 GIF 动图时，可使用该参数进行截帧配置，代表截帧的间隔。例如值设为5，则表示从第1帧开始截取，每隔5帧截取一帧，默认值3。
        :param MaxFrames: 针对 GIF 动图审核的最大截帧数量，需大于0。例如值设为5，则表示最大截取5帧，默认值为5。
        :param Compression: 对于超过大小限制的图片是否进行压缩后再审核，取值为： False（不压缩），True（压缩）。默认为0。注：压缩最大支持32MB的图片，且会收取图片压缩费用。对于 GIF 等动态图过大时，压缩时间较长，可能会导致审核超时失败。
        :return:
        file_name:{
            response:response
        }
        """
        Bucket = self.__Bucket if Bucket is None else Bucket
        Compression = 1 if Compression else 0
        response = {}
        for file_name in Files:
            try:
                if file_name[:4] in "http":
                    Temp_response = self.__client.get_object_sensitive_content_recognition(
                        Bucket=Bucket,
                        Key=None,
                        DetectUrl=file_name,
                        BizType=BizType,
                        Interval=Interval,
                        MaxFrames=MaxFrames,
                        LargeImageDetect=Compression
                    )
                    response[file_name] = Temp_response
                else:
                    file_name = f"{self.__Path}/{file_name}"
                    if self.__client.object_exists(Bucket, Key=file_name):
                        Temp_response = self.__client.get_object_sensitive_content_recognition(
                            Bucket=Bucket,
                            Key=file_name,
                            BizType=BizType,
                            Interval=Interval,
                            MaxFrames=MaxFrames,
                            LargeImageDetect=Compression
                        )
                        response[file_name] = Temp_response
                    else:
                        logger.error(f"文件{file_name}不存在")
            except:
                response.update(file_name)
                response[file_name] = False
                logger.error(f"{file_name}审核失败")
        return response
