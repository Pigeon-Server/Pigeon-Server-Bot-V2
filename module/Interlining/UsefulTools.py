from module.BasicModule.config import config

def IsAdminGroup(Group: str) -> bool:

    """
    判断所给出的是否是管理员群\n
    :param Group: 群号
    :return: true/false
    """

    return Group == config.Config["MiraiBotConfig"]["GroupConfig"]["AdminGroup"]

def IsPlayerGroup(Group: str) -> bool:

    """
    判断所给出的是否是玩家群\n
    :param Group: 群号
    :return: true/false
    """

    return Group == config.Config["MiraiBotConfig"]["GroupConfig"]["PlayerGroup"]
