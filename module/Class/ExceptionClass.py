class CustomError(Exception):
    info: str

    def __init__(self):
        super().__init__(self)
        self.info = "未知错误"

    def __str__(self):
        return self.info

class IncomingParametersError(CustomError):
    def __init__(self, info: str = "传入的参数类型不正确"):
        super(IncomingParametersError, self).__init__()
        self.info = info

class CommandNotFoundError(CustomError):
    def __init__(self, info: str = "无法找到对应命令"):
        super(CommandNotFoundError, self).__init__()
        self.info = info

class ConnectionTypeError(CustomError):
    def __init__(self, info: str = "不支持的连接方式"):
        super(ConnectionTypeError, self).__init__()
        self.info = info

class NoParametersError(CustomError):
    def __init__(self, info: str = "未传入参数"):
        super(NoParametersError, self).__init__()
        self.info = info

class ConnectServerError(CustomError):
    def __init__(self, info: str = "连接到服务器出错"):
        super(ConnectServerError, self).__init__()
        self.info = info

class WebsocketUrlError(CustomError):
    def __init__(self, info: str = "无效的连接地址"):
        super(WebsocketUrlError, self).__init__()
        self.info = info

class NoKeyError(CustomError):
    def __init__(self, info: str = "无法找到字典的键值"):
        super(NoKeyError, self).__init__()
        self.info = info
