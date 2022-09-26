from requests import get
from module.BasicModule.Logger import logger
from module.Class.ExceptionClass import IncomingParametersError
from typing import Optional, Union
from sys import exit
from module.Class.JsonDataBaseClass import JsonDataBaseCLass
from time import strftime, localtime


class MCSMClass(JsonDataBaseCLass):
    __apiUrl: str = None
    __apikey: str = None
    __SSL: bool = True
    __NameToUUID: dict = None
    __Server: dict = None
    __ServerListDict: dict = None

    # 初始化模块
    def __init__(self, apikey: str, url: str = "http://127.0.0.1:23333", EnableSSL: bool = False) -> None:
        """
        Args:
            apikey: API 接口密钥
            url: MCSM网页端后台地址（跨域请求 API 接口须打开）
            EnableSSL: 是否启用ssl连接（注意：如果网页是http访问，则此选项永远为False）
        """
        super().__init__("MCSM.json", 5)
        if not url.startswith("http"):
            raise IncomingParametersError("api地址错误,必须以http或https开头")
        if url.startswith("http"):
            self.__SSL = False
        elif url.startswith("https"):
            self.__SSL = EnableSSL
        self.__apiUrl = url if "/api" in url else f"{url}/api"
        self.__apikey = apikey
        self.__Server = {}
        self.TestConnect()

    def TestConnect(self) -> None:
        """
        测试到MCSM的连接\n
        """
        try:
            self.CallApi("overview")
        except RuntimeError as err:
            logger.error(err)
            exit()
        except ConnectionError:
            logger.error("无法访问MCSM，请检查网络和url设置")
            exit()
        except:
            logger.error("发生未知错误")
            exit()

    # 基础模块
    def CallApi(self, Path: str, Parameters: Optional[dict] = None) -> dict:
        """
        对API发起请求\n
        Args:
            Path: api路径
            Parameters: 需要在请求中额外添加的参数（除apikey以外的参数）
        Returns:
            dict: 返回api返回的内容(dict)没有访问成功则抛出异常
        """
        if Path.startswith("/api"):
            url = f"{self.__apiUrl}{Path[4:]}"
        elif Path.startswith("api"):
            url = f"{self.__apiUrl}{Path[3:]}"
        elif Path.startswith("/"):
            url = f"{self.__apiUrl}{Path}"
        else:
            url = f"{self.__apiUrl}/{Path}"
        parameters = {
            "apikey": self.__apikey
        }
        if Parameters is not None:
            if isinstance(Parameters, dict):
                parameters.update(Parameters)
            else:
                raise ValueError("请求参数错误！")
        logger.debug(f"尝试请求api{url}")
        res = get(url=url, headers={"Content-Type": "application/json; charset=utf-8"},
                  params=parameters, timeout=10, verify=self.__SSL).json()
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

    def GetMCSMInfo(self, forceReload: bool = False) -> None:
        """
        获取当前面板下所有守护进程UUID以及所有实例名
        Args:
            forceReload: 是否强制刷新已储存的uuid
        """
        backup = self.Data
        try:
            try:
                data = self.CallApi("service/remote_services_list").get("data")
            except RuntimeError as err:
                logger.error(err)
                raise RuntimeError
            else:
                if forceReload:
                    self.Data = {}
                self.__Server = {}
                for item in data:
                    if item["uuid"] in self.Data.keys():
                        self.__Server[item["uuid"]] = {"name": self.Data[item["uuid"]][item["uuid"]],
                                                       "instances": {}}
                    else:
                        self.Data[item["uuid"]] = {item["uuid"]: item["remarks"]}
                        self.__Server[item["uuid"]] = {"name": item["remarks"], "instances": {}}
                try:
                    data = self.CallApi("service/remote_services").get("data")
                except RuntimeError as err:
                    logger.error(err)
                    raise RuntimeError
                else:
                    for item in data:
                        nameDict = self.Data[item["uuid"]]
                        for raw in item["instances"]:
                            if raw["instanceUuid"] in nameDict.keys():
                                self.__Server[item["uuid"]]["instances"][raw["instanceUuid"]] = {
                                    "name": nameDict[raw["instanceUuid"]], "status": raw["status"]}
                            else:
                                self.Data[item["uuid"]][raw["instanceUuid"]] = raw["config"]["nickname"]
                                self.__Server[item["uuid"]]["instances"][raw["instanceUuid"]] = {
                                    "name": raw["config"]["nickname"], "status": raw["status"]}
                    self.WriteData()
                    self.NameToUUID()
        except:
            logger.error("初始化失败")
            self.Data = backup
            self.WriteData()

    # 状态转换和名称UUID转换
    @staticmethod
    def StatusCode(code: int) -> str:
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

    def NameToUUID(self) -> None:
        """
        转换名称-uuid映射表\n
        """
        self.__NameToUUID = {}
        self.__ServerListDict = {}
        for item in self.Data:
            for raw in self.Data[item]:
                if raw == item:
                    self.__NameToUUID[self.Data[item][raw]] = {"Service": raw}
                else:
                    self.__NameToUUID[self.Data[item][item]][self.Data[item][raw]] = raw
                    self.__ServerListDict[self.Data[item][raw]] = item

    def TranslateNameToUUID(self, name: str) -> str:
        if name in self.__NameToUUID.keys():
            return self.__NameToUUID[name]["Service"]
        else:
            return self.__NameToUUID[self.Data[self.__ServerListDict[name]][self.__ServerListDict[name]]][name]

    def GetRemoteUUID(self, name: str) -> str:
        if name in self.__NameToUUID.keys():
            return self.__NameToUUID[name]["Service"]
        else:
            return self.__ServerListDict[name]

    def IsRemoteName(self, name: str) -> int:
        if name in self.__ServerListDict.keys():
            return 0
        elif name in self.__NameToUUID.keys():
            return 1
        else:
            return 2

    # 第一次封装
    def GetInstanceInfo(self, remoteUUID: str, instanceUUID: str, FullData: bool = False) -> Optional[Union[int, dict]]:
        """
        获取实例状态\n
        Args:
            remoteUUID: 守护进程uuid
            instanceUUID: 实例uuid
            FullData: 是否返回完整结果，如果为False则只返回状态码（默认为False）
        """
        try:
            try:
                data = self.CallApi("/api/instance", {"uuid": instanceUUID, "remote_uuid": remoteUUID})
            except RuntimeError as err:
                logger.error(err)
                return None
            else:
                if FullData:
                    return data
                else:
                    return data.get("data").get("status") if data.get("data").get("instanceUuid") == instanceUUID else None
        except Exception as err:
            logger.error(err)
            return None

    def UpdateInstanceStatus(self, remoteUUID: Optional[str] = None, instanceUUID: Optional[str] = None) -> None:
        """
        刷新所有守护进程的所有实例的运行状态\n
        刷新某一守护进程的所有实例的运行状态\n
        刷新某一守护进程的某一实例的运行状态\n
        Args:
            remoteUUID: 守护进程uuid，可为空
            instanceUUID: 实例uuid，可为空
        """
        try:
            if remoteUUID is None and instanceUUID is not None:
                raise RuntimeError("传入参数错误")
            if remoteUUID is None and instanceUUID is None:
                for item in self.__Server:
                    data = self.__Server[item].get("instances")
                    for raw in data:
                        data[raw]["status"] = self.GetInstanceInfo(item, raw)
            elif remoteUUID is not None and instanceUUID is None:
                data = self.__Server[remoteUUID].get("instances")
                for raw in data:
                    data[raw]["status"] = self.GetInstanceInfo(remoteUUID, raw)
            elif remoteUUID is not None and instanceUUID is not None:
                self.__Server[remoteUUID].get("instances")[instanceUUID]["status"] = self.GetInstanceInfo(remoteUUID, instanceUUID)
        except:
            logger.error("更新实例状态出错")
        else:
            logger.debug("成功更新实例信息")

    def GetInstanceStatus(self, remoteUUID: str, instanceUUID: str, ReturnStatusCode: bool = False) -> Union[int, str]:
        if ReturnStatusCode:
            return self.GetInstanceInfo(remoteUUID, instanceUUID)
        else:
            return self.StatusCode(self.GetInstanceInfo(remoteUUID, instanceUUID))

    def CheckName(self, remoteName: str = None, instanceName: str = None) -> Union[bool, str]:
        if remoteName is None and instanceName is None:
            return "至少传入一个参数"
        elif remoteName is not None and instanceName is None:
            return True if self.IsRemoteName(remoteName) == 1 else f"{remoteName}不是一个有效的守护进程名称"
        elif remoteName is None and instanceName is not None:
            return True if self.IsRemoteName(instanceName) == 0 else f"{instanceName}不是一个有效的实例名称"
        elif remoteName is not None and instanceName is not None:
            if self.IsRemoteName(remoteName) == 1:
                return True if self.IsRemoteName(instanceName) == 0 else f"{instanceName}不是一个有效的实例名称"
            else:
                return f"{remoteName}不是一个有效的守护进程名称"

    def StartInstance(self, remoteUUID: str, instanceUUID: str) -> str:
        match self.GetInstanceInfo(remoteUUID, instanceUUID):
            case -1:
                return "实例状态未知，无法启动"
            case 0:
                try:
                    self.CallApi("/api/protected_instance/open", {"uuid": instanceUUID, "remote_uuid": remoteUUID})
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

    def StopInstance(self, remoteUUID: str, instanceUUID: str, forceKILL: bool = False) -> str:
        match self.GetInstanceInfo(remoteUUID, instanceUUID):
            case -1:
                return "实例状态未知，无法关闭"
            case 0:
                return "实例已停止，无法关闭"
            case 1:
                return "实例正在停止，无法关闭"
            case 2:
                return "实例正在启动中，无法关闭"
            case 3:
                if forceKILL:
                    try:
                        self.CallApi("/api/protected_instance/kill", {"uuid": instanceUUID, "remote_uuid": remoteUUID})
                    except RuntimeError as err:
                        logger.error(err)
                        return "关闭实例失败，api返回异常"
                    else:
                        return "执行成功，强制关闭实例"
                else:
                    try:
                        self.CallApi("/api/protected_instance/stop", {"uuid": instanceUUID, "remote_uuid": remoteUUID})
                    except RuntimeError as err:
                        logger.error(err)
                        return "关闭实例失败，api返回异常"
                    else:
                        return "执行成功，实例正在关闭"

    def RestartInstance(self, remoteUUID: str, instanceUUID: str) -> str:
        match self.GetInstanceInfo(remoteUUID, instanceUUID):
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
                    self.CallApi("/api/protected_instance/restart", {"uuid": instanceUUID, "remote_uuid": remoteUUID})
                except RuntimeError as err:
                    logger.error(err)
                    return "重启实例失败，api返回异常"
                else:
                    return "执行成功，实例正在重启"

    def Command(self, instanceUUID: str, remoteUUID: str, command: str) -> float:
        try:
            data = self.CallApi("api/protected_instance/command", {
                "remote_uuid": remoteUUID,
                "uuid": instanceUUID,
                "command": command
            })
        except RuntimeError as err:
            logger.error(err)
            raise RuntimeError
        else:
            return data.get("time")/1000

    def GetCommandOutPut(self, instanceUUID: str, remoteUUID: str, timeStamp: float) -> str:
        try:
            data = self.CallApi("/api/protected_instance/outputlog", {
                "remote_uuid": remoteUUID,
                "uuid": instanceUUID
            })
        except RuntimeError as err:
            logger.error(err)
            raise RuntimeError
        else:
            tempList: list = []
            time = strftime("[%H:%M:%S]", localtime(timeStamp))
            data = data["data"].replace("\x1b[m//\r \r\x1b[34m", "") \
                               .replace("\x1b[m/\r \r\x1b[34m", "") \
                               .replace("\r \r\x1b[34m", "") \
                               .replace("\x1b[36m", "") \
                               .replace("\x1b[32m", "") \
                               .replace("\x1b[0m", "") \
                               .replace("\x1b[m", "") \
                               .split("\n")[-20:]
            for item in data:
                if item[:10] == time and "[Server thread/INFO]" in item:
                    tempList.append(item)
            res: str = ""
            for raw in tempList:
                if raw.find("]: ") != -1:
                    res += f"{raw[raw.find(']: ') + 3:]}\n"
                elif raw.find(")") != -1:
                    res += f"{raw[raw.find(')') + 2:]}\n"
            return res.removesuffix("\n")

    # 第二次封装
    def CheckInstanceStatus(self, instanceName: str, remoteName: str = None) -> str:
        res = self.CheckName(remoteName, instanceName)
        if isinstance(res, bool):
            if remoteName is None:
                remoteUUID = self.GetRemoteUUID(instanceName)
                remoteName = self.Data[remoteUUID][remoteUUID]
            else:
                remoteUUID = self.TranslateNameToUUID(remoteName)
            return f"守护进程名称: {remoteName}\n实例名称: {instanceName}\n实例运行状态: {self.StatusCode(self.GetInstanceInfo(remoteUUID, self.TranslateNameToUUID(instanceName)))}"
        else:
            return res

    def RunCommand(self, instanceName: str, remoteName: str, command: str) -> str:
        res = self.CheckName(remoteName, instanceName)
        if isinstance(res, bool):
            instanceUUID = self.TranslateNameToUUID(instanceName)
            remoteUUID = self.TranslateNameToUUID(remoteName)
            status = self.GetInstanceInfo(remoteUUID, instanceUUID)
            if status == 3:
                return self.GetCommandOutPut(instanceUUID, remoteUUID, self.Command(instanceUUID, remoteUUID, command))
            else:
                return f"实例当前状态是:{self.StatusCode(status)},无法执行命令"
        else:
            return res

    def ListInstance(self, remoteName: str = None) -> str:
        result: str = ""
        if remoteName is None:
            for item in self.__Server:
                result += f"[{self.__Server[item]['name']}]\n"
                for raw in self.__Server[item]["instances"]:
                    result += f"{self.__Server[item]['instances'][raw]['name']} : {self.StatusCode(self.__Server[item]['instances'][raw]['status'])}\n"
            return result.removesuffix("\n")
        res = self.CheckName(remoteName)
        if isinstance(res, bool):
            remoteUUID = self.TranslateNameToUUID(remoteName)
            result += f"[{remoteName}]\n"
            for raw in self.__Server[remoteUUID]["instances"]:
                result += f"{self.__Server[remoteUUID]['instances'][raw]['name']} : {self.StatusCode(self.__Server[remoteUUID]['instances'][raw]['status'])}\n"
            return result.removesuffix("\n")
        else:
            return res

    def ReName(self, OriginalName: str, NewName: str) -> str:
        if OriginalName == NewName:
            return "未更改，与原名一致"
        if NewName in self.__NameToUUID.keys():
            return "未更改，新名字与守护进程名称重复"
        if NewName in self.__ServerListDict.keys():
            return "未更改，新名字与实例名称重复"
        match self.IsRemoteName(OriginalName):
            case 0:
                try:
                    remoteUUID = self.__ServerListDict[OriginalName]
                    del self.__ServerListDict[OriginalName]
                    self.__ServerListDict[NewName] = remoteUUID
                    instanceUUID = self.__NameToUUID[self.__Server[remoteUUID]["name"]][OriginalName]
                    del self.__NameToUUID[self.__Server[remoteUUID]["name"]][OriginalName]
                    self.__NameToUUID[self.__Server[remoteUUID]["name"]][NewName] = instanceUUID
                    self.Data[remoteUUID][instanceUUID] = NewName
                    self.WriteData()
                    self.__Server[remoteUUID]["instances"][instanceUUID]["name"] = NewName
                except:
                    return "修改名称失败"
                else:
                    return f"改名成功：\n[{OriginalName}] -> [{NewName}]"
            case 1:
                try:
                    remoteUUID = self.__NameToUUID[OriginalName]["Service"]
                    self.__NameToUUID[NewName] = self.__NameToUUID[OriginalName]
                    del self.__NameToUUID[OriginalName]
                    self.Data[remoteUUID][remoteUUID] = NewName
                    self.WriteData()
                    self.__Server[remoteUUID]["name"] = NewName
                except:
                    return "修改名称失败"
                else:
                    return f"改名成功：\n[{OriginalName}] -> [{NewName}]"
            case 2:
                return f"{OriginalName}不是一个有效的守护进程名称或实例名称"

    def Stop(self, instanceName: str, remoteName: str = None, forceKill: bool = False) -> str:
        res = self.CheckName(remoteName, instanceName)
        if isinstance(res, bool):
            if remoteName is None:
                return self.StopInstance(self.__ServerListDict[instanceName], self.TranslateNameToUUID(instanceName), forceKill)
            else:
                return self.StopInstance(self.TranslateNameToUUID(remoteName), self.TranslateNameToUUID(instanceName), forceKill)
        else:
            return res

    def Start(self, instanceName: str, remoteName: str = None) -> str:
        res = self.CheckName(remoteName, instanceName)
        if isinstance(res, bool):
            if remoteName is None:
                return self.StartInstance(self.__ServerListDict[instanceName], self.TranslateNameToUUID(instanceName))
            else:
                return self.StartInstance(self.TranslateNameToUUID(remoteName), self.TranslateNameToUUID(instanceName))
        else:
            return res

    def Restart(self, instanceName: str, remoteName: str = None) -> str:
        res = self.CheckName(remoteName, instanceName)
        if isinstance(res, bool):
            if remoteName is None:
                return self.RestartInstance(self.__ServerListDict[instanceName], self.TranslateNameToUUID(instanceName))
            else:
                return self.RestartInstance(self.TranslateNameToUUID(remoteName), self.TranslateNameToUUID(instanceName))
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
