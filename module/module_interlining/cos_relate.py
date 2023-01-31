from module.module_base.config import main_config, module_config
from module.module_class.cos_class import CosClass
from module.module_class.folder_manager_class import FolderManagerClass

if module_config.cos_client:
    cos_config = main_config.cos_config
    connect_config = main_config.cos_config.connect_config
    cos_client = CosClass(secret_id=connect_config.secret_id, secret_key=connect_config.secret_key,
                          region=connect_config.region, bucket=cos_config.bucket, path=cos_config.path,
                          token=None if connect_config.token == "" else connect_config.token, SSL=connect_config.SSL,
                          proxies=cos_config.enable_agent,
                          agent_address=cos_config.agent_address if cos_config.enable_agent else None)
    cos_client.connect()

    if module_config.download_images and module_config.packing_images:
        fmc = FolderManagerClass("images", r"./image", True, main_config.timer.timer_time, main_config.timer.timer_type, upload=module_config.upload_images, cos_client=cos_client)
