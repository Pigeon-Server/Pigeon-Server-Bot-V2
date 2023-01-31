import pymysql
from module.module_base.logger import logger


class DataBase:

    """数据库类"""

    _database_name: str
    _database_host: str
    _database_username: str
    _database_password: str
    _database_port: int
    _database_connection: pymysql.connections.Connection

    def __init__(self, database_name: str = "database", host: str = "127.0.0.1", user_name: str = "root", passwd: str = "password", port: int = 3306):

        """
        构造函数\n
        :param port: 数据库端口(int) default: 3306
        :param database_name: 数据表名称(str)
        :param host: 主机地址(str) default: 127.0.0.1
        :param user_name: 数据库用户名(str) default: root
        :param passwd: 数据库密码(str)
        """

        self._database_host = host
        self._database_name = database_name
        self._database_password = passwd
        self._database_username = user_name
        self._database_port = port

    def get_connection_info(self) -> pymysql.connections.Connection:

        """
        获取数据库连接对象\n
        :return: pymysql.connections.Connection
        """

        return self._database_connection

    def connect(self) -> None:

        """
        连接数据库\n
        :return: None
        """
        logger.debug("正在连接到数据库...")
        try:
            dataBase = pymysql.connect(
                host=self._database_host,
                user=self._database_username,
                password=self._database_password,
                database=self._database_name,
                port=self._database_port,
                autocommit=1
            )
            cursor = dataBase.cursor()
            cursor.execute("SELECT VERSION()")
            data = cursor.fetchone()
            logger.success("成功连接到数据库")
            logger.debug("数据库版本 : %s " % data)
            self._database_connection = dataBase
        except:
            logger.error("无法连接到数据库")
            exit()
