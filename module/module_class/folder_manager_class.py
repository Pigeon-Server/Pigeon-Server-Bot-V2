from os.path import exists, join
from os import mkdir, listdir, remove
from enum import Enum
from typing import Union, Optional
from module.module_class.cos_class import CosClass
from module.module_class.exception_class import IncomingParametersError
from re import match as rematch
from zipfile import ZipFile
from time import localtime, time, strftime, sleep
from module.module_base.logger import logger
from threading import Thread


class IntervalType(Enum):
    INTERVAL = "interval"  # 表明间隔多少秒执行一次
    TIMING = "timing"  # 表明每天的什么时候执行一次


class FolderManagerClass:
    _name: str
    _path: str
    _compression: bool
    _interval_time: int
    _interval_type: IntervalType
    _time: Optional[int] = None
    _hour: Optional[int] = None
    _minute: Optional[int] = None
    _second: Optional[int] = None
    _unload_to_cos: bool = False
    _cos_client: Optional[CosClass] = None
    _stop_tip: bool = False

    def __init__(self, name: str, path: str, compression: bool = False, interval: Union[int, str] = "0:0:0",
                 interval_type: IntervalType = "timing", upload: bool = False, cos_client: CosClass = None):
        if not exists(path):
            mkdir(path)
        self._name = name
        self._path = path
        self._compression = compression
        self._unload_to_cos = upload
        self._cos_client = cos_client
        if isinstance(interval, int):
            if interval_type == IntervalType.INTERVAL:
                self._time = interval
            else:
                raise IncomingParametersError("参数interval类型错误")
        elif isinstance(interval, str):
            self._decode_time(interval, interval_type)
        else:
            raise IncomingParametersError("参数interval类型错误")
        self._interval_type = interval_type

    def _decode_time(self, message: str, type_: IntervalType) -> None:
        """
        解析计时器\n
        Args:
            message: 要解析的信息
            type_: 计时器类型
        """
        timestamp: bool = False  # 表明间隔多少秒执行一次 "interval"
        time_: bool = False  # 表明每天的什么时候执行一次 "timing"
        if rematch(r"(^(2[0-3]|[0-1]\d|\d):([0-5]\d|\d))(:([0-5]\d|\d))?$", message) is not None:
            time_ = True
        if rematch(r"^(\d{1,2}d)?((2[0-3]|[0-1]\d|\d)h)?(([0-5]\d|\d)m)?(([0-5]\d|\d)s)?$", message) is not None:
            timestamp = True
        if (not time_ and not timestamp) or (time_ and timestamp):
            raise IncomingParametersError("参数message格式错误")
        if (time_ and type_ == IntervalType.INTERVAL) or \
                (timestamp and type_ == IntervalType.TIMING):
            raise IncomingParametersError("给定值与设定的模式不匹配")
        if timestamp:
            self._time = 0
            if 'd' in message:
                self._time += 86400 * int(message[:message.find('d')])
                message = message[message.find('d') + 1:]
            if 'h' in message:
                self._time += 3600 * int(message[:message.find('h')])
                message = message[message.find('h') + 1:]
            if 'm' in message:
                self._time += 60 * int(message[:message.find('m')])
                message = message[message.find('m') + 1:]
            if 's' in message:
                self._time += int(message[:-1])
            return
        if time_:
            if rematch("(^(2[0-3]|[0-1]\\d|\\d):([0-5]\\d|\\d))$", message) is not None:
                self._hour = int(message[:message.find(":")])
                message = message[message.find(":") + 1:]
                self._minute = int(message)
                self._second = 0
            else:
                self._hour = int(message[:message.find(":")])
                message = message[message.find(":") + 1:]
                self._minute = int(message[:message.find(":")])
                message = message[message.find(":") + 1:]
                self._second = int(message)
            return

    def start(self) -> None:
        """
        开始计时\n
        """
        def interval():
            logger.debug(f"计时器开始运行,每隔{self._time}s执行一次")
            while True:
                sleep(self._time)
                logger.debug("计时器执行")
                self._compress()
                if self._stop_tip:
                    break

        def timing():
            target_time = ""
            if self._hour < 10:
                target_time += f"0{self._hour}:"
            else:
                target_time += f"{self._hour}:"
            if self._minute < 10:
                target_time += f"0{self._minute}:"
            else:
                target_time += f"{self._minute}:"
            if self._second < 10:
                target_time += f"0{self._second}"
            else:
                target_time += f"{self._second}"
            logger.debug(f"计时器开始运行,每天{target_time}执行")
            finished = False
            while True:
                sleep(1)
                if finished:
                    finished = False
                if target_time == strftime("%H:%M:%S", localtime(time())) and not finished:
                    logger.debug("计时器执行")
                    self._compress()
                    finished = True
                if self._stop_tip:
                    break

        self._stop_tip = False
        if self._interval_type == IntervalType.INTERVAL:
            Thread(target=interval).start()
        else:
            Thread(target=timing).start()

    def _compress(self) -> None:
        """
        打包压缩文件\n
        """
        file_list = listdir(self._path)
        file_name = strftime(f"{self._name}_%Y_%m_%d_%H_%M_%S.zip", localtime(time()))
        zipfile = ZipFile(join(self._path, file_name), "w")
        for item in file_list:
            if not item.endswith("zip"):
                zipfile.write(join(self._path, item))
        zipfile.close()
        file_list = listdir(self._path)
        for item in file_list:
            if not item.endswith("zip"):
                remove(join(self._path, item))
        if self._unload_to_cos:
            self._upload(file_name)

    def _upload(self, file_name: str) -> None:
        """
        上传文件到cos\n
        Args:
            file_name: 文件路径
        """
        self._cos_client.upload_file([file_name])

    def stop(self) -> None:
        """
        停止计时
        """
        self._stop_tip = True
