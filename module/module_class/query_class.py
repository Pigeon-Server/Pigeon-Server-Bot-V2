from module.module_base.sql_relate import cursor


class QueryClass:
    @staticmethod
    def get_wait_list() -> str:
        if cursor.execute("select * from wait where pass is null and locked is not true and used is true"):
            data = cursor.fetchall()
            output = ""
            for raw in data:
                output += f"序号: {raw[0]}\n" \
                          f"玩家名: {raw[2]}\n"
            return output.removesuffix("\n")
        else:
            return "未查询到待审核玩家"
