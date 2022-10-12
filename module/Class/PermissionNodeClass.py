from module.Class.JsonDataBaseClass import JsonDataBaseCLass
from module.Class.ConfigClass import ConfigTools
from typing import Union, Optional


class PermissionClass(JsonDataBaseCLass, ConfigTools):
    _GroupPermission: JsonDataBaseCLass
    _PermissionNodeList: list

    class Mcsm:
        """
        关于mcsm面板的权限节点
        """
        class Update:
            Common: str = "Mcsm.Update.Common"
            Force: str = "Mcsm.Update.Force"

        Check: str = "Mcsm.Check"
        List: str = "Mcsm.List"
        Rename: str = "Mcsm.Rename"
        Stop: str = "Mcsm.Stop"
        Kill: str = "Mcsm.Kill"
        Start: str = "Mcsm.Start"
        Restart: str = "Mcsm.Restart"
        Command: str = "Mcsm.Command"

        def GetAllPermissionNode(self) -> list:
            return [self.Command, self.Kill, self.Start, self.Stop, self.Restart,
                    self.Check, self.List, self.Rename, self.Update.Force, self.Update.Common]

    class Permission:
        """
        关于权限系统自身的权限节点
        """
        class Player:
            Give: str = "Permission.Player.Give"
            Remove: str = "Permission.Player.Remove"
            Check: str = "Permission.Player.Check"
            List: str = "Permission.Player.List"
            Clone: str = "Permission.Player.Clone"
            Del: str = "Permission.Player.Del"
            Info: str = "Permission.Player.Info"
            Create: str = "Permission.Player.Create"

            class Inherit:
                Add: str = "Permission.Player.Inherit.Add"
                Del: str = "Permission.Player.Inherit.Del"
                Set: str = "Permission.Player.Inherit.Set"

        class Group:
            Give: str = "Permission.Group.Give"
            Remove: str = "Permission.Group.Remove"
            List: str = "Permission.Group.List"
            Clone: str = "Permission.Group.Clone"
            Del: str = "Permission.Group.Del"
            Info: str = "Permission.Group.Info"
            Check: str = "Permission.Group.Check"
            Create: str = "Permission.Group.Create"

            class Inherit:
                Add: str = "Permission.Group.Inherit.Add"
                Del: str = "Permission.Group.Inherit.Del"

        class Reload:
            Common: str = "Permission.Group.Reload.Common"
            Force: str = "Permission.Group.Reload.Force"

        List: str = "Permission.List"

        def GetAllPermissionNode(self) -> list:
            return [self.Player.Check, self.Player.Clone, self.Player.Give, self.Player.Remove,
                    self.Player.List, self.Player.Inherit.Del,self.Player.Inherit.Add, self.Player.Del, self.Player.Info,
                    self.Player.Create, self.Player.Inherit.Set,
                    self.Group.List, self.Group.Clone, self.Group.Remove, self.Group.Give, self.Group.Info,
                    self.Group.Del, self.Group.Inherit.Add, self.Group.Inherit.Del, self.Group.Check,
                    self.Reload.Common, self.Reload.Force,self.Group.Create,
                    self.List]

    class Whitelist:
        """
        白名单权限节点
        """
        Apply: str = "Whitelist.Apply"
        Change: str = "Whitelist.Change"
        Agree: str = "Whitelist.Agree"
        AgreeALL: str = "Whitelist.AgreeALL"
        Refuse: str = "Whitelist.Refuse"

        class List:
            Wait: str = "Whitelist.List.Wait"

        def GetAllPermissionNode(self) -> list:
            return [self.Apply, self.Agree, self.AgreeALL, self.Change, self.Refuse, self.List.Wait]

    class Blacklist:
        """
        黑名单权限节点
        """
        List: str = "Blacklist.List"
        Check: str = "Blacklist.Check"
        Add: str = "Blacklist.Add"
        Remove: str = "Blacklist.Remove"

        def GetAllPermissionNode(self) -> list:
            return [self.List, self.Check, self.Add, self.Remove]

    class Token:
        """
        秘钥权限节点
        """
        Lock: str = "Token.Lock"
        Unlock: str = "Token.Unlock"
        Check: str = "Token.Check"

        def GetAllPermissionNode(self) -> list:
            return [self.Lock, self.Unlock, self.Check]

    class Question:
        """
        问答权限节点
        """
        Shutup: str = "Question.Shutup"
        GetAnswer: str = "Question.GetAnswer"

        def GetAllPermissionNode(self) -> list:
            return [self.GetAnswer, self.Shutup]

    def __init__(self) -> None:
        """
        类构造函数
        """
        super().__init__("permission.json", 5)
        self._GroupPermission = JsonDataBaseCLass("permissionGroup.json", 5)
        if self._GroupPermission.Data == {}:
            self._GroupPermission.Data = self.loadConfig("permission.json5")
            self._GroupPermission.WriteData()
        self._PermissionNodeList = self.Mcsm.GetAllPermissionNode(self.Mcsm())
        self._PermissionNodeList += self.Permission.GetAllPermissionNode(self.Permission())
        self._PermissionNodeList += self.Blacklist.GetAllPermissionNode(self.Blacklist())
        self._PermissionNodeList += self.Whitelist.GetAllPermissionNode(self.Whitelist())
        self._PermissionNodeList += self.Token.GetAllPermissionNode(self.Token())
        self._PermissionNodeList += self.Question.GetAllPermissionNode(self.Question())

    def ReloadGroupPermission(self, overWrite: bool = False) -> str:
        """
        重新从配置文件中加载权限组配置\n
        Args:
            overWrite: 是覆盖模式还是追加模式，默认为追加
        Returns:
            返回执行状态
        """
        try:
            if overWrite:
                self._GroupPermission.Data = self.loadConfig("permission.json5")
                self._GroupPermission.WriteData()
            else:
                raw: str
                data: dict = self.loadConfig("permission.json5")
                for raw in data:
                    if raw in self._GroupPermission.Data.keys():
                        temp = data[raw]["permission"]
                        for item in temp:
                            if item not in self._GroupPermission.Data[raw]["permission"]:
                                self._GroupPermission.Data[raw]["permission"].append(item)
                        if "parent" in data[raw].keys():
                            if "parent" in self._GroupPermission.Data[raw].keys():
                                temp = data[raw]["parent"]
                                for item in temp:
                                    if item not in self._GroupPermission.Data[raw]["parent"]:
                                        self._GroupPermission.Data[raw]["parent"].append(item)
                            else:
                                self._GroupPermission.Data[raw]["parent"] = data[raw]["parent"]
                    else:
                        self._GroupPermission.Data[raw] = data[raw]
                self._GroupPermission.WriteData()
        except:
            return "重载权限组失败"
        else:
            return "重载权限组成功"

    def GetGroupPermission(self, groupName: Union[list, str]) -> list:
        """
        获取权限组的所有权限（包括继承的权限组）\n
        Args:
            groupName: 要查询的组名，可以单个也可以用列表
        Returns:
            返回权限节点列表
        """
        result = []
        name: str
        if not isinstance(groupName, list):
            groupName = list(groupName)
        for name in groupName:
            if name in self._GroupPermission.Data.keys():
                if "parent" in self._GroupPermission.Data[name].keys():
                    result += self.GetGroupPermission(self._GroupPermission.Data[name]["parent"])
                result += self._GroupPermission.Data[name]["permission"]
        return list(set(result))

    def GetPlayerPermission(self, userId: str) -> list:
        """
        获取某个玩家的全部权限\n
        Args:
            userId: 玩家id
        Returns:
            返回权限节点列表
        """
        try:
            if userId in self.Data.keys():
                result: list = []
                if "permission" in self.Data[userId].keys():
                    result += self.Data[userId]["permission"]
                if "group" in self.Data[userId].keys():
                    result += self.GetGroupPermission(self.Data[userId]["group"])
                return result
            else:
                return []
        except:
            return []

    def AddPlayerPermission(self, userId: str, permission: str) -> str:
        """
        向某个玩家添加一个权限节点\n
        Args:
            userId: 玩家id
            permission: 要添加的权限节点
        Returns:
            执行信息
        """
        try:
            if userId in self.Data.keys():
                if "group" in self.Data[userId]:
                    userPermission = self.GetGroupPermission(self.Data[userId]["group"]) + self.Data[userId]["permission"]
                else:
                    userPermission = self.Data[userId]["permission"]
                if permission in userPermission:
                    return f"此用户已有{permission}权限" if permission in self.Data[userId]["permission"] else "该用户下某一用户组具有该权限"
                else:
                    if self.CheckPlayerPermission(userId, permission):
                        self.Data[userId]["permission"].append(permission)
                    else:
                        return f"你必须拥有{permission}权限才能给予他人{permission}权限"
            else:
                self.Data[userId] = {
                    "group": ["default"],
                    "permission": [permission]
                }
            self.WriteData()
        except:
            return f"向{userId}添加权限{permission}失败"
        else:
            return f"向{userId}添加权限{permission}成功"

    def RemovePlayerPermission(self, userId: str, permission: str) -> str:
        """
        移除某个玩家的某个权限节点\n
        Args:
            userId: 玩家id
            permission: 权限节点
        Returns:
            执行结果
        """
        try:
            if userId in self.Data.keys():
                if permission in self.Data[userId]["permission"]:
                    self.Data[userId]["permission"].remove(permission)
                else:
                    return f"此用户没有{permission}权限"
            self.WriteData()
        except:
            return f"移除{userId}的权限{permission}失败"
        else:
            return f"移除{userId}的权限{permission}成功"

    def CheckPlayerPermission(self, userId: str, permission: str) -> bool:
        """
        检查玩家是否拥有某一权限节点\n
        Args:
            userId: 玩家id
            permission: 权限节点
        Returns:
            拥有Ture 未拥有False
        """
        userId = str(userId)
        try:
            if userId in self.Data.keys():
                data: list = self.Data[userId]["permission"]
                if "group" in self.Data[userId].keys():
                    data += self.GetGroupPermission(self.Data[userId]["group"])
                if f"-{permission}" in data:
                    return False
                data = self._PermissionDel(data)
                if "*.*" in data:
                    return True
                return self._CheckPermission(data, permission)
        except:
            return False

    def ClonePlayerPermission(self, fromId: str, toId: str) -> str:
        """
        克隆某一玩家的权限\n
        Args:
            fromId: 克隆对象id
            toId: 克隆目标id
        Returns:
            返回执行消息
        """
        try:
            if fromId not in self.Data.keys():
                return f"无法查询到{fromId}的权限记录"
            else:
                self.Data[toId] = self.Data[fromId]
                self.WriteData()
        except:
            return "克隆权限出现错误"
        else:
            return f"成功将{fromId}的权限克隆到{toId}"

    def GetPlayerInfo(self, userId: str) -> Optional[dict]:
        """
        获取玩家所有权限信息\n
        Args:
            userId: 目标玩家id
        Returns:
            如果玩家不存在返回None，存在返回字典
        """
        if userId in self.Data.keys():
            return self.Data[userId]
        else:
            return None

    def GetGroupInfo(self, groupName: str) -> Optional[dict]:
        """
        获取某一权限组所有权限信息\n
        Args:
            groupName: 目标玩家id
        Returns:
            如果权限组不存在返回None，存在返回字典
        """
        if groupName in self._GroupPermission.Data.keys():
            return self._GroupPermission.Data[groupName]
        else:
            return None

    def CloneGroupPermission(self, fromGroup: str, toGroup: str) -> str:
        """
        克隆某一权限组的权限到另一权限组\n
        Args:
            fromGroup: 克隆对象权限组名
            toGroup: 克隆目标权限组名
        Returns:
            返回执行消息
        """
        try:
            if fromGroup not in self._GroupPermission.Data.keys():
                return f"权限组{fromGroup}不存在"
            else:
                self._GroupPermission.Data[toGroup] = self._GroupPermission.Data[fromGroup]
                self._GroupPermission.WriteData()
        except:
            return "克隆权限出现错误"
        else:
            return f"成功将权限组{fromGroup}的权限克隆到{fromGroup}"

    def GetPermissionNode(self) -> list:
        """
        获得所有的权限节点列表\n
        Returns:
            返回所有的权限节点列表
        """
        return self._PermissionNodeList

    def AddGroupPermission(self, groupName: str, permission: str) -> str:
        """
        向权限组内添加权限\n
        Args:
            groupName: 权限组名
            permission: 权限节点名
        Returns:
            执行结果
        """
        try:
            if groupName in self._GroupPermission.Data.keys():
                self._GroupPermission.Data[groupName]["permission"].append(permission)
            else:
                self._GroupPermission.Data[groupName] = {
                    "permission": [
                        permission
                    ]
                }
            self._GroupPermission.WriteData()
        except:
            return f"向权限组{groupName}添加权限{permission}失败"
        else:
            return f"向权限组{groupName}添加权限{permission}成功"

    def RemoveGroupPermission(self, groupName: str, permission: str) -> str:
        """
        从权限组内移除权限\n
        Args:
            groupName: 权限组名
            permission: 权限节点名
        Returns:
            执行结果
        """
        try:
            if groupName in self._GroupPermission.Data.keys():
                if "permission" in self._GroupPermission.Data[groupName].keys():
                    if permission in self._GroupPermission.Data[groupName]["permission"]:
                        self._GroupPermission.Data[groupName]["permission"].remove(permission)
                    else:
                        return f"权限组{groupName}中没有权限{permission}"
                else:
                    self._GroupPermission.Data[groupName]["permission"] = []
                self._GroupPermission.WriteData()
            else:
                return f"无法查询到权限组{groupName}"
        except:
            return f"移除权限组{groupName}的权限{permission}失败"
        else:
            return f"移除权限组{groupName}的权限{permission}成功"

    def CheckGroupPermission(self, groupName: str, permission: str) -> bool:
        """
        检查某一权限组是否拥有某一权限\n
        Args:
            groupName: 权限组名
            permission: 权限节点名
        Returns:
            拥有True 未拥有 False
        """
        try:
            data = self.GetGroupPermission(groupName)
            if f"-{permission}" in data:
                return False
            data = self._PermissionDel(data)
            if "*.*" in data:
                return True
            return self._CheckPermission(data, permission)
        except:
            return False

    def AddGroupParent(self, groupName: str, parentGroup: str) -> str:
        """
        向某一权限组内添加父权限组\n
        Args:
            groupName: 权限组名
            parentGroup: 父权限组名
        Returns:
            返回运行结果
        """
        try:
            if parentGroup not in self._GroupPermission.Data.keys():
                return f"无法找到权限组{parentGroup}"
            if groupName in self._GroupPermission.Data.keys():
                if "parent" in self._GroupPermission.Data[groupName].keys():
                    self._GroupPermission.Data[groupName]["parent"].append(parentGroup)
                else:
                    self._GroupPermission.Data[groupName]["parent"] = [parentGroup]
                self._GroupPermission.WriteData()
            else:
                self._GroupPermission.Data[groupName] = {
                    "parent": [parentGroup]
                }
                self._GroupPermission.WriteData()
                return f"无法找到目标权限组{groupName},已自动创建"
        except:
            return f"向权限组{groupName}中添加父权限组{parentGroup}失败"
        else:
            return f"成功向权限组{groupName}中添加父权限组{parentGroup}"

    def RemoveGroupParent(self, groupName: str, parentGroup: str) -> str:
        """
        从某一权限组内移除父权限组\n
        Args:
            groupName: 权限组名
            parentGroup: 父权限组名
        Returns:
            执行结果
        """
        try:
            if parentGroup not in self._GroupPermission.Data.keys():
                return f"无法找到权限组{parentGroup}"
            if groupName in self._GroupPermission.Data.keys():
                if "parent" in self._GroupPermission.Data[groupName]:
                    self._GroupPermission.Data[groupName]["parent"].remove(parentGroup)
                    self._GroupPermission.WriteData()
                else:
                    return f"权限组{groupName}没有父权限组"
            else:
                return f"无法找到权限组{groupName}"
        except:
            return f"向权限组{groupName}中移除父权限组{parentGroup}失败"
        else:
            return f"成功移除权限组{groupName}的父权限组{parentGroup}"

    def AddPlayerParent(self, userID: str, parentGroup: str) -> str:
        """
        为玩家添加继承权限组\n
        Args:
            userID: 玩家ID
            parentGroup: 要继承的权限组
        Returns:
            返回执行结果
        """
        try:
            if parentGroup not in self._GroupPermission.Data.keys():
                return f"无法找到权限组{parentGroup}"
            if userID in self.Data.keys():
                if "group" in self.Data[userID].keys():
                    self.Data[userID]["group"].append(parentGroup)
                else:
                    self.Data[userID]["group"] = [parentGroup]
                self.WriteData()
            else:
                self.Data[userID] = {
                    "group": [parentGroup]
                }
                self._GroupPermission.WriteData()
                return f"无法找到目标{userID},已自动创建"
        except:
            return f"向目标{userID}添加权限组{parentGroup}失败"
        else:
            return f"向目标{userID}添加权限组{parentGroup}成功"

    def RemovePlayerParent(self, userID: str, parentGroup: str) -> str:
        """
        移除玩家继承的权限组\n
        Args:
            userID: 玩家ID
            parentGroup: 要移除的父权限组
        Returns:
            执行结果
        """
        try:
            if parentGroup not in self._GroupPermission.Data.keys():
                return f"无法找到权限组{parentGroup}"
            if userID in self.Data.keys():
                if "group" in self.Data[userID].keys():
                    self.Data[userID]["group"].remove(parentGroup)
                    self.WriteData()
                else:
                    return f"目标{userID}没有权限组"
            else:
                return f"无法找到目标{userID}"
        except:
            return f"移除目标{userID}权限组{parentGroup}失败"
        else:
            return f"移除目标{userID}权限组{parentGroup}成功"

    def DelGroup(self, groupName: str) -> str:
        """
        删除权限组\n
        Args:
            groupName: 要删除的权限组名
        Returns:
            返回执行结果
        """
        try:
            if groupName in self._GroupPermission.Data.keys():
                del self._GroupPermission.Data[groupName]
                self._GroupPermission.WriteData()
            else:
                return f"无法找到权限组{groupName}"
        except:
            return f"删除权限组{groupName}失败"
        else:
            return f"删除权限组{groupName}成功"

    def DelPlayer(self, userId: str) -> str:
        """
        删除某一玩家\n
        Args:
            userId: 玩家id
        Returns:
            返回执行结果
        """
        try:
            if userId in self.Data.keys():
                del self.Data[userId]
                self.WriteData()
            else:
                return f"无法找到目标{userId}"
        except:
            return f"删除目标{userId}失败"
        else:
            return f"删除目标{userId}成功"

    def SetPlayerGroup(self, userId: str, groupName: Union[str, list] = None) -> str:
        """
        为某一玩家设置权限组\n
        Args:
            userId: 玩家id
            groupName: 要设置的权限名
        Returns:
            执行结果
        """
        try:
            if userId in self.Data.keys():
                if groupName is None:
                    self.Data[userId]["group"] = []
                elif isinstance(groupName, str):
                    self.Data[userId]["group"] = [groupName]
                elif isinstance(groupName, list):
                    self.Data[userId]["group"] = groupName
                else:
                    raise ValueError
                self.WriteData()
        except:
            return f"设置{userId}的权限组失效"
        else:
            return f"设置{userId}的权限组为{str(groupName)}"

    def CreatGroup(self, groupName: str) -> str:
        """
        创建权限组\n
        Args:
            groupName: 权限组名
        Returns:
            执行结果
        """
        if groupName not in self._GroupPermission.Data.keys():
            self._GroupPermission.Data[groupName] = {
                "parent": ["default"],
                "permission": []
            }
            self._GroupPermission.WriteData()
            return "创建成功"
        else:
            return "创建权限组是吧，权限组已存在"

    def CreatPlayer(self, userId: str, group: str = None) -> str:
        """
        创建玩家\n
        Args:
            userId: 玩家ID
            group: 初始继承的权限组
        Returns:
            执行结果
        """
        if userId not in self.Data.keys():
            self.Data[userId] = {
                "group": ["default" if group is None else group],
                "permission": []
            }
            self.WriteData()
            return "创建成功"
        else:
            return "创建失败,记录已存在"

    @staticmethod
    def _PermissionDel(data: list) -> list:
        for raw in data:
            if raw.startswith("-"):
                check = raw[1:].split(".")
                match len(check):
                    case 2:
                        if raw[1:] == "*.*":
                            data.remove("*.*")
                        elif check[1] == "*":
                            for item in data:
                                if item.startswith(check[0]):
                                    data.remove(item)
                        else:
                            if raw[1:] in data:
                                data.remove(raw[1:])
                    case 3:
                        if check[2] == "*":
                            for item in data:
                                if item.startswith(f"{check[0]}.{check[1]}"):
                                    data.remove(item)
                        else:
                            if raw[1:] in data:
                                data.remove(raw[1:])
                    case 4:
                        if check[3] == "*":
                            for item in data:
                                if item.startswith(f"{check[0]}.{check[1]},{check[2]}"):
                                    data.remove(item)
                        else:
                            if raw[1:] in data:
                                data.remove(raw[1:])
                data.remove(raw)
        return data

    @staticmethod
    def _CheckPermission(data: list, permission: str) -> bool:
        temp = permission.split(".")
        match len(temp):
            case 1:
                raise ValueError(permission)
            case 2:
                if permission == "*.*":
                    return permission in data
                elif temp[1] == "*":
                    return permission in data
                elif temp[0] == "*":
                    raise ValueError(permission)
                else:
                    if f"{temp[0]}.*" in data:
                        return True
                    else:
                        return permission in data
            case 3:
                if permission == "*.*.*":
                    raise ValueError(permission)
                elif temp[2] == "*":
                    return permission in data
                elif temp[0] == "*" or temp[1] == "*":
                    raise ValueError(permission)
                else:
                    if f"{temp[0]}.*" in data or f"{temp[0]}.{temp[1]}.*" in data:
                        return True
                    else:
                        return permission in data
            case 4:
                if permission == "*.*.*.*":
                    raise ValueError(permission)
                elif temp[3] == "*":
                    return permission in data
                elif temp[0] == "*" or temp[1] == "*" or temp[2] == "*":
                    raise ValueError(permission)
                else:
                    if f"{temp[0]}.*" in data or f"{temp[0]}.{temp[1]}.*" in data or f"{temp[0]}.{temp[1]}.{temp[2]}.*" in data:
                        return True
                    else:
                        return permission in data
            case 5:
                if permission == "*.*.*.*.*":
                    raise ValueError(permission)
                elif temp[4] == "*":
                    return permission in data
                elif temp[0] == "*" or temp[1] == "*" or temp[2] == "*" or temp[3] == "*":
                    raise ValueError(permission)
                else:
                    if f"{temp[0]}.*" in data or f"{temp[0]}.{temp[1]}.*" in data or f"{temp[0]}.{temp[1]}.{temp[2]}.*" in data or f"{temp[0]}.{temp[1]}.{temp[2]}.{temp[3]}.*" in data:
                        return True
                    else:
                        return permission in data
