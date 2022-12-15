from sys import exit
from time import strftime, localtime
from typing import Optional, Union

from requests import get

from asyncio.tasks import sleep
from module.module_base.logger import logger
from module.module_class.exception_class import IncomingParametersError
from module.module_class.json_database_class import JsonDataBaseCLass


class MCSMClass(JsonDataBaseCLass):
    _api_url: str = None
    _api_key: str = None
    _enable_SSL: bool = True
    _name_to_uuid: dict = None
    _server: dict = None
    _server_list_dict: dict = None

    # 初始化模块
    def __init__(self, apikey: str, url: str = "http://127.0.0.1:23333", enable_ssl: bool = False) -> None:
        """
        Args:
            apikey: API 接口密钥
            url: MCSM网页端后台地址（跨域请求 API 接口须打开）
            enable_ssl: 是否启用ssl连接（注意：如果网页是http访问，则此选项永远为False）
        """
        super().__init__("MCSM.json", 5)
        if not url.startswith("http"):
            raise IncomingParametersError("api地址错误,必须以http或https开头")
        self._enable_SSL = False if url.startswith("http://") else enable_ssl
        self._api_url = url if "/api" in url else f"{url}/api"
        self._api_key = apikey
        self._server = {}
        self.test_connect()

    def test_connect(self) -> None:
        """
        测试到MCSM的连接\n
        """
        try:
            self._call_api("overview")
        except RuntimeError as err:
            logger.error(err)
            exit()
        except ConnectionError:
            logger.error("无法访问MCSM，请检查网络和url设置是否出错")
            exit()
        except:
            logger.error("发生未知错误")
            exit()

    # 基础模块
    def _call_api(self, path: str, parameters: Optional[dict] = None, log: bool = True) -> dict:
        """
        对API发起请求\n
        Args:
            path: api路径
            parameters: 需要在请求中额外添加的参数（除apikey以外的参数）
            log: 是否输出访问信息
        Returns:
            dict: 返回api返回的内容(dict)没有访问成功则抛出异常
        """
        if path.startswith("/api"):
            url = f"{self._api_url}{path[4:]}"
        elif path.startswith("api"):
            url = f"{self._api_url}{path[3:]}"
        elif path.startswith("/"):
            url = f"{self._api_url}{path}"
        else:
            url = f"{self._api_url}/{path}"
        parameter = {
            "apikey": self._api_key
        }
        if parameters is not None:
            if isinstance(parameters, dict):
                parameter.update(parameters)
            else:
                raise ValueError("请求参数错误！")
        if log:
            logger.debug(f"尝试请求api{url}")
        res = get(url=url, headers={"Content-Type": "application/json; charset=utf-8"},
                  params=parameter, timeout=10, verify=self._enable_SSL).json()
        match res.get("status"):
            case 200:
                return res
            case 403:
                logger.error("访问被拒绝，apikey错误")
                raise RuntimeError("访问被拒绝，apikey错误")
            case 400:
                logger.error("请求参数不正确")
                raise RuntimeError("请求参数不正确")
            case 500:
                logger.error("服务器内部错误")
                raise RuntimeError("服务器内部错误")

    def get_mcsm_info(self, force_load: bool = False) -> None:
        """
        获取当前面板下所有守护进程UUID以及所有实例名
        Args:
            force_load: 是否强制刷新已储存的uuid
        """
        backup = self.stored_data
        try:
            try:
                data = self._call_api("service/remote_services_list").get("data")
            except RuntimeError as err:
                logger.error(err)
                raise RuntimeError
            else:
                if force_load:
                    self.stored_data = {}
                self._server = {}
                for item in data:
                    if item["uuid"] in self.stored_data.keys():
                        self._server[item["uuid"]] = {"name": self.stored_data[item["uuid"]][item["uuid"]],
                                                       "instances": {}}
                    else:
                        self.stored_data[item["uuid"]] = {item["uuid"]: item["remarks"]}
                        self._server[item["uuid"]] = {"name": item["remarks"], "instances": {}}
                try:
                    data = self._call_api("service/remote_services").get("data")
                except RuntimeError as err:
                    logger.error(err)
                    raise RuntimeError
                else:
                    for item in data:
                        nameDict = self.stored_data[item["uuid"]]
                        for raw in item["instances"]:
                            if raw["instanceUuid"] in nameDict.keys():
                                self._server[item["uuid"]]["instances"][raw["instanceUuid"]] = {
                                    "name": nameDict[raw["instanceUuid"]], "status": raw["status"]}
                            else:
                                self.stored_data[item["uuid"]][raw["instanceUuid"]] = raw["config"]["nickname"]
                                self._server[item["uuid"]]["instances"][raw["instanceUuid"]] = {
                                    "name": raw["config"]["nickname"], "status": raw["status"]}
                    self.write_data()
                    self._name_to_uuid_()
        except:
            logger.error("初始化失败")
            self.stored_data = backup
            self.write_data()

    # 状态转换和名称UUID转换
    @staticmethod
    def _status_code(code: int) -> str:
        match code:
            case -1:
                return "状态未知"
            case 0:
                return "已停止"
            case 1:
                return "停止中"
            case 2:
                return "启动中"
            case 3:
                return "运行中"

    def _name_to_uuid_(self) -> None:
        """
        转换名称-uuid映射表\n
        """
        self._name_to_uuid = {}
        self._server_list_dict = {}
        for item in self.stored_data:
            for raw in self.stored_data[item]:
                if raw == item:
                    self._name_to_uuid[self.stored_data[item][raw]] = {"Service": raw}
                else:
                    self._name_to_uuid[self.stored_data[item][item]][self.stored_data[item][raw]] = raw
                    self._server_list_dict[self.stored_data[item][raw]] = item

    def _translate_name_to_uuid(self, name: str) -> str:
        if name in self._name_to_uuid.keys():
            return self._name_to_uuid[name]["Service"]
        else:
            return self._name_to_uuid[self.stored_data[self._server_list_dict[name]][self._server_list_dict[name]]][name]

    def _get_remote_uuid(self, name: str) -> str:
        if name in self._name_to_uuid.keys():
            return self._name_to_uuid[name]["Service"]
        else:
            return self._server_list_dict[name]

    def _is_remote_name(self, name: str) -> int:
        if name in self._server_list_dict.keys():
            return 0
        elif name in self._name_to_uuid.keys():
            return 1
        else:
            return 2

    # 第一次封装
    def _get_instance_info(self, remote_uuid: str, instance_uuid: str, full_data: bool = False, log: bool = True) -> Optional[Union[int, dict]]:
        """
        获取实例状态\n
        Args:
            remote_uuid: 守护进程uuid
            instance_uuid: 实例uuid
            full_data: 是否返回完整结果，如果为False则只返回状态码（默认为False）
            log: 是否输出调试信息
        """
        try:
            try:
                data = self._call_api("/api/instance", {"uuid": instance_uuid, "remote_uuid": remote_uuid}, log)
            except RuntimeError as err:
                logger.error(err)
                return None
            else:
                if full_data:
                    return data
                else:
                    return data.get("data").get("status") if data.get("data").get("instanceUuid") == instance_uuid else None
        except Exception as err:
            logger.error(err)
            return None

    def update_instance_status(self, remote_uuid: Optional[str] = None, instance_uuid: Optional[str] = None) -> None:
        """
        刷新所有守护进程的所有实例的运行状态\n
        刷新某一守护进程的所有实例的运行状态\n
        刷新某一守护进程的某一实例的运行状态\n
        Args:
            remote_uuid: 守护进程uuid，可为空
            instance_uuid: 实例uuid，可为空
        """
        try:
            if remote_uuid is None and instance_uuid is not None:
                raise RuntimeError("传入参数错误")
            if remote_uuid is None and instance_uuid is None:
                for item in self._server:
                    data = self._server[item].get("instances")
                    for raw in data:
                        data[raw]["status"] = self._get_instance_info(item, raw, log=False)
            elif remote_uuid is not None and instance_uuid is None:
                data = self._server[remote_uuid].get("instances")
                for raw in data:
                    data[raw]["status"] = self._get_instance_info(remote_uuid, raw, log=False)
            elif remote_uuid is not None and instance_uuid is not None:
                self._server[remote_uuid].get("instances")[instance_uuid]["status"] = self._get_instance_info(remote_uuid,
                                                                                                              instance_uuid,
                                                                                                              log=False)
        except:
            logger.error("更新实例状态出错")

    # def GetInstanceStatus(self, remoteUUID: str, instanceUUID: str, ReturnStatusCode: bool = False) -> Union[int, str]:
    #     if ReturnStatusCode:
    #         return self._get_instance_info(remoteUUID, instanceUUID)
    #     else:
    #         return self._status_code(self._get_instance_info(remoteUUID, instanceUUID))

    def _check_name(self, remote_name: str = None, instance_name: str = None) -> Union[bool, str]:
        if remote_name is None and instance_name is None:
            return "至少传入一个参数"
        elif remote_name is not None and instance_name is None:
            return True if self._is_remote_name(remote_name) == 1 else f"{remote_name}不是一个有效的守护进程名称"
        elif remote_name is None and instance_name is not None:
            return True if self._is_remote_name(instance_name) == 0 else f"{instance_name}不是一个有效的实例名称"
        elif remote_name is not None and instance_name is not None:
            if self._is_remote_name(remote_name) == 1:
                return True if self._is_remote_name(instance_name) == 0 else f"{instance_name}不是一个有效的实例名称"
            else:
                return f"{remote_name}不是一个有效的守护进程名称"

    def _start_instance(self, remote_uuid: str, instance_uuid: str) -> str:
        match self._get_instance_info(remote_uuid, instance_uuid):
            case -1:
                return "实例状态未知，无法启动"
            case 0:
                try:
                    self._call_api("/api/protected_instance/open", {"uuid": instance_uuid, "remote_uuid": remote_uuid})
                except RuntimeError as err:
                    logger.error(err)
                    return "实例启动失败，api返回异常"
                else:
                    return "执行成功，实例正在启动"
            case 1:
                return "实例正在停止，无法启动"
            case 2:
                return "实例正在启动中，请耐心等待"
            case 3:
                return "实例已在运行"

    def _stop_instance(self, remote_uuid: str, instance_uuid: str, force_kill: bool = False) -> str:
        if force_kill:
            match self._get_instance_info(remote_uuid, instance_uuid):
                case -1:
                    return "实例状态未知，无法关闭"
                case 0:
                    return "实例已停止，无法关闭"
            try:
                self._call_api("/api/protected_instance/kill", {"uuid": instance_uuid, "remote_uuid": remote_uuid})
            except RuntimeError as err:
                logger.error(err)
                return "关闭实例失败，api返回异常"
            else:
                return "执行成功，强制关闭实例"
        else:
            match self._get_instance_info(remote_uuid, instance_uuid):
                case -1:
                    return "实例状态未知，无法关闭"
                case 0:
                    return "实例已停止，无法关闭"
                case 1:
                    return "实例正在停止，无法关闭"
                case 2:
                    return "实例正在启动中，无法关闭"
                case 3:
                    try:
                        self._call_api("/api/protected_instance/stop", {"uuid": instance_uuid, "remote_uuid": remote_uuid})
                    except RuntimeError as err:
                        logger.error(err)
                        return "关闭实例失败，api返回异常"
                    else:
                        return "执行成功，实例正在关闭"

    def _restart_instance(self, remote_uuid: str, instance_uuid: str) -> str:
        match self._get_instance_info(remote_uuid, instance_uuid):
            case -1:
                return "实例状态未知，无法重启"
            case 0:
                return "实例已停止，无法重启"
            case 1:
                return "实例正在停止，无法重启"
            case 2:
                return "实例正在启动中，无法重启"
            case 3:
                try:
                    self._call_api("/api/protected_instance/restart", {"uuid": instance_uuid, "remote_uuid": remote_uuid})
                except RuntimeError as err:
                    logger.error(err)
                    return "重启实例失败，api返回异常"
                else:
                    return "执行成功，实例正在重启"

    def _command(self, instance_uuid: str, remote_uuid: str, command: str) -> float:
        try:
            data = self._call_api("api/protected_instance/command", {
                "remote_uuid": remote_uuid,
                "uuid": instance_uuid,
                "command": command
            })
        except RuntimeError as err:
            logger.error(err)
            raise RuntimeError
        else:
            return data.get("time")/1000

    def _get_command_output(self, instance_uuid: str, remote_uuid: str, time_stamp: float) -> str:
        try:
            data = self._call_api("/api/protected_instance/outputlog", {
                "remote_uuid": remote_uuid,
                "uuid": instance_uuid
            })
        except RuntimeError as err:
            logger.error(err)
            raise RuntimeError
        else:
            temp_list: list = []
            time = strftime("[%H:%M:%S]", localtime(time_stamp))
            data = data["data"].split('\n')
            for item in data:
                if time in item and "[Server thread/INFO]" in item:
                    temp_list.append(item)
            res: str = ""
            for raw in temp_list:
                if raw.find("]: ") != -1:
                    res += f"{raw[raw.find(']: ') + 3:]}\n"
            return res.removesuffix("\n")

    # 第二次封装
    def check_instance_status(self, instance_uuid: str, remote_name: str = None) -> str:
        res = self._check_name(remote_name, instance_uuid)
        if isinstance(res, bool):
            if remote_name is None:
                remote_uuid = self._get_remote_uuid(instance_uuid)
                remote_name = self.stored_data[remote_uuid][remote_uuid]
            else:
                remote_uuid = self._translate_name_to_uuid(remote_name)
            return f"守护进程名称: {remote_name}\n实例名称: {instance_uuid}\n实例运行状态: {self._status_code(self._get_instance_info(remote_uuid, self._translate_name_to_uuid(instance_uuid)))}"
        else:
            return res

    async def run_command(self, instance_name: str, remote_name: str, command: str) -> str:
        res = self._check_name(remote_name, instance_name)
        if isinstance(res, bool):
            instance_uuid = self._translate_name_to_uuid(instance_name)
            remote_uuid = self._translate_name_to_uuid(remote_name)
            status = self._get_instance_info(remote_uuid, instance_uuid)
            if status == 3:
                time_stamp = self._command(instance_uuid, remote_uuid, command)
                await sleep(1)
                return self._get_command_output(instance_uuid, remote_uuid, time_stamp)
            else:
                return f"实例当前状态是:{self._status_code(status)},无法执行命令"
        else:
            return res

    def list_instance(self, remote_name: str = None) -> str:
        result: str = ""
        if remote_name is None:
            for item in self._server:
                result += f"[{self._server[item]['name']}]\n"
                for raw in self._server[item]["instances"]:
                    result += f"{self._server[item]['instances'][raw]['name']} : {self._status_code(self._server[item]['instances'][raw]['status'])}\n"
            return result.removesuffix("\n")
        res = self._check_name(remote_name)
        if isinstance(res, bool):
            remote_uuid = self._translate_name_to_uuid(remote_name)
            result += f"[{remote_name}]\n"
            for raw in self._server[remote_uuid]["instances"]:
                result += f"{self._server[remote_uuid]['instances'][raw]['name']} : {self._status_code(self._server[remote_uuid]['instances'][raw]['status'])}\n"
            return result.removesuffix("\n")
        else:
            return res

    def rename(self, original_name: str, new_name: str) -> str:
        if original_name == new_name:
            return "未更改，与原名一致"
        if new_name in self._name_to_uuid.keys():
            return "未更改，新名字与守护进程名称重复"
        if new_name in self._server_list_dict.keys():
            return "未更改，新名字与实例名称重复"
        match self._is_remote_name(original_name):
            case 0:
                try:
                    remote_uuid = self._server_list_dict[original_name]
                    del self._server_list_dict[original_name]
                    self._server_list_dict[new_name] = remote_uuid
                    instance_uuid = self._name_to_uuid[self._server[remote_uuid]["name"]][original_name]
                    del self._name_to_uuid[self._server[remote_uuid]["name"]][original_name]
                    self._name_to_uuid[self._server[remote_uuid]["name"]][new_name] = instance_uuid
                    self.stored_data[remote_uuid][instance_uuid] = new_name
                    self.write_data()
                    self._server[remote_uuid]["instances"][instance_uuid]["name"] = new_name
                except:
                    return "修改名称失败"
                else:
                    return f"改名成功：\n[{original_name}] -> [{new_name}]"
            case 1:
                try:
                    remote_uuid = self._name_to_uuid[original_name]["Service"]
                    self._name_to_uuid[new_name] = self._name_to_uuid[original_name]
                    del self._name_to_uuid[original_name]
                    self.stored_data[remote_uuid][remote_uuid] = new_name
                    self.write_data()
                    self._server[remote_uuid]["name"] = new_name
                except:
                    return "修改名称失败"
                else:
                    return f"改名成功：\n[{original_name}] -> [{new_name}]"
            case 2:
                return f"{original_name}不是一个有效的守护进程名称或实例名称"

    def stop(self, instance_name: str, remote_name: str = None, force_kill: bool = False) -> str:
        res = self._check_name(remote_name, instance_name)
        if isinstance(res, bool):
            if remote_name is None:
                return self._stop_instance(self._server_list_dict[instance_name], self._translate_name_to_uuid(instance_name), force_kill)
            else:
                return self._stop_instance(self._translate_name_to_uuid(remote_name), self._translate_name_to_uuid(instance_name), force_kill)
        else:
            return res

    def start(self, instance_name: str, remote_name: str = None) -> str:
        res = self._check_name(remote_name, instance_name)
        if isinstance(res, bool):
            if remote_name is None:
                return self._start_instance(self._server_list_dict[instance_name], self._translate_name_to_uuid(instance_name))
            else:
                return self._start_instance(self._translate_name_to_uuid(remote_name), self._translate_name_to_uuid(instance_name))
        else:
            return res

    def restart(self, instance_name: str, remote_name: str = None) -> str:
        res = self._check_name(remote_name, instance_name)
        if isinstance(res, bool):
            if remote_name is None:
                return self._restart_instance(self._server_list_dict[instance_name], self._translate_name_to_uuid(instance_name))
            else:
                return self._restart_instance(self._translate_name_to_uuid(remote_name), self._translate_name_to_uuid(instance_name))
        else:
            return res

# 数据结构备忘
# self.__NameToUUID
# {
#   'Server2': {
#     'Service': '40c4a15d59af40b38c4147340445c1d3',
#     'Velocity': '9fda84e890de4d64bc51ad8ea7633c75'
#   },
#   'Server1': {
#     'Service': 'df473f5da63640b9b4617e4cde3f0a8e',
#     '原版服-1.18.1': '6856f8a753ff4317a1f03f3bee0ae93c'
#   }
# }
# self.__ServerListDict
# {
#   'Velocity': '40c4a15d59af40b38c4147340445c1d3',
#   '原版服-1.18.1': 'df473f5da63640b9b4617e4cde3f0a8e'
# }
# self.__Server
# {
#   '40c4a15d59af40b38c4147340445c1d3': {
#     'name': 'Server2',
#     'instances': {
#       '9fda84e890de4d64bc51ad8ea7633c75': {
#         'name': 'Velocity',
#         'status': 3
#       }
#     }
#   },
#   'df473f5da63640b9b4617e4cde3f0a8e': {
#     'name': 'Server1',
#     'instances': {
#       '6856f8a753ff4317a1f03f3bee0ae93c': {
#         'name': '原版服-1.18.1',
#         'status': 3
#       }
#     }
#   }
# }
# self.Data(存入文件)
# {
#   '40c4a15d59af40b38c4147340445c1d3': {
#     '40c4a15d59af40b38c4147340445c1d3': 'Server2',
#     '9fda84e890de4d64bc51ad8ea7633c75': 'Velocity'
#   },
#   'df473f5da63640b9b4617e4cde3f0a8e': {
#     'df473f5da63640b9b4617e4cde3f0a8e': 'Server1',
#     '6856f8a753ff4317a1f03f3bee0ae93c': '原版服-1.18.1'
#   }
# }
