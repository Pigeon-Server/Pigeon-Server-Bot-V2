from module.Class.JsonDataBaseClass import JsonDataBaseCLass
from module.Class.ConfigClass import ConfigTools
from typing import Union, Optional


class PermissionClass(JsonDataBaseCLass, ConfigTools):
    _GroupPermission: JsonDataBaseCLass

    class Mcsm:
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
        class Player:
            Give: str = "Permission.Player.Give"
            Remove: str = "Permission.Player.Remove"
            Check: str = "Permission.Player.Check"
            List: str = "Permission.Player.List"
            Clone: str = "Permission.Player.Clone"
            Del: str = "Permission.Player.Del"
            Info: str = "Permission.Player.Info"

            class Inherit:
                Add: str = "Permission.Player.Inherit.Add"
                Del: str = "Permission.Player.Inherit.Del"

        class Group:
            Give: str = "Permission.Group.Give"
            Remove: str = "Permission.Group.Remove"
            List: str = "Permission.Group.List"
            Clone: str = "Permission.Group.Clone"
            Del: str = "Permission.Group.Del"
            Info: str = "Permission.Group.Info"
            Check: str = "Permission.Group.Check"

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
                    self.Group.List, self.Group.Clone, self.Group.Remove, self.Group.Give, self.Group.Info,
                    self.Group.Del, self.Group.Inherit.Add, self.Group.Inherit.Del, self.Group.Check,
                    self.Group.Reload.Common, self.Group.Reload.Force,
                    self.List]

    def __init__(self) -> None:
        super().__init__("permission.json", 5)
        self._GroupPermission = JsonDataBaseCLass("permissionGroup.json", 5)
        if self._GroupPermission.Data == {}:
            self._GroupPermission.Data = self.loadConfig("permission.json5")
            self._GroupPermission.WriteData()

    def ReloadGroupPermission(self, overWrite: bool = False) -> str:
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
            else:
                return False
        except:
            return False

    def ClonePlayerPermission(self, fromId: str, toId: str) -> str:
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
        if userId in self.Data.keys():
            return self.Data[userId]
        else:
            return None

    def GetGroupInfo(self, groupName: str) -> Optional[dict]:
        if groupName in self._GroupPermission.Data.keys():
            return self._GroupPermission.Data[groupName]
        else:
            return None

    def CloneGroupPermission(self, fromGroup: str, toGroup: str) -> str:
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
        result = self.Mcsm.GetAllPermissionNode(self.Mcsm())
        result += self.Permission.GetAllPermissionNode(self.Permission())
        return result

    def AddGroupPermission(self, groupName: str, permission: str) -> str:
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
