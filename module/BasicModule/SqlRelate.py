from module.Class.DataBaseClass import DataBase
from module.BasicModule.Config import MainConfig
from module.BasicModule.Logger import logger

database = DataBase(MainConfig.DataBaseConfig.DatabaseName, MainConfig.DataBaseConfig.Host,
                    MainConfig.DataBaseConfig.Username, MainConfig.DataBaseConfig.Password, MainConfig.DataBaseConfig.Port)
database.Connect()
connected = database.GetConnectionInfo()
cursor = connected.cursor()

# 创建数据表
if cursor.execute("show tables") < 4:
    logger.error("数据表丢失，正在修复")
    cursor.execute("""CREATE TABLE IF NOT EXISTS `wait` (
      `id` int NOT NULL AUTO_INCREMENT COMMENT '自动生成 识别id',
      `account` char(30) CHARACTER SET utf8mb3 COLLATE utf8_general_ci NOT NULL COMMENT 'QQ/KOOK账号',
      `PlayerName` char(16) CHARACTER SET utf8mb3 COLLATE utf8_general_ci NOT NULL COMMENT '游戏名',
      `UserSource` char(4) CHARACTER SET utf8mb3 COLLATE utf8_general_ci NOT NULL COMMENT '玩家账号类型',
      `kookid` char(20) CHARACTER SET utf8mb3 COLLATE utf8_general_ci DEFAULT NULL COMMENT 'kook识别id（当UserSource为KOOK时自动填充）',
      `age` int NOT NULL COMMENT '年龄',
      `playtime` char(4) CHARACTER SET utf8mb3 COLLATE utf8_general_ci NOT NULL COMMENT '游玩时间',
      `onlinemode` tinyint(1) NOT NULL COMMENT '在线模式',
      `GameVersion` char(4) CHARACTER SET utf8mb3 COLLATE utf8_general_ci NOT NULL COMMENT '游戏版本',
      `Introduce` text CHARACTER SET utf8mb3 COLLATE utf8_general_ci NOT NULL COMMENT '自我介绍',
      `rules` char(4) CHARACTER SET utf8mb3 COLLATE utf8_general_ci NOT NULL COMMENT '是否同意规则',
      `ip` char(40) CHARACTER SET utf8mb3 COLLATE utf8_general_ci NOT NULL COMMENT '答题时ip地址',
      `token` char(16) CHARACTER SET utf8mb3 COLLATE utf8_general_ci NOT NULL COMMENT '秘钥',
      `score` float NOT NULL COMMENT '分数',
      `number` int NOT NULL COMMENT '答题次数',
      `used` tinyint(1) DEFAULT NULL COMMENT '是否已使用',
      `locked` tinyint(1) DEFAULT NULL COMMENT '是否被锁定',
      `pass` tinyint(1) DEFAULT NULL COMMENT '是否通过',
      `passinfo` text CHARACTER SET utf8mb3 COLLATE utf8_general_ci COMMENT '补充说明',
      PRIMARY KEY (`id`,`account`,`PlayerName`,`token`),
      UNIQUE KEY `id` (`id`,`account`,`PlayerName`,`UserSource`,`GameVersion`,`token`) USING BTREE
    ) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb3""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS `whitelist` (
      `id` int NOT NULL COMMENT '唯一id',
      `account` char(30) CHARACTER SET utf8mb3 COLLATE utf8_general_ci NOT NULL COMMENT '账号',
      `PlayerName` char(16) CHARACTER SET utf8mb3 COLLATE utf8_general_ci NOT NULL COMMENT '玩家名',
      `UserSource` char(4) CHARACTER SET utf8mb3 COLLATE utf8_general_ci NOT NULL COMMENT '账号类型',
      `GameVersion` char(4) CHARACTER SET utf8mb3 COLLATE utf8_general_ci NOT NULL COMMENT '游戏版本',
      `token` char(16) CHARACTER SET utf8mb3 COLLATE utf8_general_ci NOT NULL COMMENT '秘钥',
      PRIMARY KEY (`id`,`token`),
      UNIQUE KEY `id` (`id`,`account`,`PlayerName`,`UserSource`,`GameVersion`,`token`) USING BTREE,
      CONSTRAINT `id` FOREIGN KEY (`id`, `account`, `PlayerName`, `UserSource`, `GameVersion`, `token`) REFERENCES `wait` (`id`, `account`, `PlayerName`, `UserSource`, `GameVersion`, `token`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS `blacklist` (
      `id` int NOT NULL COMMENT '唯一id',
      `account` char(30) CHARACTER SET utf8mb3 COLLATE utf8_general_ci NOT NULL COMMENT '账号',
      `PlayerName` char(16) CHARACTER SET utf8mb3 COLLATE utf8_general_ci NOT NULL COMMENT '玩家名',
      `UserSource` char(4) CHARACTER SET utf8mb3 COLLATE utf8_general_ci NOT NULL COMMENT '账号类型',
      `GameVersion` char(4) CHARACTER SET utf8mb3 COLLATE utf8_general_ci NOT NULL COMMENT '游戏版本',
      `token` char(16) CHARACTER SET utf8mb3 COLLATE utf8_general_ci NOT NULL COMMENT '秘钥',
      `reason` text CHARACTER SET utf8mb3 COLLATE utf8_general_ci COMMENT '封禁原因',
      PRIMARY KEY (`id`,`token`),
      UNIQUE KEY `id` (`id`,`account`,`PlayerName`,`UserSource`,`GameVersion`,`token`) USING BTREE,
      CONSTRAINT `id1` FOREIGN KEY (`id`, `account`, `PlayerName`, `UserSource`, `GameVersion`, `token`) REFERENCES `wait` (`id`, `account`, `PlayerName`, `UserSource`, `GameVersion`, `token`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS `usedname` (
     `PlayerName` char(16) NOT NULL,
     `account` char(30) NOT NULL,
     PRIMARY KEY (`account`,`PlayerName`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3""")

    logger.success("数据表创建完成")

