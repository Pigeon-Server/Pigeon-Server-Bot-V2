from mirai.models.events import MemberJoinRequestEvent, GroupMessage, MemberJoinEvent
from mirai_extensions.trigger import Filter

from module.module_base.config import main_config
from module.module_interlining.bot import bot, message, interrupt
from module.module_interlining.useful_tools import is_admin_group, is_player_group
from module.module_class.config_class import GroupUnit

count: int = 1
in_progress: list = []


@bot.on(MemberJoinEvent)
async def listen_to_group_entry(event: MemberJoinEvent):
    in_progress.remove(event.member.id)


@bot.on(MemberJoinRequestEvent)
async def review_join(event: MemberJoinRequestEvent):
    member_id = event.from_id
    group_id = event.group_id
    if not is_admin_group(group_id):
        member_info = await bot.user_profile(member_id)
        global count
        temp = count
        send = "[{groupName}]有一条入群申请:\n" \
               f"处理id: {count}\n" \
               f"QQ名: {member_info.nickname}\n" \
               f"QQ号: {member_id}\n" \
               f"等级: {member_info.level}\n" \
               f"年龄: {member_info.age}\n" \
               f"入群信息：\n{event.message}\n" \
               f"个性签名: {member_info.sign}\n" \
               "处理结果：{result}\n" \
               "处理详情: {info}"
        count += 1
        if str(group_id) in list(vars(main_config.automatic_config).keys()):
            GAAConfig: GroupUnit = vars(main_config.automatic_config)[str(group_id)]
            Refuse = None

            async def send_info(result: str) -> None:
                await message.send_admin_message(send.format(
                    groupName=message.player_name if is_player_group(group_id) else (
                        await bot.get_group(group_id)).name,
                    result=result, info="核验通过" if Refuse is None else Refuse["error_msg"]))

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
                        await send_info("机审未通过，等待人工审核(同意/拒绝 + id)")
                        await manual_audit()
                    else:
                        await bot.decline(event, Refuse["error_msg"], ban=Refuse["ban"])
                        await send_info("机审未通过，已拒绝入群")

            async def manual_audit():
                in_progress.append(member_id)

                @Filter(GroupMessage)
                def wait_commit(msg: GroupMessage):
                    if member_id not in in_progress:
                        return {
                            "status": 4
                        }
                    if is_admin_group(msg.group.id):
                        res = str(msg.message_chain).rsplit(" ")
                        if len(res) < 2 or res[1] != str(temp):
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
                    match data["status"]:
                        case 1:
                            try:
                                await bot.allow(event)
                            except:
                                await message.send_admin_message("出现未知错误")
                            else:
                                await message.send_admin_message(f"已同意序号为{temp}的入群申请")
                        case 2:
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
                                    await bot.decline(event, Refuse["error_msg"])
                                except:
                                    await message.send_admin_message("出现未知错误")
                                else:
                                    await message.send_admin_message(f"已拒绝序号为{temp}的入群申请")
                        case 3:
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
                                    await bot.decline(event, Refuse["error_msg"], ban=True)
                                except:
                                    await message.send_admin_message("出现未知错误")
                                else:
                                    await message.send_admin_message(f"已拒绝序号为{temp}的入群申请并封禁")
                        case 4:
                            await message.send_admin_message(f"管理员已手动同意序号为{temp}的入群申请")

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
                if member_info.level < GAAConfig.audit_config.pass_config.pass_min_level:
                    Refuse = {
                        "error_code": 0,
                        "error_msg": "QQ等级未满足要求",
                        "ban": False
                    }
                    await final_step()
                    return
                # 年龄判断
                if member_info.age < GAAConfig.audit_config.pass_config.pass_min_age:
                    Refuse = {
                        "error_code": 1,
                        "error_msg": "年龄未满足要求",
                        "ban": False
                    }
                    await final_step()
                    return
                # 进群问答
                if GAAConfig.audit_config.pass_config.join_group_answer_keyword_review:
                    temp_ = vars(GAAConfig.keyword_config.join_group_answer_keyword.refuse_keywords)
                    for key in temp_.keys():
                        if temp_[key] in event.message.lower():
                            Refuse = {
                                "error_code": 2.1,
                                "error_msg": str(temp_[key]),
                                "ban": False
                            }
                            await final_step()
                            return
                    if not check_answer(event.message.lower()):
                        Refuse = {
                            "error_code": 2.2,
                            "error_msg": "未能解析的进群原因",
                            "ban": False
                        }
                        await final_step()
                        return
                # QQ签名
                if GAAConfig.audit_config.pass_config.signature_refuse_keyword:
                    for item in GAAConfig.keyword_config.signature_refuse_keyword:
                        if item in member_info.sign:
                            Refuse = {
                                "error_code": 3,
                                "error_msg": "签名有违规字符",
                                "ban": True
                            }
                            await final_step()
                            return
                await final_step()
