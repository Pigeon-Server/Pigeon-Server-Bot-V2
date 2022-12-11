from pathlib import Path
from typing import Union, Optional
from json5.lib import load
from module.module_base.logger import logger


class ConfigTools:
    @staticmethod
    def load_config(filename: str, obj_target: Optional[object] = None) -> Union[dict, list, object]:
        """
        加载config\n
        Args:
            filename: 要加载的配置文件名(str)
            obj_target: 传入实例化对象
        Return:
            object: 实例化对象
        """
        if not Path("config/" + filename).is_file():
            logger.error(f"{filename}配置文件不存在")
        else:
            try:
                return load(open(f"config/{filename}", "r", encoding="UTF-8",
                                 errors="ignore")) if obj_target is None else load(
                    open(f"config/{filename}", "r", encoding="UTF-8", errors="ignore"), object_hook=obj_target)
            except:
                logger.error(f"{filename}已损坏")


class ConnectConfig:
    secret_id: str
    secret_key: str
    region: str
    token: str
    SSL: bool


class CosConfig:
    biz_type: str
    bucket: str
    path: str
    enable_agent: bool
    agent_address: bool
    connect_config: ConnectConfig


class DataBaseConfig:
    host: str
    password: str
    username: str
    database_name: str
    port: int


class GroupConfig:
    admin_group: int
    player_group: int


class MiraiHTTP:
    host: str
    key: str
    port: int
    sync_id: str
    single_mode: bool


class MiraiBotConfig:
    qq: int
    connect_type: str
    websocket_port: int
    group_config: GroupConfig
    mirai_http: MiraiHTTP


class WebsocketConfig:
    host: str
    port: int


class MCSMConfig:
    api_key: str
    api_url: str
    update_time: int


class Permission:
    default: str
    common: str
    ban: str


class PassConfig:
    pass_min_level: int
    pass_min_age: int
    join_group_answer_keyword_review: bool
    signature_refuse_keyword: bool
    auto_pass_manual_audit: bool
    auto_refuse_manual_audit: bool


class AuditConfig:
    pass_all: bool
    refuse_all: bool
    manual_audit_all: bool
    pass_config: PassConfig


class JoinGroupAnswerKeyword:
    pass_keywords: list
    refuse_keywords: dict


class KeyWordConfig:
    join_group_answer_keyword: JoinGroupAnswerKeyword
    signature_refuse_keyword: list


class GroupUnit:
    audit_config: AuditConfig
    keyword_config: KeyWordConfig


class ConfigInit:
    config_version: str
    info_limit: int
    cos_config: CosConfig
    database_config: DataBaseConfig
    mirai_bot_config: MiraiBotConfig
    websocket_config: WebsocketConfig
    server_list: object
    update_check_interval: int
    welcome_message: str
    mcsm_config: MCSMConfig
    permission: Permission
    automatic_config: dict[object]

    def __init__(self, json):
        self.__dict__ = json


class RconConfig:
    rcon_host: str
    rcon_password: str
    rcon_port: int


class Whitelist:
    add: str
    delete: str


class Ban:
    add: str
    delete: str


class Bot:
    delete: str


class VanillaCommand:
    whitelist: Whitelist
    ban: Ban
    bot: Bot


class VanillaServer:
    server_name: str
    rcon_config: RconConfig
    command: VanillaCommand


class ServerConfigInit:
    vanilla_server: VanillaServer

    def __init__(self, json):
        self.__dict__ = json


class ModuleConfigInit:
    websocket_report: bool
    image_review: bool
    black_list: bool
    white_list: bool
    block_word: bool
    questions: bool
    shutup: bool
    online: bool
    automatic_review: bool
    debug_mode: bool
    mcsm_module: bool
    check_mc_update: bool
    tps: bool

    def __init__(self, json):
        self.__dict__ = json
