import pymysql
from module.BasicModule.Logger import logger

class DataBase:

    """数据库类"""

    __DBName: str
    __DBHost: str
    __DBUserName: str
    __DBUserPasswd: str
    __DBPort: int
    __DataBase: pymysql.connections.Connection

    def __init__(self, dateBaseName: str = "database", host: str = "127.0.0.1", userName: str = "root", passwd: str = "password", port: int = 3306):

        """
        构造函数\n
        :param port: 数据库端口(int) default: 3306
        :param dateBaseName: 数据表名称(str)
        :param host: 主机地址(str) default: 127.0.0.1
        :param userName: 数据库用户名(str) default: root
        :param passwd: 数据库密码(str)
        """

        self.__DBHost = host
        self.__DBName = dateBaseName
        self.__DBUserPasswd = passwd
        self.__DBUserName = userName
        self.__DBPort = port

    def GetConnectionInfo(self) -> pymysql.connections.Connection:

        """
        获取数据库连接对象\n
        :return: pymysql.connections.Connection
        """

        return self.__DataBase

    def Connect(self) -> None:

        """
        连接数据库\n
        :return: None
        """
        logger.debug("正在连接到数据库...")
        try:
            dataBase = pymysql.connect(
                host=self.__DBHost,
                user=self.__DBUserName,
                password=self.__DBUserPasswd,
                database=self.__DBName,
                port=self.__DBPort,
                autocommit=1
            )
            cursor = dataBase.cursor()
            cursor.execute("SELECT VERSION()")
            data = cursor.fetchone()
            logger.success("成功连接到数据库")
            logger.debug("数据库版本 : %s " % data)
            self.__DataBase = dataBase
        except:
            logger.error("无法连接到数据库")
            exit()
