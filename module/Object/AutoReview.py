from mirai.models.events import MemberJoinRequestEvent, GroupMessage
from mirai.models.message import Plain
from mirai_extensions.trigger import Filter

from module.BasicModule.Config import MainConfig
from module.Interlining.Bot import bot, message, interrupt
from module.Interlining.UsefulTools import IsAdminGroup, IsPlayerGroup

count: int = 1
processing: int = 1


@bot.on(MemberJoinRequestEvent)
async def ReviewJoin(event: MemberJoinRequestEvent):
    memberId = event.from_id
    groupId = event.group_id
    if not IsAdminGroup(groupId):
        memberInfo = await bot.user_profile(memberId)
        global count, processing
        temp = count
        send = "[{groupName}]有一条入群申请:\n" + f"QQ名: {memberInfo.nickname}\nQQ号: {memberId}\n等级: {memberInfo.level}\n" \
                                                  f"年龄: {memberInfo.age}\n入群信息：\n{event.message}\n个性签名: {memberInfo.sign}\n" + "处理结果：{result}"
        # if (MainConfig.AutomaticReview.age.min <= memberInfo.age <= MainConfig.AutomaticReview.age.max) and \
        #         memberInfo.level >= MainConfig.AutomaticReview.level:
        #     await bot.allow(event)
        #     await message.AdminMessage(send.format(
        #         groupName=message.PlayerName if IsPlayerGroup(groupId) else (await bot.get_group(groupId)).name,
        #         result="满足入群条件，已同意"))
        # elif MainConfig.AutomaticReview.Refuse:
        #     await message.AdminMessage(send.format(
        #         groupName=message.PlayerName if IsPlayerGroup(groupId) else (await bot.get_group(groupId)).name,
        #         result="未满足入群条件，已自动拒绝"))
        #     await bot.decline(event, "未达到入群要求", ban=MainConfig.AutomaticReview.BlackList)
        # else:
        #     await message.AdminMessage(send.format(
        #         groupName=message.PlayerName if IsPlayerGroup(groupId) else (await bot.get_group(groupId)).name,
        #         result="未满足入群条件，需人工审核(是/否/拉黑/忽略)"))
        #     count += 1
        if str(memberId) in list(vars(MainConfig.AutomaticAuditConfig).keys()):
            Group_AutomaticAuditConfig = vars(MainConfig.AutomaticAuditConfig)[str(memberId)]
            Join_Group_Answer = event.message.lower()
            Signature = memberInfo.sign.lower()
            Refuse = None

            if (
                    not Group_AutomaticAuditConfig.Pass_All and not Group_AutomaticAuditConfig.Refuse_All
            ):
                # QQ等级判断
                if (
                        not memberInfo.level >= Group_AutomaticAuditConfig.Pass_config.Pass_min_level and
                        Refuse is None
                ):
                    Refuse = {
                        "error_code": 0,
                        "error_msg": "QQ等级未满足要求",
                        "ban": True
                    }
                # 年龄判断
                if (
                        not memberInfo.age >= Group_AutomaticAuditConfig.Pass_config.Pass_min_Age and
                        Refuse is None
                ):
                    Refuse = {
                        "error_code": 1,
                        "error_msg": "年龄未满足要求",
                        "ban": True
                    }
                # 进群问答
                if (
                        Group_AutomaticAuditConfig.Pass_config.Join_Group_Answer_Keyword_Review and
                        Refuse is None
                ):
                    if event.message in Group_AutomaticAuditConfig.Keyword_config.Join_Group_Answer_Keyword.Refuse_Keywords:
                        for key, value in vars(Group_AutomaticAuditConfig.Keyword_config.Join_Group_Answer_Keyword.Refuse_Keywords).values():
                            if event.message in key:
                                Refuse = {
                                    "error_code": 2.1,
                                    "error_msg": str(value),
                                    "ban": False
                                }
                    else:
                        if not event.message in Group_AutomaticAuditConfig.Keyword_config.Join_Group_Answer_Keyword.Pass_Keywords:
                            Refuse = {
                                "error_code": 2.2,
                                "error_msg": "未能解析的进群原因",
                                "ban": False
                            }
                # QQ签名
                if (
                        Group_AutomaticAuditConfig.Pass_config.Signature_Refuse_Keyword and
                        memberInfo.sign in Group_AutomaticAuditConfig.Keyword_config.Signature_Refuse_Keyword and
                        Refuse is None
                ):
                    Refuse = {
                        "error_code": 3,
                        "error_msg": "签名有违规字符",
                        "ban": True
                    }
                # 拒绝/同意
                if (
                        Group_AutomaticAuditConfig.Pass_config.Auto_Pass_Manual_Audit and
                        Refuse is None
                ):
                    await bot.allow(event)
                    await message.AdminMessage(send.format(
                        groupName=message.PlayerName if IsPlayerGroup(groupId) else (await bot.get_group(groupId)).name,
                        result="已满足进群要求，已自动通过"))
                elif (
                        not Group_AutomaticAuditConfig.Pass_config.Auto_Pass_Manual_Audit and
                        Refuse is None
                ):
                    await message.AdminMessage(send.format(
                        groupName=message.PlayerName if IsPlayerGroup(groupId) else (await bot.get_group(groupId)).name,
                        result="已满足进群要求，但根据设置需人工审核(是/否/拉黑/忽略)"))
                    count += 1
                elif (
                        Group_AutomaticAuditConfig.Pass_config.Auto_Refuse_Manual_Audit and
                        Refuse is not None
                ):
                    await message.AdminMessage(send.format(
                        groupName=message.PlayerName if IsPlayerGroup(groupId) else (await bot.get_group(groupId)).name,
                        result="未满足入群条件，需人工审核(是/否/拉黑/忽略)"))
                    count += 1
                elif (
                        not Group_AutomaticAuditConfig.Pass_config.Auto_Refuse_Manual_Audit and
                        Refuse is not None
                ):
                    await bot.decline(event, Refuse["error_msg"], ban=Refuse["ban"])
                    await message.AdminMessage(send.format(
                        groupName=message.PlayerName if IsPlayerGroup(groupId) else (await bot.get_group(groupId)).name,
                        result="未满足入群条件，根据设置已自动拒绝"))
            elif (
                    Group_AutomaticAuditConfig.Refuse_All
            ):
                await bot.decline(event, "该群不允许其他人进入", ban=True)
            elif (
                    Group_AutomaticAuditConfig.Pass_All
            ):
                await bot.allow(event)

        @Filter(GroupMessage)
        def WaitCommit(msg: GroupMessage):
            if msg.message_chain.has(Plain) and IsAdminGroup(msg.group.id) and temp == processing:
                res = msg.message_chain.get_first(Plain).text
                if res.startswith("是"):
                    return {
                        "code": 1
                    }
                elif res.startswith("否"):
                    if len(res) > 1:
                        return {
                            "code": 2,
                            "message": res[2:]
                        }
                    else:
                        return {
                            "code": 3
                        }
                elif res.startswith("忽略"):
                    if len(res) > 2:
                        return {
                            "code": 4,
                            "message": res[3:]
                        }
                    else:
                        return {
                            "code": 5
                        }
                elif res.startswith("忽略"):
                    return {
                        "code": 6
                    }

        data = await interrupt.wait(WaitCommit)
        match data["code"]:
            case 1:
                await message.AdminMessage("已同意")
                await bot.allow(event)
            case 2:
                await message.AdminMessage(f"已拒绝, 理由:{data['message']}")
                await bot.decline(event, data["message"])
            case 3:
                await message.AdminMessage(f"已拉黑")
                await bot.decline(event, "未达到入群标准")
            case 4:
                await message.AdminMessage("已拉黑")
                await bot.decline(event, data["message"], ban=True)
            case 5:
                await message.AdminMessage("已拒绝")
                await bot.decline(event, "未达到入群标准", ban=True)
            case 6:
                await message.AdminMessage("已忽略")
                await bot.ignore(event)
        processing += 1
