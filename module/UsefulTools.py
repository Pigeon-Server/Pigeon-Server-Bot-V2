from module.BasicModule.Config import config

def IsAdminChannel(id: str) -> bool:
    """
    判断是否是管理员频道\n
    :param id: 频道id
    :return: True/False
    """
    return id == config["channel"]["admin"]

def IsPlayerChannel(id: str) -> bool:
    """
    判断是否是玩家频道\n
    :param id: 频道id
    :return: True/False
    """
    return id == config["channel"]["player"]

