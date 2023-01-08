from enum import Enum
from json import load, dumps
from os import mkdir
from os.path import exists
from typing import Union, Optional

from module.module_class.exception_class import NoKeyError


class DataType(Enum):
    """枚举类，用来转换类型和数字"""
    STR = 1
    INT = 2
    FLOAT = 3
    LIST = 4
    DICT = 5


class JsonDataBaseCLass:
    _database_name: str
    _data_type: int
    stored_data: list | dict = None

    def __init__(self, file_name: str, data_type: int) -> None:
        """
        类构造函数\n
        Args:
            file_name: 要使用的文件名，应该位于data文件夹下，如果不存在会自动创建
            data_type: 文件内存储的格式 1:str 2:int 3: float 4: list: 5: dict 除了dict外，其他类型均为list存储
        """
        self._database_name = file_name
        self._data_type = data_type
        if not exists("data"):
            mkdir("data")
        if exists(f"data/{file_name}"):
            self.stored_data = load(open(f"data/{file_name}", "r", encoding="UTF-8", errors="ignore"))
        else:
            if DataType(data_type) == DataType.DICT:
                file = open(f"data/{file_name}", 'w')
                file.write("{}")
                file.close()
                self.stored_data = {}
            else:
                file = open(f"data/{file_name}", 'w')
                file.write("[]")
                file.close()
                self.stored_data = []

    def edit_data(self, data: Union[str, int, float, list, dict], target: Optional[str] = None, del_data: bool = False) -> bool:
        """
        编辑数据, 可添加可删除\n
        可编辑受限制：\n
        int float str list 四种存储类型无target属性，只有一层深度，均有delData属性\n
        dict 存储类型有target属性，当第一层为list类型时有delData属性\n
        注意，dict套dict时仅支持传入dict类型的参数进行修改，其他参数将会抛出错误\n
        Args:
            data: 要修改或删除的数据
            target: 要修改的键名，仅当存储类型为dict的时候需要传入
            del_data: 是否为删除模式，当存储类型为dict以外的四种类型或存储类型为dict且target下为list类型时生效
        Return:
            bool: True 成功  False 失败
        """
        backupData = self.stored_data
        if DataType(self._data_type) == DataType.DICT and target is None:
            raise NoKeyError("未指定修改的键值")
        elif DataType(self._data_type) == DataType.DICT and target is not None:
            if target not in self.stored_data.keys():
                if not del_data:
                    self.stored_data[target] = data
            else:
                tempData = self.stored_data[target]
                if isinstance(tempData, list):
                    self.stored_data[target].remove(data) if del_data else self.stored_data[target].append(data)
                elif isinstance(tempData, str) or isinstance(tempData, int) or isinstance(tempData, float):
                    self.stored_data[target] = data
                elif isinstance(tempData, dict):
                    if isinstance(data, dict):
                        self.stored_data[target] = data
                    else:
                        raise RuntimeError("不支持此类修改")
        if DataType(self._data_type) == DataType.DICT:
            try:
                self.write_data()
                return True
            except:
                self.stored_data = backupData
                self.write_data()
                return False
        else:
            try:
                self.stored_data.remove(data) if del_data else self.stored_data.append(data)
                self.write_data()
                return True
            except:
                self.stored_data = backupData
                self.write_data()
                return False

    def reload_data(self) -> None:
        """
        重新从文件加载数据\n
        """
        self.stored_data = load(open(f"data/{self._database_name}", "r", encoding="UTF-8", errors="ignore"))

    def write_data(self) -> None:
        """
        将本地缓存的内容写入文件\n
        """
        with open(f"data/{self._database_name}", 'w', encoding="UTF-8") as file:
            file.write(dumps(self.stored_data, indent=4, ensure_ascii=False))

    def query_data(self, data: Union[str, int, float, list, dict], target: Optional[str] = None) -> bool:
        """
        查询数据\n
        查询限制：\n
        int str float list 四种存储类型无target属性,查询无限制,均可查询\n
        dict 存储类型有target属性\n
        注意，当第一层为dict类型时无法查询，且会抛出错误\n
        Args:
            data: 查询的数据
            target: 要查询的键名，仅当存储类型为dict的时候需要传入
        Return:
            bool: True 成功  False 失败
        """
        if DataType(self._data_type) == DataType.DICT:
            if target is None:
                raise NoKeyError("未指定查询的键值")
            elif target not in self.stored_data.keys():
                return False
            else:
                tempData = self.stored_data[target]
                if isinstance(tempData, list):
                    return True if data in tempData else False
                elif isinstance(tempData, str) or isinstance(tempData, int):
                    return True if data == tempData else False
                elif isinstance(tempData, float):
                    return True if abs(tempData - data) <= 0.000000000000001 else False
                elif isinstance(tempData, dict):
                    raise RuntimeError("不支持此类型的查询")
        else:
            return True if data in self.stored_data else False

