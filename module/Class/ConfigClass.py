from json5.lib import load
from pathlib import Path
from module.BasicModule.Logger import logger
from typing import Union, Optional


class ConfigTools:
    @staticmethod
    def loadConfig(filename: str, objectTarget: Optional[object] = None) -> Union[dict, list, object]:
        """
        加载config\n
        Args:
            filename: 要加载的配置文件名(str)
            objectTarget: 传入实例化对象
        Return:
            object: 实例化对象
        """
        if not Path("config/" + filename).is_file():
            logger.error(f"{filename}配置文件不存在")
        else:
            try:
                return load(open(f"config/{filename}", "r", encoding="UTF-8",
                                 errors="ignore")) if objectTarget is None else load(
                    open(f"config/{filename}", "r", encoding="UTF-8", errors="ignore"), object_hook=objectTarget)
            except:
                logger.error(f"{filename}已损坏")


class ConnectConfig:
    SecretId: str
    SecretKey: str
    Region: str
    Token: str
    SSL: bool


class CosConfig:
    BizType: str
    Bucket: str
    Path: str
    enableAgent: bool
    agentAddress: bool
    ConnectConfig: ConnectConfig


class DataBaseConfig:
    Host: str
    Password: str
    Username: str
    DatabaseName: str
    Port: int


class GroupConfig:
    AdminGroup: int
    PlayerGroup: int


class MiraiHTTP:
    Host: str
    Key: str
    Port: int
    SyncId: str
    SingleMode: bool


class MiraiBotConfig:
    QQ: int
    ConnectType: str
    WebSocketPort: int
    GroupConfig: GroupConfig
    MiraiHTTP: MiraiHTTP


class WebsocketConfig:
    host: str
    port: int


class Age:
    min: int
    max: int


class AutomaticReview:
    level: int
    age: Age
    Refuse: bool
    BlackList: bool


class MCSMConfig:
    apikey: str
    apiurl: str
    updateTime: int


class Permission:
    default: str
    common: str
    ban: str


class ConfigInit:
    ConfigVersion: str
    infoLimit: int
    CosConfig: CosConfig
    DataBaseConfig: DataBaseConfig
    MiraiBotConfig: MiraiBotConfig
    WebsocketConfig: WebsocketConfig
    ServerList: object
    AutomaticReview: AutomaticReview
    UpdateCheckInterval: int
    WelcomeMessage: str
    MCSMConfig: MCSMConfig
    Permission: Permission

    def __init__(self, json):
        self.__dict__ = json


class RconConfig:
    RconHost: str
    RconPassword: str
    RconPort: int


class Whitelist:
    Add: str
    Del: str


class Ban:
    Add: str
    Del: str


class Bot:
    Del: str


class VanillaCommand:
    Whitelist: Whitelist
    Ban: Ban
    Bot: Bot


class VanillaServer:
    ServerName: str
    RconConfig: RconConfig
    Command: VanillaCommand


class ServerConfigInit:
    VanillaServer: VanillaServer

    def __init__(self, json):
        self.__dict__ = json


class ModuleConfigInit:
    WebsocketReport: bool
    ImageReview: bool
    BlackList: bool
    WhiteList: bool
    BlockWord: bool
    Questions: bool
    Shutup: bool
    Online: bool
    AutomaticReview: bool
    DebugMode: bool
    MCSMModule: bool
    CheckMCUpdate: bool
    TPS: bool

    def __init__(self, json):
        self.__dict__ = json
