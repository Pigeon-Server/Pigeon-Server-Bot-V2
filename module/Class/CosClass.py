from module.BasicModule.Logger import logger
from qcloud_cos import CosConfig, CosS3Client
from qcloud_cos.cos_exception import CosClientError, CosServiceError
from module.Class.ExceptionClass import IncomingParametersError, NoKeyError
from os.path import exists, split, join
from typing import Union

class CosClass:  # Cos属于付费接口，尽量少调用
    __ConnectConfig = None
    __client = None
    __Bucket: str
    __Path: str
    connected: bool = False

    def __init__(self, SecretId: str, SecretKey: str, region: str, Bucket: str, Path: str, token: Union[str, None] = None,
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


