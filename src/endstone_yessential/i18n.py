"""
YEssential I18n - 多语言系统
硬编码字典兜底 + JSON 文件覆盖，%s 格式化
"""
import json
import os
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# 默认翻译（硬编码兜底，确保无 JSON 也能运行）
# ═══════════════════════════════════════════════════════════

default_translations = {
    "zh_CN": {
        "economy.coin": "金币",
        "economy.query": "查询%s",
        "economy.transfer": "转账%s",
        "economy.transfer_offline": "转账给离线玩家",
        "economy.history": "查看%s历史记录",
        "economy.ranking": "%s排行榜",
        "economy.redpacket": "红包",
        "economy.admin_add": "增加玩家的%s",
        "economy.admin_reduce": "减少玩家的%s",
        "economy.admin_set": "设置玩家的%s",
        "economy.admin_offline": "对离线玩家进行金币操作",
        "economy.admin_look": "查看玩家的%s",
        "economy.admin_history": "查看玩家的%s历史记录",
        "economy.admin_ranking": "全服%s排行榜",
        "economy.player_menu": "使用玩家的金钱菜单",
        "economy.back": "返回",
        "economy.back_btn": "§c返回",
        "economy.confirm_btn": "§a确认转账",
        "economy.confirm_btn2": "§a确认",
        "economy.cancel_btn": "§c取消",
        "economy.confirm_title": "§6确认转账",
        "economy.confirm_offline_title": "§6确认离线转账",
        "economy.confirm_admin_title": "§6确认操作",
        "economy.transfer_title": "§6转账%s",
        "economy.tax_info": "税率: %s",
        "economy.amount_label": "转账金额",
        "economy.note_label": "备注(可选)",
        "economy.add_op": "增加",
        "economy.reduce_op": "减少",
        "economy.set_op": "设置",
        "economy.op_type_label": "操作类型",
        "economy.select_player": "选择玩家",
        "economy.amount": "金额",
        "economy.note": "备注(可选)",
        "economy.offline_target": "目标玩家名",
        "economy.op_type": "操作类型",
        "economy.add": "增加",
        "economy.reduce": "减少",
        "economy.set": "设置",
        "economy.confirm_transfer": "确认转账",
        "economy.confirm_offline": "确认离线转账",
        "economy.confirm_operation": "确认操作",
        "economy.confirm": "确认",
        "economy.cancel": "取消",
        "economy.balance": "§7当前余额: §a%s %s",
        "economy.player_balance": "§a玩家 %s 的余额为: §e%s",
        "economy.offline_balance": "§a玩家 %s(离线) 的余额为: §e%s",
        "economy.not_enough": "§c余额不足",
        "economy.no_permission": "§c你没有权限管理经济。",
        "economy.need_number": "§c金额必须是数字。",
        "economy.must_positive": "§c金额必须大于0。",
        "economy.must_nonneg": "§c金额不能为负。",
        "economy.player_only": "§c该命令只能由玩家执行。",
        "economy.player_offline": "§c玩家 %s 已离线。",
        "economy.player_online": "§c玩家 %s 在线，请使用在线操作。",
        "economy.no_online": "§c当前没有其他在线玩家。",
        "economy.need_player_name": "§c请输入玩家名。",
        "economy.need_valid_number": "§c请输入有效数字。",
        "economy.cannot_self": "§c不能操作自己。",
        "economy.tax_too_high": "§c税额过高，请调整金额。",
        "economy.disabled": "§c该模块未启用。",
        "economy.send_success": "§a操作成功！%s %s → %s",
        "economy.receive_from": "§a收到来自 §e%s §a的: %s %s",
        "economy.admin_give": "§a已给 %s 增加 %s %s。",
        "economy.admin_take": "§a已从 %s 扣除 %s %s。",
        "economy.admin_set_to": "§a已将 %s 的%s设置为 %s。",
        "economy.no_history": "§c暂无历史记录",
        "economy.history_title": "%s 的 %s 历史",
        "economy.ranking_title": "§6■ 财富排行榜 ■ §8[前%s名]",
        "economy.ranking_total": "§7服务器总财富: §6%s",
        "economy.ranking_yours": "§a你的余额: %s",
        "economy.no_ranking": "§c暂无排行榜数据。",
        "economy.transfer_content": "§7转账给 §a%s\n§7金额: §e%s %s\n§7税率: §e%s\n§7税额: §c%s\n§7到账: §a%s",
        "economy.offline_warn": "§c⚠ 对方将在上线时收到金币。",
        "economy.offline_target_online": "§c目标玩家在线，请使用在线操作。",
        "economy.offline_cached": "§a已缓存离线操作 → %s",
        "economy.transfer_note": "§7备注:§f%s",

        "home.set": "§a家园 §e%s §a已设置。",
        "home.deleted": "§c家园 §e%s §c已删除。",
        "home.not_found": "§c家园 §e%s §c不存在。",
        "home.teleported": "§a已传送到家园 §e%s§a。",
        "home.title": "§6家园系统",
        "home.set_new": "§a设置新家",
        "home.options_title": "§6家园: %s",
        "home.teleport_btn": "§a传送到此家",
        "home.delete_btn": "§c删除此家",
        "home.back": "§c返回",
        "home.set_title": "§6设置家园",
        "home.name_label": "请输入家园名称",

        "warp.set": "§a传送点 §e%s §a已设置。",
        "warp.deleted": "§c传送点 §e%s §c已删除。",
        "warp.not_found": "§c传送点 §e%s §c不存在。",
        "warp.teleported": "§a已传送到传送点 §e%s§a。",
        "warp.title": "§6传送点系统",
        "warp.set_new": "§a设置新传送点",
        "warp.admin_only": "§c只有管理员可以%s传送点。",
        "warp.set_title": "§6设置传送点",
        "warp.name_label": "请输入传送点名称",

        "tpa.sent": "§7已向 §a%s §7发送传送请求。",
        "tpa.request_title": "§6传送请求",
        "tpa.request_to": "§a%s §7请求传送至您的位置。",
        "tpa.accept": "§a接受",
        "tpa.reject": "§c拒绝",
        "tpa.accepted": "§7您已接受来自 §a%s §7的传送请求。",
        "tpa.sender_accepted": "§a%s §7接受了您的传送请求。",
        "tpa.rejected": "§7您已拒绝来自 §a%s §7的传送请求。",
        "tpa.sender_rejected": "§a%s §7拒绝了您的传送请求。",
        "tpa.no_pending": "§c没有待处理的传送请求。",
        "tpa.already_pending": "§c你已有待处理的传送请求，请等待对方回应。",
        "tpa.timeout": "§c请求已超时。",
        "tpa.offline": "§c玩家 %s 已离线。",
        "tpa.no_target": "§c玩家 %s 不在线。",
        "tpa.title": "§6传送请求 - 选择玩家",
        "tpa.no_players": "§c当前没有其他在线玩家。",
        "tpa.close": "§c关闭",
        "tpa.usage": "§c用法: /tpa <player>",

        "notice.title": "§6服务器公告",
        "notice.added": "§a公告已添加。",
        "notice.deleted": "§a公告 %s 已删除。",
        "notice.add_btn": "§a添加公告",
        "notice.close": "§c关闭",
        "notice.add_title": "§6添加公告",
        "notice.content_label": "请输入公告内容",

        "back.title": "§6死亡回溯",
        "back.recorded": "§c死亡点已记录，输入 /back 返回。记录了 %s 个死亡点。",
        "back.teleported": "§a已传送到死亡点。",
        "back.empty": "§c当前没有记录的死亡点。",
        "back.no_death": "§c你似乎还没有死亡过。",
        "back.invalid_index": "§c无效的死亡点索引。",
        "back.close": "§c关闭",
        "back.count": "§7您共有 %s 个记录的死亡点。",
        "back.sec_ago": "%s秒前",
        "back.min_ago": "%s分钟前",
        "back.hour_ago": "%s小时前",
        "back.day_ago": "%s天前",

        "pvp.title": "§6PVP 设置",
        "pvp.status": "§7当前状态: %s",
        "pvp.enabled": "§a开启",
        "pvp.disabled": "§c关闭",
        "pvp.set_on": "§7PVP 状态: §a开启§7。",
        "pvp.set_off": "§7PVP 状态: §c关闭§7。",
        "pvp.on_btn": "§a开启 PVP",
        "pvp.off_btn": "§c关闭 PVP",
        "pvp.close": "§c关闭",
        "pvp.usage": "§c用法: /pvp | /pvp on | /pvp off",

        "maintenance.enabled": "§c维护模式已开启。",
        "maintenance.disabled": "§a维护模式已关闭。",
        "maintenance.no_permission": "§c你没有权限使用此命令。",
        "maintenance.disabled_module": "§c该模块未启用。",
        "maintenance.kick_msg": "服务器正在维护中，请您稍后再来!",

        "hub.title": "§6回城菜单",
        "hub.teleported": "§a已传送至回城点。",
        "hub.teleport_now": "§a立即传送",
        "hub.cancel": "§c取消",
        "hub.disabled": "§c该模块未启用。",
        "hub.no_location": "§c无法获取传送位置。",
        "hub.set": "§a回城点已设置：",
        "hub.no_perm": "§c你没有权限设置回城点。",
        "hub.pos_info": "§e目标位置：\n§bX: §f%s\n§bY: §f%s\n§bZ: §f%s\n§b维度: §f%s",

        "servers.title": "§6跨服传送",
        "servers.disabled": "§c该模块未启用。",
        "servers.empty": "§c服务器列表为空。",
        "servers.unknown": "未知服务器",
        "servers.no_motd": "暂无描述",
        "servers.confirm_title": "确认要传送到以下服务器吗？",
        "servers.server_name_label": "服务器名：",
        "servers.confirm_warn": "⚠ 传送后将从当前服务器断开",
        "servers.confirm_yes": "§a确认传送",
        "servers.confirm_no": "§c取消",
        "servers.transferred": "§a%s 前往了 %s",
        "servers.fail": "§c传送失败: %s",

        "motd.default1": "§6YEssential §a服务器正在运行中！",
        "motd.default2": "§e欢迎来到 §bMinecraft §a服务器！",
        "motd.maintenance": "§c服务器维护中，请勿进入！",

        "fcam.disabled": "§c该模块未启用",
        "fcam.already": "§c你已经在灵魂出窍状态",
        "fcam.entered": "§a已进入灵魂出窍模式",
        "fcam.exited": "§a已退出灵魂出窍模式",
        "fcam.damage_exit": "§c受到伤害，已退出灵魂出窍模式",

        "sign.disabled": "§7签到功能已关闭",
        "sign.already": "§e今日已完成签到~",
        "sign.success": "§a签到成功！§e连续 §6%s §e天 ✦ 奖励：§f%s",
        "sign.milestone": "§b连续签到里程碑！§r §e第 §6%s§e 天附加奖励：§f%s",
        "sign.title": "§l§e每日签到",
        "sign.stats": "§e本月 §f%s §7次  §b连续 §f%s §7天  §a累计 §f%s §7次",
        "sign.sign_btn": "§l§a立即签到",
        "sign.signed_btn": "§8§l今日已签到",
        "sign.admin_title": "§3签到管理后台",
        "sign.admin_only": "§c仅管理员可用",
        "sign.admin_content": "§7当前服务器签到系统配置中心，请选择要管理的模块：",
        "sign.admin_economy": "§e§l经济参数查看\n§8查看当前经济模式与计分板",
        "sign.admin_params": "§a§l签到参数设置\n§8开关、随机范围、列数",
        "sign.admin_reward": "§6§l每日奖励序列\n§8配置每天的签到奖励",
        "sign.admin_items": "§d§l奖励物品库\n§8管理可用的物品奖励列表",
        "sign.admin_addition": "§b§l连续签到奖励\n§8设置连续打卡里程碑奖励",
        "sign.item": "物品",
        "sign.none": "无",
        "sign.random_item": "随机物品",
        "sign.random_money": "随机金币",
        "sign.random_exp": "随机经验",
        "sign.money_fmt": "%sx%s",
        "sign.exp_fmt": "经验x%s",
        "sign.monthly_title": "§7── 本月奖励一览 ──",
        "sign.prompt_sign": "§a▶ 点击按钮立即签到并领取今日奖励！",
        "sign.prompt_done": "§7今日已完成签到，明天再来吧~",
        "sign.gui_back": "§c返回",
        "sign.gui_on": "§a开启",
        "sign.gui_off": "§c关闭",
        "sign.gui_updated": "§a参数已更新",
        "sign.gui_economy_title": "§l§e经济参数概览",
        "sign.gui_economy_mode": "§e当前经济模式  §f%s",
        "sign.gui_economy_sb": "§e计分板名称    §f%s",
        "sign.gui_economy_coin": "§e货币单位名称  §f%s",
        "sign.gui_economy_note": "§7以上参数在 YEssential 主配置 Economy 块统一管理，此处仅供查看。",
        "sign.gui_params_title": "§l§a签到参数设置",
        "sign.gui_params_switch": "§l签到功能总开关§r §7(当前: %s§7)",
        "sign.gui_params_money_label": "§6§l随机金币范围",
        "sign.gui_params_money_min": "§e最小值§7 (当前: %s)",
        "sign.gui_params_money_max": "§e最大值§7 (当前: %s)",
        "sign.gui_params_exp_label": "§b§l随机经验范围",
        "sign.gui_params_exp_min": "§3最小值§7 (当前: %s)",
        "sign.gui_params_exp_max": "§3最大值§7 (当前: %s)",
        "sign.gui_params_layout_label": "§d§l界面布局",
        "sign.gui_params_layout": "§5每行列数§7 (当前: %s，范围 1~10)",
        "sign.gui_daily_title": "§6每日奖励序列",
        "sign.gui_daily_content": "§7共 %s 天\n选择要修改的天数：",
        "sign.gui_daily_day": "§e第%s天 §f%s",
        "sign.gui_day_edit_title": "修改第%s天奖励",
        "sign.gui_day_edit_type": "奖励类型",
        "sign.gui_day_edit_amount": "金币/经验数量(仅指定类型)",
        "sign.gui_day_updated": "§a第%s天奖励已更新",
        "sign.gui_items_title": "§d奖励物品库",
        "sign.gui_items_content": "§7共 %s 种物品\n§e管理物品库（影响随机物品和指定物品奖励）：",
        "sign.gui_addition_title": "§b连续签到附加奖励",
        "sign.gui_addition_list_title": "§l连续签到里程碑奖励：§r",
        "sign.gui_addition_item": "  §6第 §e%s §6天 → §a%s",
        "sign.gui_addition_empty": "  §7(暂未配置)",
        "sign.gui_addition_add": "§a添加/修改里程碑",
        "sign.gui_addition_del": "§c删除里程碑",
        "sign.gui_addition_none": "§c没有可删除的里程碑",
        "sign.gui_addition_edit_title": "添加/修改连续签到奖励",
        "sign.gui_addition_days": "连续天数(如: 7)",
        "sign.gui_addition_set": "§a连续签到第%s天奖励已设置",
        "sign.gui_addition_del_title": "删除里程碑",
        "sign.gui_addition_del_content": "选择要删除的：",
        "sign.gui_addition_day": "第%s天: %s",
        "sign.gui_addition_deleted": "§a已删除第%s天里程碑",

        "rtp.cooldown": "§c传送冷却中，剩余时间：%s秒",
        "rtp.cost": "§e花费 %s 金币",
        "rtp.need_money": "§c您需要 %s 金币",
        "rtp.searching": "§7正在搜索安全位置...",
        "rtp.success": "§a传送成功！位置: %s, %s, %s",
        "rtp.distance": "§e距离出生点: §f%s 格",
        "rtp.done": "§b传送完成！",
        "rtp.error": "§c传送错误",
        "rtp.refund": "§a已退还 %s 金币",

        "suicide.cooldown": "§c请等待 %s 秒后再试",
        "suicide.disabled": "§c自杀功能已禁用",

        "crash.no_perm": "§c你不是管理员",
        "crash.disabled": "§c该模块未启用",
        "crash.no_players": "§c当前没有其他在线玩家",
        "crash.title": "§c使玩家客户端崩溃",
        "crash.crashed": "§a已使 %s 客户端崩溃",
        "crash.fail": "§c崩溃操作失败",

        "reload": "§a配置已重载！",
        "no_permission": "§c你没有权限使用此命令。",
        "player_only": "§c该命令只能由玩家执行。",
        "version": "§7Version %s (Python Refactored)",
        "welcome": "§6[YEssential] §a欢迎回到服务器, %s!",
        "module_disabled": "§c该模块未启用。",

        "cleanmgr.prefix": "§l§6[-YEST-] §l§e[清理系统] §r",
        "cleanmgr.toast_title": "清理系统",
        "cleanmgr.cleanup_start": "§a开始清理实体...",
        "cleanmgr.cleanup_complete": "§a已清理 %s 个实体",
        "cleanmgr.low_tps_clean": "§cTPS 过低(%s)，已自动清理",
        "cleanmgr.low_tps_ineffective": "§c连续清理无效，冷却 %s 分钟",
        "cleanmgr.manual_trigger": "§6玩家触发了手动清理",
        "cleanmgr.cancel_success": "§c已取消计划清理",
        "cleanmgr.no_scheduled": "§c当前没有计划清理可取消",
        "cleanmgr.cooldown_msg": "§c触发清理冷却中，请稍后再试",
        "cleanmgr.status": "§a状态: %s",
        "cleanmgr.tps_info": "§a当前TPS: §e%s§a / 20.00",
        "cleanmgr.cleanup_notice": "§e将在 %s 秒后清理实体！",
        "cleanmgr.cleanup_notice2": "§e将在 %s 秒后清理实体！",
        "cleanmgr.cleanup_notice3": "§c将在 %s 秒后清理实体！请做好准备！",
        "cleanmgr.toast_toggle": "%s顶部弹窗通知",
        "cleanmgr.help": "§e用法:\n§a/clean §7- 触发清理\n§a/clean now §7- 立即清理\n§a/clean status §7- 查询状态\n§a/clean cancel §7- 取消清理\n§a/clean tps §7- 查询TPS\n§a/clean toast §7- 开关顶部弹窗",

        "suicide.killed": "§c你选择了结束自己的生命",
        "suicide.already_dead": "§c你已经死亡",
        "suicide.cooldown": "§c请等待 %s 秒后再试",
        "suicide.disabled": "§c自杀功能已禁用",

        "logo.author": "作者：",
        "logo.version": "版本：",
        "logo.thanks": "感谢您使用Easy系列插件！",
        "logo.license": "本插件使用 %s 许可证协议进行发布",
        "logo.github": "GitHub 仓库：%s",
        "logo.minebbs": "插件MineBBS资源帖：%s",
        "logo.qq_group": "Easy系列插件交流群：%s",
        "logo.enabled": "%s 已启用！",
        "logo.disabling": "%s 正在禁用...",
        "logo.disabled": "%s 已禁用!",
        "config.created": "已创建默认配置 (%s)",
        "config.migrated": "配置已从 %s 迁移到 %s",
        "config.load_failed": "加载配置失败: %s",
        "config.save_failed": "保存配置失败: %s",
        "config.recovering": "配置已损坏(%s)，已自动重建",
    },
    "en_US": {
        "economy.coin": "Coins",
        "economy.query": "Check %s",
        "economy.transfer": "Send %s",
        "economy.transfer_offline": "Send to Offline Player",
        "economy.history": "View %s History",
        "economy.ranking": "%s Leaderboard",
        "economy.redpacket": "Red Packet",
        "economy.admin_add": "Add Player's %s",
        "economy.admin_reduce": "Deduct Player's %s",
        "economy.admin_set": "Set Player's %s",
        "economy.admin_offline": "Offline Player Coins",
        "economy.admin_look": "View Player's %s",
        "economy.admin_history": "View Player's %s History",
        "economy.admin_ranking": "Server %s Leaderboard",
        "economy.player_menu": "Use Player Menu",
        "economy.back": "Back",
        "economy.back_btn": "§cBack",
        "economy.confirm_btn": "§aConfirm Transfer",
        "economy.confirm_btn2": "§aConfirm",
        "economy.cancel_btn": "§cCancel",
        "economy.confirm_title": "§6Confirm Transfer",
        "economy.confirm_offline_title": "§6Confirm Offline Transfer",
        "economy.confirm_admin_title": "§6Confirm Operation",
        "economy.transfer_title": "§6Send %s",
        "economy.tax_info": "Tax: %s",
        "economy.amount_label": "Amount",
        "economy.note_label": "Note (optional)",
        "economy.add_op": "Add",
        "economy.reduce_op": "Deduct",
        "economy.set_op": "Set",
        "economy.op_type_label": "Operation",
        "economy.select_player": "Select Player",
        "economy.amount": "Amount",
        "economy.note": "Note (optional)",
        "economy.offline_target": "Target Player Name",
        "economy.op_type": "Operation Type",
        "economy.add": "Add",
        "economy.reduce": "Deduct",
        "economy.set": "Set",
        "economy.confirm_transfer": "Confirm Transfer",
        "economy.confirm_offline": "Confirm Offline Transfer",
        "economy.confirm_operation": "Confirm Operation",
        "economy.confirm": "Confirm",
        "economy.cancel": "Cancel",
        "economy.balance": "§7Balance: §a%s %s",
        "economy.player_balance": "§aPlayer %s balance: §e%s",
        "economy.offline_balance": "§aPlayer %s(offline) balance: §e%s",
        "economy.not_enough": "§cInsufficient balance",
        "economy.no_permission": "§cNo permission to manage economy.",
        "economy.need_number": "§cAmount must be a number.",
        "economy.must_positive": "§cAmount must be > 0.",
        "economy.must_nonneg": "§cAmount cannot be negative.",
        "economy.player_only": "§cPlayers only.",
        "economy.player_offline": "§cPlayer %s is offline.",
        "economy.player_online": "§cPlayer %s is online, use online transfer.",
        "economy.no_online": "§cNo other players online.",
        "economy.need_player_name": "§cEnter a player name.",
        "economy.need_valid_number": "§cEnter a valid number.",
        "economy.cannot_self": "§cCannot target yourself.",
        "economy.tax_too_high": "§cTax too high, adjust amount.",
        "economy.disabled": "§cModule not enabled.",
        "economy.send_success": "§aSent! %s %s → %s",
        "economy.receive_from": "§aReceived from §e%s§a: %s %s",
        "economy.admin_give": "§aGave %s +%s %s.",
        "economy.admin_take": "§aTook -%s %s from %s.",
        "economy.admin_set_to": "§aSet %s's %s to %s.",
        "economy.no_history": "§cNo history",
        "economy.history_title": "%s's %s History",
        "economy.ranking_title": "§6■ Wealth Leaderboard ■ §8[Top %s]",
        "economy.ranking_total": "§7Server Total: §6%s",
        "economy.ranking_yours": "§aYour Balance: %s",
        "economy.no_ranking": "§cNo ranking data.",
        "economy.transfer_content": "§7To §a%s\n§7Amount: §e%s %s\n§7Tax: §e%s\n§7Tax Amt: §c%s\n§7Receive: §a%s",
        "economy.offline_warn": "§c⚠ They will receive coins on login.",
        "economy.offline_target_online": "§cPlayer is online, use online transfer.",
        "economy.offline_cached": "§aCached offline op → %s",
        "economy.transfer_note": "§7Note:§f%s",

        "home.set": "§aHome §e%s §aset.",
        "home.deleted": "§cHome §e%s §cdeleted.",
        "home.not_found": "§cHome §e%s §cnot found.",
        "home.teleported": "§aTeleported to home §e%s§a.",
        "home.title": "§6Home System",
        "home.set_new": "§aSet New Home",
        "home.options_title": "§6Home: %s",
        "home.teleport_btn": "§aTeleport Here",
        "home.delete_btn": "§cDelete Home",
        "home.back": "§cBack",
        "home.set_title": "§6Set Home",
        "home.name_label": "Enter home name",

        "warp.set": "§aWarp §e%s §aset.",
        "warp.deleted": "§cWarp §e%s §cdeleted.",
        "warp.not_found": "§cWarp §e%s §cnot found.",
        "warp.teleported": "§aTeleported to warp §e%s§a.",
        "warp.title": "§6Warp System",
        "warp.set_new": "§aSet New Warp",
        "warp.admin_only": "§cOnly admins can %s warps.",
        "warp.set_title": "§6Set Warp",
        "warp.name_label": "Enter warp name",

        "tpa.sent": "§7Sent teleport request to §a%s§7.",
        "tpa.request_title": "§6Teleport Request",
        "tpa.request_to": "§a%s §7requests to teleport to you.",
        "tpa.accept": "§aAccept",
        "tpa.reject": "§cReject",
        "tpa.accepted": "§7Accepted §a%s§7's request.",
        "tpa.sender_accepted": "§a%s §7accepted your request.",
        "tpa.rejected": "§7Rejected §a%s§7's request.",
        "tpa.sender_rejected": "§a%s §7rejected your request.",
        "tpa.no_pending": "§cNo pending teleport requests.",
        "tpa.already_pending": "§cYou already have a pending request, wait for a response.",
        "tpa.timeout": "§cRequest timed out.",
        "tpa.offline": "§cPlayer %s is offline.",
        "tpa.no_target": "§cPlayer %s is not online.",
        "tpa.title": "§6Teleport Request - Select Player",
        "tpa.no_players": "§cNo other players online.",
        "tpa.close": "§cClose",
        "tpa.usage": "§cUsage: /tpa <player>",

        "notice.title": "§6Server Notice",
        "notice.added": "§aNotice added.",
        "notice.deleted": "§aNotice %s deleted.",
        "notice.add_btn": "§aAdd Notice",
        "notice.close": "§cClose",
        "notice.add_title": "§6Add Notice",
        "notice.content_label": "Enter notice content",

        "back.title": "§6Death Back",
        "back.recorded": "§cDeath point recorded. /back to return. %s points recorded.",
        "back.teleported": "§aTeleported to death point.",
        "back.empty": "§cNo death points recorded.",
        "back.no_death": "§cYou haven't died yet.",
        "back.invalid_index": "§cInvalid death point index.",
        "back.close": "§cClose",
        "back.count": "§7You have %s death points.",
        "back.sec_ago": "%ss ago",
        "back.min_ago": "%smin ago",
        "back.hour_ago": "%sh ago",
        "back.day_ago": "%sd ago",

        "pvp.title": "§6PVP Settings",
        "pvp.status": "§7Status: %s",
        "pvp.enabled": "§aEnabled",
        "pvp.disabled": "§cDisabled",
        "pvp.set_on": "§7PVP: §aEnabled§7.",
        "pvp.set_off": "§7PVP: §cDisabled§7.",
        "pvp.on_btn": "§aEnable PVP",
        "pvp.off_btn": "§cDisable PVP",
        "pvp.close": "§cClose",
        "pvp.usage": "§cUsage: /pvp | /pvp on | /pvp off",

        "maintenance.enabled": "§cMaintenance mode enabled.",
        "maintenance.disabled": "§aMaintenance mode disabled.",
        "maintenance.no_permission": "§cNo permission.",
        "maintenance.disabled_module": "§cModule not enabled.",
        "maintenance.kick_msg": "Server is under maintenance. Come back later!",

        "hub.title": "§6Hub Menu",
        "hub.teleported": "§aTeleported to hub.",
        "hub.teleport_now": "§aTeleport Now",
        "hub.cancel": "§cCancel",
        "hub.disabled": "§cModule not enabled.",
        "hub.no_location": "§cCannot get teleport location.",
        "hub.set": "§aHub set:",
        "hub.no_perm": "§cNo permission to set hub.",
        "hub.pos_info": "§eTarget:\n§bX: §f%s\n§bY: §f%s\n§bZ: §f%s\n§bDim: §f%s",

        "servers.title": "§6Server Transfer",
        "servers.disabled": "§cModule not enabled.",
        "servers.empty": "§cServer list empty.",
        "servers.unknown": "Unknown Server",
        "servers.no_motd": "No description",
        "servers.confirm_title": "Confirm transfer to this server?",
        "servers.server_name_label": "Server: ",
        "servers.confirm_warn": "⚠ You will be disconnected from this server",
        "servers.confirm_yes": "§aTransfer",
        "servers.confirm_no": "§cCancel",
        "servers.transferred": "§a%s went to %s",
        "servers.fail": "§cTransfer failed: %s",

        "motd.default1": "§6YEssential §aServer Running!",
        "motd.default2": "§eWelcome to §bMinecraft §aServer!",
        "motd.maintenance": "§cUnder Maintenance. Do not enter!",

        "fcam.disabled": "§cModule not enabled",
        "fcam.already": "§cAlready in free camera mode",
        "fcam.entered": "§aEntered free camera mode",
        "fcam.exited": "§aExited free camera mode",
        "fcam.damage_exit": "§cTook damage! Free camera disabled.",

        "sign.disabled": "§7Sign-in disabled",
        "sign.already": "§eAlready signed in today~",
        "sign.success": "§aSigned in! §eStreak §6%s §edays ✦ Reward: §f%s",
        "sign.milestone": "§bStreak Milestone! §r §eDay §6%s§e Bonus: §f%s",
        "sign.title": "§l§eDaily Sign-in",
        "sign.stats": "§eMonth §f%s §7x  §bStreak §f%s §7d  §aTotal §f%s §7x",
        "sign.sign_btn": "§l§aSign In Now",
        "sign.signed_btn": "§8§lAlready Signed",
        "sign.admin_title": "§3Sign-in Admin",
        "sign.admin_only": "§cAdmin only",
        "sign.admin_content": "§7Sign-in system configuration, select a module:",
        "sign.admin_economy": "§e§lEconomy Info\n§8View economy mode & scoreboard",
        "sign.admin_params": "§a§lSign-in Settings\n§8Toggle, random range, columns",
        "sign.admin_reward": "§6§lDaily Reward List\n§8Edit daily rewards",
        "sign.admin_items": "§d§lItem Library\n§8Manage reward items",
        "sign.admin_addition": "§b§lStreak Rewards\n§8Set milestone bonuses",
        "sign.item": "Item",
        "sign.none": "None",
        "sign.random_item": "Random Item",
        "sign.random_money": "Random Coins",
        "sign.random_exp": "Random EXP",
        "sign.money_fmt": "%sx%s",
        "sign.exp_fmt": "EXP x%s",
        "sign.monthly_title": "§7── Monthly Rewards ──",
        "sign.prompt_sign": "§a▶ Click to sign in and claim today's reward!",
        "sign.prompt_done": "§7Already signed in today, come back tomorrow~",
        "sign.gui_back": "§cBack",
        "sign.gui_on": "§aON",
        "sign.gui_off": "§cOFF",
        "sign.gui_updated": "§aSettings updated",
        "sign.gui_economy_title": "§l§eEconomy Info",
        "sign.gui_economy_mode": "§eMode  §f%s",
        "sign.gui_economy_sb": "§eScoreboard  §f%s",
        "sign.gui_economy_coin": "§eCoin Name  §f%s",
        "sign.gui_economy_note": "§7These settings are in YEssential main config Economy section. Read-only.",
        "sign.gui_params_title": "§l§aSign-in Settings",
        "sign.gui_params_switch": "§lSign-in Switch§r §7(Current: %s§7)",
        "sign.gui_params_money_label": "§6§lRandom Money Range",
        "sign.gui_params_money_min": "§eMin§7 (Current: %s)",
        "sign.gui_params_money_max": "§eMax§7 (Current: %s)",
        "sign.gui_params_exp_label": "§b§lRandom EXP Range",
        "sign.gui_params_exp_min": "§3Min§7 (Current: %s)",
        "sign.gui_params_exp_max": "§3Max§7 (Current: %s)",
        "sign.gui_params_layout_label": "§d§lLayout",
        "sign.gui_params_layout": "§5Columns per row§7 (Current: %s, range 1~10)",
        "sign.gui_daily_title": "§6Daily Reward List",
        "sign.gui_daily_content": "§7%s days total\nSelect day to edit:",
        "sign.gui_daily_day": "§eDay %s §f%s",
        "sign.gui_day_edit_title": "Edit Day %s Reward",
        "sign.gui_day_edit_type": "Reward Type",
        "sign.gui_day_edit_amount": "Coin/EXP amount (specified type only)",
        "sign.gui_day_updated": "§aDay %s reward updated",
        "sign.gui_items_title": "§dItem Library",
        "sign.gui_items_content": "§7%s items\n§eItem library (affects random & specified item rewards):",
        "sign.gui_addition_title": "§bStreak Rewards",
        "sign.gui_addition_list_title": "§lStreak Milestone Rewards:§r",
        "sign.gui_addition_item": "  §6Day §e%s §6→ §a%s",
        "sign.gui_addition_empty": "  §7(None configured)",
        "sign.gui_addition_add": "§aAdd/Edit Milestone",
        "sign.gui_addition_del": "§cDelete Milestone",
        "sign.gui_addition_none": "§cNo milestones to delete",
        "sign.gui_addition_edit_title": "Add/Edit Streak Reward",
        "sign.gui_addition_days": "Consecutive days (e.g. 7)",
        "sign.gui_addition_set": "§aStreak day %s reward set",
        "sign.gui_addition_del_title": "Delete Milestone",
        "sign.gui_addition_del_content": "Select to delete:",
        "sign.gui_addition_day": "Day %s: %s",
        "sign.gui_addition_deleted": "§aDay %s milestone deleted",

        "rtp.cooldown": "§cRTP cooldown: %ss",
        "rtp.cost": "§eCost %s coins",
        "rtp.need_money": "§cYou need %s coins",
        "rtp.searching": "§7Searching safe location...",
        "rtp.success": "§aTeleported! Pos: %s, %s, %s",
        "rtp.distance": "§eDistance: §f%s blocks",
        "rtp.done": "§bTeleport complete!",
        "rtp.error": "§cTeleport error",
        "rtp.refund": "§aRefunded %s coins",

        "suicide.killed": "§cYou chose to end your life",
        "suicide.cooldown": "§cWait %ss",
        "suicide.disabled": "§cSuicide disabled",

        "crash.no_perm": "§cNot an admin",
        "crash.disabled": "§cModule not enabled",
        "crash.no_players": "§cNo other players online",
        "crash.title": "§cCrash Client",
        "crash.crashed": "§aCrashed %s's client",
        "crash.fail": "§cCrash failed",

        "reload": "§aConfig reloaded!",
        "no_permission": "§cNo permission.",
        "player_only": "§cPlayers only.",
        "version": "§7Version %s (Python Refactored)",
        "welcome": "§6[YEssential] §aWelcome back, %s!",
        "module_disabled": "§cModule not enabled.",

        "cleanmgr.prefix": "§l§6[-YEST-] §l§e[Cleanup] §r",
        "cleanmgr.toast_title": "Cleanup System",
        "cleanmgr.cleanup_start": "§aStarting entity cleanup...",
        "cleanmgr.cleanup_complete": "§aCleaned up %s entities",
        "cleanmgr.low_tps_clean": "§cLow TPS(%s), auto cleanup triggered",
        "cleanmgr.low_tps_ineffective": "§cCleanup ineffective, cooldown %s min",
        "cleanmgr.manual_trigger": "§6Manual cleanup triggered",
        "cleanmgr.cancel_success": "§cScheduled cleanup cancelled",
        "cleanmgr.no_scheduled": "§cNo scheduled cleanup to cancel",
        "cleanmgr.cooldown_msg": "§cCleanup on cooldown, try again later",
        "cleanmgr.status": "§aStatus: %s",
        "cleanmgr.tps_info": "§aCurrent TPS: §e%s§a / 20.00",
        "cleanmgr.cleanup_notice": "§eCleanup in %s seconds!",
        "cleanmgr.cleanup_notice2": "§eCleanup in %s seconds!",
        "cleanmgr.cleanup_notice3": "§cCleanup in %s seconds! Get ready!",
        "cleanmgr.toast_toggle": "%s toast notifications",
        "cleanmgr.help": "§eUsage:\n§a/clean §7- Trigger cleanup\n§a/clean now §7- Clean now\n§a/clean status §7- Status\n§a/clean cancel §7- Cancel\n§a/clean tps §7- TPS\n§a/clean toast §7- Toggle toast",

        "suicide.killed": "§cYou chose to end your life",
        "suicide.already_dead": "§cYou are already dead",
        "suicide.cooldown": "§cWait %s seconds",
        "suicide.disabled": "§cSuicide is disabled",

        "logo.author": "Author: ",
        "logo.version": "Version: ",
        "logo.thanks": "Thank you for using Easy Series Plugin!",
        "logo.license": "Licensed under %s",
        "logo.github": "GitHub: %s",
        "logo.minebbs": "MineBBS: %s",
        "logo.qq_group": "Easy Series QQ Group: %s",
        "logo.enabled": "%s enabled!",
        "logo.disabling": "%s disabling...",
        "logo.disabled": "%s disabled!",
        "config.created": "Default config created (%s)",
        "config.migrated": "Config migrated from %s to %s",
        "config.load_failed": "Failed to load config: %s",
        "config.save_failed": "Failed to save config: %s",
        "config.recovering": "Config corrupted(%s), auto-recovered",
    }
}


class I18n:
    def __init__(self, plugin):
        self.plugin = plugin
        self._translations: dict[str, dict] = {}
        self._locale = "zh_CN"
        self._ready = False

    def init(self):
        # 语言设置（配置可能尚未加载，默认 zh_CN）
        try:
            cfg = self.plugin.config_manager.config_data
            self._locale = cfg.get("Language", "zh_CN")
        except Exception:
            self._locale = "zh_CN"

        # 数据目录: plugins/YEssential/
        data_dir = Path(str(self.plugin.data_folder))
        langs_dir = data_dir / "langs"
        langs_dir.mkdir(parents=True, exist_ok=True)

        # 1) 硬编码字典兜底
        for lang, trans in default_translations.items():
            self._translations.setdefault(lang, {}).update(trans)

        # 2) 补齐缺失键值 + 清理旧版 key-as-value 残留
        for f in langs_dir.glob("*.json"):
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                updated = False
                for lang, trans in data.items():
                    if lang in default_translations:
                        defaults = default_translations[lang]
                        for k, v in list(trans.items()):
                            # 删除旧版自动追加的 key-as-value（键值相同的无效翻译）
                            if v == k and k in defaults:
                                trans[k] = defaults[k]
                                updated = True
                            # 补齐默认值
                            elif k not in trans or trans.get(k) == k:
                                if k in defaults:
                                    trans[k] = defaults[k]
                                    updated = True
                        # 补充缺失的键
                        for k, v in defaults.items():
                            if k not in trans:
                                trans[k] = v
                                updated = True
                    self._translations.setdefault(lang, {}).update(trans)
                if updated:
                    with open(f, "w", encoding="utf-8") as fh:
                        json.dump(data, fh, indent=4, ensure_ascii=False)
            except Exception:
                pass

        # 3) 首次运行：写出默认语言文件
        for lang, trans in default_translations.items():
            lang_file = langs_dir / f"{lang}.json"
            if not lang_file.exists():
                try:
                    with open(lang_file, "w", encoding="utf-8") as fh:
                        json.dump({lang: trans}, fh, indent=4, ensure_ascii=False)
                except Exception:
                    pass

        # 4) 回退
        if self._locale not in self._translations:
            self._locale = "zh_CN" if "zh_CN" in self._translations else list(self._translations.keys())[0]

        self._ready = True

    @property
    def locale(self) -> str:
        return self._locale

    def set_locale(self, loc: str):
        if loc in self._translations:
            self._locale = loc
            self.plugin.config_manager.set("Language", loc)

    def translate(self, key: str, *args) -> str:
        if not self._ready:
            return key

        lang_dict = self._translations.setdefault(self._locale, {})
        text = lang_dict.get(key)

        # 回退链：当前语言 → en_US → zh_CN
        if text is None:
            for fb in ("en_US", "zh_CN"):
                if fb == self._locale:
                    continue
                text = self._translations.get(fb, {}).get(key)
                if text is not None:
                    break

        # 未找到翻译 → 自动追加到当前语言文件
        if text is None:
            self._append_missing(key)
            return key

        if args:
            try:
                return text % args
            except (TypeError, ValueError):
                return text
        return text

    def _append_missing(self, key: str):
        """将缺失的翻译键自动追加到 langs 文件，优先用默认翻译"""
        # 查找默认翻译值
        value = key
        for loc in (self._locale, "zh_CN"):
            dv = default_translations.get(loc, {}).get(key)
            if dv is not None:
                value = dv
                break

        self._translations[self._locale][key] = value
        langs_dir = Path(str(self.plugin.data_folder)) / "langs"
        lang_file = langs_dir / f"{self._locale}.json"
        try:
            existing = {}
            if lang_file.exists():
                with open(lang_file, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            existing.setdefault(self._locale, {})[key] = value
            with open(lang_file, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

# ── 全局 ────────────────────────────────────────────────

_i18n: I18n = None


def init_i18n(plugin) -> I18n:
    global _i18n
    _i18n = I18n(plugin)
    _i18n.init()
    return _i18n


def get_i18n() -> I18n:
    return _i18n


def tr(key: str, *args) -> str:
    if _i18n:
        return _i18n.translate(key, *args)
    return key
