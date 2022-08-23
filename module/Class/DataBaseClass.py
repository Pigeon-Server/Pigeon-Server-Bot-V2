import pymysql
from module.BasicModule.Logger import logger

class DataBase:

    """数据库类"""

    __DBName = ""
    __DBHost = ""
    __DBUserName = ""
    __DBUserPasswd = ""
    __DBPort = 0
    __DataBase = None

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

    def Ping(self) -> None:
        """
        测试数据库连接/n
        :return: None
        """
        self.__DataBase.ping(reconnect=True)

    def GetConfig(self) -> dict:

        """
        获取数据库配置信息\n
        :return: { "Host": str,"Name": str,"UserName": str,"PassWord": str,"Port": int}
        """

        return {
            "Host": self.__DBHost,
            "Name": self.__DBName,
            "UserName": self.__DBUserName,
            "PassWord": self.__DBUserPasswd,
            "Port": self.__DBPort
        }

    def changeConfig(self, dateBaseName: str, host: str, userName: str, passwd: str, port: int = 3306) -> None:

        """
        修改配置\n
        :param port: 数据库端口(int) default: 3306
        :param dateBaseName: 数据表名称(str)
        :param host: 主机地址(str)
        :param userName: 数据库用户名(str)
        :param passwd: 数据库密码(str)
        :return: None
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
        dataBase = pymysql.connect(
            host=self.__DBHost,
            user=self.__DBUserName,
            password=self.__DBUserPasswd,
            database=self.__DBName,
            port=self.__DBPort
        )
        cursor = dataBase.cursor()
        cursor.execute("SELECT VERSION()")
        data = cursor.fetchone()
        logger.success("成功连接到数据库")
        logger.debug("数据库版本 : %s " % data)
        self.__DataBase = dataBase

    async def DataBaseRunCommand(self, sqlCommand: str = None) -> int:

        """
        运行数据库命令\n
        :param sqlCommand: 要执行的数据库命令(str)
        :return: int : 0(success) -1(fail)
        """

        self.Ping()
        try:
            # 执行sql语句
            if sqlCommand is not None:
                self.__DataBase.cursor().execute(sqlCommand)
            # 提交到数据库执行
            self.__DataBase.commit()
            logger.info("[数据库]命令执行成功~")
            return 0
        except:
            # 如果发生错误则回滚
            self.__DataBase.rollback()
            logger.error("[数据库]数据库发生错误，执行失败")
            return -1

    def __del__(self) -> None:

        """
        析构函数\n
        :return: None
        """

        self.__DataBase.commit()
        self.__DataBase.close()
