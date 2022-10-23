from module.Interlining.Bot import bot, message, interrupt
from mirai_extensions.trigger import Filter
from module.Interlining.UsefulTools import IsAdminGroup, IsPlayerGroup
from mirai.models.events import MemberJoinRequestEvent, GroupMessage
from mirai.models.message import Plain
from module.BasicModule.Config import MainConfig

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
        if (MainConfig.AutomaticReview.age.min <= memberInfo.age <= MainConfig.AutomaticReview.age.max) and \
                memberInfo.level >= MainConfig.AutomaticReview.level:
            await bot.allow(event)
            await message.AdminMessage(send.format(
                groupName=message.PlayerName if IsPlayerGroup(groupId) else (await bot.get_group(groupId)).name,
                result="满足入群条件，已同意"))
        elif MainConfig.AutomaticReview.Refuse:
            await message.AdminMessage(send.format(
                groupName=message.PlayerName if IsPlayerGroup(groupId) else (await bot.get_group(groupId)).name,
                result="未满足入群条件，已自动拒绝"))
            await bot.decline(event, "未达到入群要求", ban=MainConfig.AutomaticReview.BlackList)
        else:
            await message.AdminMessage(send.format(
                groupName=message.PlayerName if IsPlayerGroup(groupId) else (await bot.get_group(groupId)).name,
                result="未满足入群条件，需人工审核(是/否/拉黑/忽略)"))
            count += 1

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
