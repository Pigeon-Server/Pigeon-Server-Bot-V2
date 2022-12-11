from mirai.models.events import MemberJoinRequestEvent, GroupMessage
from mirai.models.message import Plain
from mirai_extensions.trigger import Filter

from module.module_base.config import main_config
from module.module_interlining.bot import bot, message, interrupt
from module.module_interlining.useful_tools import is_admin_group, is_player_group
from module.module_class.config_class import GroupUnit

count: int = 1


@bot.on(MemberJoinRequestEvent)
async def review_join(event: MemberJoinRequestEvent):
    memberId = event.from_id
    groupId = event.group_id
    if not is_admin_group(groupId):
        memberInfo = await bot.user_profile(memberId)
        global count
        temp = count
        send = "[{groupName}]有一条入群申请:\n" \
               f"处理id: {count}" \
               f"QQ名: {memberInfo.nickname}\n" \
               f"QQ号: {memberId}\n" \
               f"等级: {memberInfo.level}\n" \
               f"年龄: {memberInfo.age}\n" \
               f"入群信息：\n{event.message}\n" \
               f"个性签名: {memberInfo.sign}\n" \
               "处理结果：{result}"
        if str(memberId) in list(vars(main_config.automatic_audit_config).keys()):
            GAAConfig: GroupUnit = vars(main_config.automatic_audit_config)[str(memberId)]
            Refuse = None

            async def send_info(result: str) -> None:
                await message.send_admin_message(send.format(
                    groupName=message.player_name if is_player_group(groupId) else (
                        await bot.get_group(groupId)).name,
                    result=result))

            def check_answer(msg: str) -> bool:
                for _key in GAAConfig.keyword_config.join_group_answer_keyword.pass_keywords:
                    if _key in msg:
                        return True
                return False

            async def final_step() -> None:
                if Refuse is None:
                    if GAAConfig.audit_config.pass_config.auto_pass_manual_audit:
                        await bot.allow(event)
                        await send_info("机审通过，已自动同意")
                    else:
                        await send_info("机审通过，等待人工复核(同意/拒绝/ban + id)")
                        await manual_audit()
                else:
                    if GAAConfig.audit_config.pass_config.auto_refuse_manual_audit:
                        await send_info("机审未通过，等待人工审核(同意/拒绝)")
                        await manual_audit()
                    else:
                        await bot.decline(event, Refuse["error_msg"], ban=Refuse["ban"])
                        await send_info("机审未通过，已拒绝入群")

            async def manual_audit():
                @Filter(GroupMessage)
                def wait_commit(msg: GroupMessage):
                    if is_admin_group(msg.group.id):
                        res = str(msg.message_chain).rsplit(" ")
                        if len(res) < 2 or res[1] != temp:
                            return
                        if res[0] == "同意":
                            return {
                                "status": 1
                            }
                        elif res[0] == "拒绝":
                            if len(res) == 3:
                                return {
                                    "status": 2,
                                    "message": res[2]
                                }
                            return {
                                "status": 2
                            }
                        elif res[0] == "ban":
                            if len(res) == 3:
                                return {
                                    "status": 3,
                                    "message": res[2]
                                }
                            return {
                                "status": 3
                            }

                data: dict = await interrupt.wait(wait_commit, timeout=3600)
                if data is None:
                    await message.send_admin_message(f"审核id为{temp}的请求已废弃")
                else:
                    if data["status"] == 1:
                        try:
                            await bot.allow(event)
                        except:
                            await message.send_admin_message("出现未知错误")
                        else:
                            await message.send_admin_message(f"已同意序号为{temp}的入群申请")
                    elif data["status"] == 2:
                        if "message" in data.keys():
                            try:
                                await bot.decline(event, data["message"])
                            except:
                                await message.send_admin_message("出现未知错误")
                            else:
                                await message.send_admin_message(f"已拒绝序号为{temp}的入群申请\n"
                                                           f"拒绝理由为:{data['message']}")
                        else:
                            try:
                                await bot.decline(event)
                            except:
                                await message.send_admin_message("出现未知错误")
                            else:
                                await message.send_admin_message(f"已拒绝序号为{temp}的入群申请")
                    elif data["status"] == 3:
                        if "message" in data.keys():
                            try:
                                await bot.decline(event, data["message"], ban=True)
                            except:
                                await message.send_admin_message("出现未知错误")
                            else:
                                await message.send_admin_message(f"已拒绝序号为{temp}的入群申请并封禁\n"
                                                           f"拒绝理由为:{data['message']}")
                        else:
                            try:
                                await bot.decline(event, ban=True)
                            except:
                                await message.send_admin_message("出现未知错误")
                            else:
                                await message.send_admin_message(f"已拒绝序号为{temp}的入群申请并封禁")

            if GAAConfig.audit_config.manual_audit_all:
                await send_info("该群不允许机审，等待人工审核")
                await manual_audit()
            elif GAAConfig.audit_config.refuse_all:
                await bot.decline(event, "该群不允许其他人进入", ban=True)
                await send_info("该群不允许其他人进入, 已自动拒绝")
            elif GAAConfig.audit_config.pass_all:
                await bot.allow(event)
                await send_info("该群所有人都能进入，已自动同意")
            else:
                # QQ等级判断
                if memberInfo.level < GAAConfig.audit_config.pass_config.pass_min_level:
                    Refuse = {
                        "error_code": 0,
                        "error_msg": "QQ等级未满足要求",
                        "ban": True
                    }
                    await final_step()
                # 年龄判断
                elif memberInfo.age < GAAConfig.audit_config.pass_config.pass_min_age:
                    Refuse = {
                        "error_code": 1,
                        "error_msg": "年龄未满足要求",
                        "ban": True
                    }
                    await final_step()
                # 进群问答
                elif GAAConfig.audit_config.pass_config.join_group_answer_keyword_review:
                    if check_answer(event.message.lower()):
                        for key, value in vars(GAAConfig.keyword_config.join_group_answer_keyword.refuse_keywords).values():
                            if key in event.message.lower():
                                Refuse = {
                                    "error_code": 2.1,
                                    "error_msg": str(value),
                                    "ban": False
                                }
                                break
                        await final_step()
                    else:
                        Refuse = {
                            "error_code": 2.2,
                            "error_msg": "未能解析的进群原因",
                            "ban": False
                        }
                        await final_step()
                # QQ签名
                elif GAAConfig.audit_config.pass_config.signature_refuse_keyword:
                    for item in GAAConfig.keyword_config.signature_refuse_keyword:
                        if item in memberInfo.sign:
                            Refuse = {
                                "error_code": 3,
                                "error_msg": "签名有违规字符",
                                "ban": True
                            }
                            break
                    await final_step()
