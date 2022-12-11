from module.module_class.whitelist_class import WhitelistClass
from module.module_class.server_class import MinecraftServer
from module.module_base.config import main_config, module_config
from module.module_class.server_status_class import ServerStatus
from module.module_class.blacklist_class import BlackListClass
from module.module_class.query_class import QueryClass
from module.module_class.mcsm_class import MCSMClass
from module.module_base.logger import logger
from asyncio.runners import run
from sys import exit

vanilla_server = None
if module_config.white_list or module_config.black_list:
    from module.module_base.config import server_config
    try:
        vanilla_server = MinecraftServer(server_config.vanilla_server.server_name, vars(server_config.vanilla_server.rcon_config), vars(server_config.vanilla_server.command))
        run(vanilla_server.test_connection())
    except:
        logger.error("初始化服务器发生错误")
        exit()
if module_config.white_list and vanilla_server is not None:
    whitelist = WhitelistClass(vanilla_server)
if module_config.black_list and vanilla_server is not None:
    blacklist = BlackListClass(vanilla_server)
if module_config.online:
    server = ServerStatus(vars(main_config.server_list))
if module_config.mcsm_module:
    MCSM = MCSMClass(main_config.mcsm_config.api_key, main_config.mcsm_config.api_url)
query = QueryClass()
