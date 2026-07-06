"""
YEssential Plugin - 主入口
基岩版多功能基础插件, 基于 Endstone 框架
"""
from endstone.plugin import Plugin
from endstone.event import event_handler, PacketReceiveEvent, PlayerJoinEvent, PlayerDeathEvent, PlayerRespawnEvent, ActorDamageEvent, ServerCommandEvent
from endstone.command import Command, CommandSender, CommandSenderWrapper
from endstone import Player
from typing import List

from .config import ConfigManager
from .economy import EconomySystem
from .home import HomeSystem
from .warp import WarpSystem
from .rtp import RTPSystem
from .tpa import TPASystem
from .notice import NoticeSystem
from .back import BackSystem
from .pvp import PVPSystem
from .maintenance import MaintenanceSystem
from .servers import ServersSystem
from .hub import HubSystem
from .motd import MotdSystem
from .cd import CdSystem
from .fcam import FcamSystem
from .redpacket import RedpacketSystem
from .crash import CrashSystem
from .cleanmgr import CleanmgrSystem
from .suicide import SuicideSystem
from .sign import SignSystem
from .i18n import init_i18n, get_i18n
from .update_checker import UpdateChecker
from .log import plugin_print
from .constant import *


def _is_simulated(player: Player) -> bool:
    """检查是否为模拟玩家(Fcam 创建的)"""
    return player.name.endswith("_sp")


class YEssentialPlugin(Plugin):
    api_version = "0.5"
    commands = {
        "yest": {
            "description": "YEssential 主命令",
            "usages": ["/yest", "/yest reload"],
            "aliases": ["yessential"],
            "permissions": ["yessential.command.yest"],
        },
        "money": {
            "description": "经济系统",
            "usages": ["/money", "/money give <player: target> <amount: int>", "/money take <player: target> <amount: int>", "/money set <player: target> <amount: int>"],
            "permissions": ["yessential.command.money"],
        },
        "moneygui": {
            "description": "金钱菜单",
            "usages": ["/moneygui"],
            "permissions": ["yessential.command.money"],
        },
        "moneys": {
            "description": "管理员金钱操作",
            "usages": ["/moneys <add|del|set|get|history> <player: target> [amount: int]"],
            "permissions": ["yessential.command.money.admin"],
        },
        "home": {
            "description": "家园系统",
            "usages": ["/home", "/home set <name: str>", "/home del <name: str>", "/home <name: str>"],
            "permissions": ["yessential.command.home"],
        },
        "warp": {
            "description": "传送点系统",
            "usages": ["/warp", "/warp set <name: str>", "/warp del <name: str>", "/warp <name: str>"],
            "permissions": ["yessential.command.warp"],
        },
        "rtp": {
            "description": "随机传送",
            "usages": ["/rtp"],
            "permissions": ["yessential.command.rtp"],
        },
        "tpa": {
            "description": "传送请求",
            "usages": ["/tpa"],
            "permissions": ["yessential.command.tpa"],
        },
        "tpayes": {
            "description": "同意传送请求",
            "usages": ["/tpayes"],
            "permissions": ["yessential.command.tpa"],
        },
        "tpano": {
            "description": "拒绝传送请求",
            "usages": ["/tpano"],
            "permissions": ["yessential.command.tpa"],
        },
        "notice": {
            "description": "公告系统",
            "usages": ["/notice", "/notice add <content: str>", "/notice del <index: int>"],
            "permissions": ["yessential.command.notice"],
        },
        "back": {
            "description": "死亡回溯",
            "usages": ["/back"],
            "permissions": ["yessential.command.back"],
        },
        "pvp": {
            "description": "PVP设置",
            "usages": ["/pvp", "/pvp on", "/pvp off"],
            "permissions": ["yessential.command.pvp"],
        },
        "wh": {
            "description": "维护模式",
            "usages": ["/wh"],
            "permissions": ["yessential.command.wh"],
        },
        "servers": {
            "description": "跨服传送",
            "usages": ["/servers"],
            "permissions": ["yessential.command.servers"],
        },
        "hub": {
            "description": "回城菜单",
            "usages": ["/hub"],
            "permissions": ["yessential.command.hub"],
        },
        "sethub": {
            "description": "设置回城点",
            "usages": ["/sethub"],
            "permissions": ["yessential.command.sethub"],
        },
        "menu": {
            "description": "菜单系统",
            "usages": ["/menu"],
            "permissions": ["yessential.command.menu"],
        },
        "cd": {
            "description": "菜单设置",
            "usages": ["/cd", "/cd set"],
            "permissions": ["yessential.command.cd"],
        },
        "getclock": {
            "description": "获取钟表",
            "usages": ["/getclock"],
            "permissions": ["yessential.command.getclock"],
        },
        "fcam": {
            "description": "灵魂出窍",
            "usages": ["/fcam"],
            "permissions": ["yessential.command.fcam"],
        },
        "rp": {
            "description": "红包系统",
            "usages": ["/rp", "/rp send <amount> <count>", "/rp open", "/rp list", "/rp history"],
            "permissions": ["yessential.command.rp"],
        },
        "crash": {
            "description": "崩溃玩家客户端",
            "usages": ["/crash"],
            "permissions": ["yessential.command.crash"],
        },
        "clean": {
            "description": "实体清理系统",
            "usages": ["/clean", "/clean now", "/clean status", "/clean cancel", "/clean tps", "/clean toast"],
            "permissions": ["yessential.command.clean"],
        },
        "suicide": {
            "description": "自杀系统",
            "usages": ["/suicide"],
            "permissions": ["yessential.command.suicide"],
        },
        "sign": {
            "description": "每日签到",
            "usages": ["/sign"],
            "permissions": ["yessential.command.sign"],
        },
        "signset": {
            "description": "签到管理",
            "usages": ["/signset"],
            "permissions": ["yessential.command.signset"],
        },
    }

    permissions = {
        "yessential.command.yest": {"description": "允许使用 YEssential 主命令", "default": True},
        "yessential.command.yest.admin": {"description": "允许重载 YEssential 配置", "default": "op"},
        "yessential.command.money": {"description": "允许使用经济系统命令", "default": True},
        "yessential.command.money.admin": {"description": "允许管理经济系统", "default": "op"},
        "yessential.command.home": {"description": "允许使用家园系统命令", "default": True},
        "yessential.command.warp": {"description": "允许使用传送点系统命令", "default": True},
        "yessential.command.warp.admin": {"description": "允许管理传送点", "default": "op"},
        "yessential.command.rtp": {"description": "允许使用随机传送命令", "default": True},
        "yessential.command.tpa": {"description": "允许使用传送请求命令", "default": True},
        "yessential.command.notice": {"description": "允许使用公告系统命令", "default": True},
        "yessential.command.notice.admin": {"description": "允许管理公告", "default": "op"},
        "yessential.command.back": {"description": "允许使用死亡回溯命令", "default": True},
        "yessential.command.pvp": {"description": "允许使用 PVP 设置命令", "default": True},
        "yessential.command.wh": {"description": "允许使用维护模式命令", "default": "op"},
        "yessential.command.servers": {"description": "允许使用跨服传送命令", "default": True},
        "yessential.command.hub": {"description": "允许使用回城命令", "default": True},
        "yessential.command.sethub": {"description": "允许设置回城点", "default": "op"},
        "yessential.command.menu": {"description": "允许使用菜单命令", "default": True},
        "yessential.command.cd": {"description": "允许使用菜单设置命令", "default": "op"},
        "yessential.command.getclock": {"description": "允许领取钟表", "default": True},
        "yessential.command.fcam": {"description": "允许使用灵魂出窍命令", "default": True},
        "yessential.command.rp": {"description": "允许使用红包命令", "default": True},
        "yessential.command.crash": {"description": "允许使用崩溃命令", "default": "op"},
        "yessential.command.clean": {"description": "允许使用清理命令", "default": True},
        "yessential.command.suicide": {"description": "允许使用自杀命令", "default": True},
        "yessential.command.sign": {"description": "允许使用签到命令", "default": True},
        "yessential.command.signset": {"description": "允许管理签到系统", "default": "op"},
    }

    def on_load(self):
        """插件加载时调用"""
        from .randomcolor import RandomColor
        
        print(RandomColor("██╗   ██╗███████╗███████╗███████╗███████╗███╗   ██╗████████╗██╗ █████╗ ██╗     "))
        print(RandomColor("╚██╗ ██╔╝██╔════╝██╔════╝██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║██╔══██╗██║     "))
        print(RandomColor(" ╚████╔╝ █████╗  ███████╗███████╗█████╗  ██╔██╗ ██║   ██║   ██║███████║██║     "))
        print(RandomColor("  ╚██╔╝  ██╔══╝  ╚════██║╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██╔══██║██║     "))
        print(RandomColor("   ██║   ███████╗███████║███████║███████╗██║ ╚████║   ██║   ██║██║  ██║███████╗"))
        print(RandomColor("   ╚═╝   ╚══════╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═╝╚══════╝"))
        print("                                                                               ")
        print(RandomColor(f"  {plugin_author[0]}  {plugin_version}"))

        plugin_print("=" * 80, "INFO")
        plugin_print(f"{plugin_name} - {plugin_description}", "INFO")
        plugin_print("感谢您使用Easy系列插件！", "INFO")
        plugin_print(f"本插件使用 {plugin_license} 许可证协议进行发布", "INFO")
        plugin_print(f"GitHub 仓库：{plugin_github_link}", "INFO")
        plugin_print(f"插件MineBBS资源帖：{plugin_minebbs_link}", "INFO")
        plugin_print(f"Easy系列插件交流群：1083195477", "INFO")
        plugin_print(f"作者：{plugin_author[0]} | 版本：{plugin_version}", "INFO")
        plugin_print("=" * 80, "INFO")

    def on_enable(self):
        plugin_print(f"{plugin_name} 已启用！")

        # 1. 初始化配置
        self.config_manager = ConfigManager(self)
        self.config_manager.load_config()

        # 2. 初始化子系统
        self.economy = EconomySystem(self)
        self.home = HomeSystem(self)
        self.warp = WarpSystem(self)
        self.rtp = RTPSystem(self)
        self.tpa = TPASystem(self)
        self.notice = NoticeSystem(self)
        self.back = BackSystem(self)
        self.pvp = PVPSystem(self)
        self.maintenance = MaintenanceSystem(self)
        self.servers = ServersSystem(self)
        self.hub = HubSystem(self)
        self.motd = MotdSystem(self)
        self.register_events(self.motd)  # 将 motd 注册为独立 listener
        self.cd = CdSystem(self)
        self.fcam = FcamSystem(self)
        self.redpacket = RedpacketSystem(self)
        self.crash = CrashSystem(self)
        self.cleanmgr = CleanmgrSystem(self)
        self.suicide = SuicideSystem(self)
        self.sign_system = SignSystem(self)

        # 3. 初始化 I18n
        self.i18n = init_i18n(self)

        # 4. 初始化更新检查器
        self.update_checker = UpdateChecker(self)

        # 5. 子系统额外初始化
        self.rtp.start_cooltime_task()

        # 6. 生命周期逻辑
        # KeepInventory（静默执行，不输出到控制台）
        if self.config_manager.config_data.get("KeepInventory", True):
            try:
                silent = CommandSenderWrapper(self.server.command_sender)
                self.server.dispatch_command(silent, "gamerule KeepInventory true")
            except Exception as e:
                self.logger.warning(f"KeepInventory 设置失败: {e}")

        # 7. MOTD 轮播启动(维护模式除外)
        if not self.maintenance.is_active:
            self.motd.start_rotation()

        # 8. 更新检查 (延迟)
        def start_update_check():
            self.update_checker.start_periodic()
        self.server.scheduler.run_task(self, start_update_check, 60)  # 3秒后

        # 9. 维护模式
        if self.maintenance.is_active:
            self.maintenance.enable()

    def on_disable(self):
        plugin_print(f"{plugin_name} 正在禁用...")
        self.motd.stop_rotation()
        plugin_print(f"{plugin_name} 已禁用!")

    # ══════════════════════════════════════════════════════════
    # Event Handlers
    # ══════════════════════════════════════════════════════════

    @event_handler
    def on_player_quit(self, event):
        player = event.player
        if _is_simulated(player):
            return
        # Fcam 清理
        if hasattr(self, 'fcam') and self.fcam:
            self.fcam.on_player_quit(player)
        # 排行榜缓存保存
        if hasattr(self, 'economy') and self.economy:
            try:
                self.economy.ranking.update(player.name, self.economy.get_money_internal(player))
            except:
                pass

    @event_handler
    def on_player_join(self, event: PlayerJoinEvent):
        player = event.player
        if _is_simulated(player):
            return

        player.send_message(f"§6[YEssential] §a欢迎回到服务器, {player.name}!")

        # Fcam 地址映射
        if hasattr(self, 'fcam') and self.fcam:
            self.fcam.on_player_join(player)

        # 初始化经济数据
        if hasattr(self, 'economy') and self.economy:
            self.economy.on_player_join(player)

        # 初始化 PVP 默认值
        if hasattr(self, 'pvp') and self.pvp:
            self.pvp.init_player_default(player)

        # 显示公告
        self.notice.show_notice(player)

        # 签到弹窗 (延迟)
        if hasattr(self, 'sign_system') and self.sign_system:
            self.sign_system.on_player_join(player)

    @event_handler
    def on_player_death(self, event: PlayerDeathEvent):
        player = event.player
        if _is_simulated(player):
            return
        # 记录死亡点
        self.back.record_death(player)
        # Fcam 死亡自动退出
        if hasattr(self, 'fcam') and self.fcam:
            self.fcam.on_death(player)

    @event_handler
    def on_player_respawn(self, event: PlayerRespawnEvent):
        player = event.player
        if _is_simulated(player):
            return
        # 复活时显示 Back GUI
        if self.config_manager.config_data.get("BackTipAfterDeath", True):
            def show_back():
                p = self.server.get_player(player.name)
                if p:
                    self.back.open_back_gui(p)
            self.server.scheduler.run_task(self, show_back, 40)  # 2秒后

    @event_handler
    def on_packet_receive(self, event: PacketReceiveEvent):
        """Fcam 拦截移动包"""
        if hasattr(self, 'fcam') and self.fcam:
            self.fcam.on_packet_receive(event)

    @event_handler
    def on_actor_damage(self, event: ActorDamageEvent):
        """PVP 伤害拦截 + Fcam 受伤退出"""
        if hasattr(self, 'pvp') and self.pvp:
            self.pvp.on_actor_damage(event)
        # Fcam 受伤自动退出
        if hasattr(self, 'fcam') and self.fcam:
            victim = event.actor
            from endstone import Player as P
            if isinstance(victim, P):
                self.fcam.on_damage(victim)

    @event_handler
    def on_server_command(self, event: ServerCommandEvent):
        """监听控制台命令: stop 时先踢出所有玩家"""
        cmd = event.command.lower().strip().lstrip("/")
        if cmd == "stop" and self.config_manager.config_data.get("CustomStopMessage", True):
            msg = self.config_manager.config_data.get("wh", {}).get(
                "whgamemsg", "服务器正在维护中，请您稍后再来!"
            )
            for player in self.server.online_players:
                if not _is_simulated(player):
                    try:
                        player.kick(msg)
                    except:
                        pass

    # ══════════════════════════════════════════════════════════
    # Command Dispatch
    # ══════════════════════════════════════════════════════════

    def on_command(self, sender: CommandSender, command: Command, args: List[str]) -> bool:
        cmd = command.name

        # ── yest ──────────────────────────────────────────
        if cmd == "yest" or cmd == "yessential":
            if len(args) > 0 and args[0] == "reload":
                if not sender.has_permission("yessential.command.yest.admin"):
                    sender.send_message("§c你没有权限重载配置。")
                    return True
                self.config_manager.load_config()
                self.fcam.load_config()
                sender.send_message("§6[YEssential] §a配置已重载！")
                return True
            else:
                sender.send_message(f"§6[YEssential] §7Version {plugin_version} (Python Refactored)")
                return True

        # ── moneygui ──────────────────────────────────────
        if cmd == "moneygui":
            if not isinstance(sender, Player):
                sender.send_message("§c该命令只能由玩家执行。")
                return True
            self.economy.open_money_gui(sender)
            return True

        # ── moneys (admin) ────────────────────────────────
        if cmd == "moneys":
            if not sender.has_permission("yessential.command.money.admin"):
                sender.send_message("§c你没有权限使用此命令。")
                return True
            return self.economy.handle_moneys_command(sender, args)

        # ── 玩家专用命令 ──────────────────────────────────
        if not isinstance(sender, Player):
            sender.send_message("§c该命令只能由玩家执行。")
            return True

        # ── money ─────────────────────────────────────────
        if cmd == "money":
            if len(args) == 0:
                self.economy.open_money_gui(sender)
            elif len(args) == 1:
                target = self.server.get_player(args[0])
                if target:
                    balance = self.economy.get_money_internal(target)
                    sender.send_message(f"§6[YEssential] §a玩家 {target.name} 的余额为: §e{int(balance)} §7金币")
                else:
                    balance = self.economy.get_money(args[0])
                    sender.send_message(f"§6[YEssential] §a玩家 {args[0]}(离线) 的余额为: §e{int(balance)} §7金币")
            elif len(args) == 3 and args[0] in ["give", "take", "set"]:
                if not sender.has_permission("yessential.command.money.admin"):
                    sender.send_message("§c你没有权限管理经济。")
                    return True
                action = args[0]
                target_name = args[1]
                try:
                    amount = float(args[2])
                    if action == "give":
                        self.economy.add_money(target_name, amount)
                        sender.send_message(f"§6[YEssential] §a已给 {target_name} 增加 {amount} 金币。")
                    elif action == "take":
                        if self.economy.reduce_money(target_name, amount):
                            sender.send_message(f"§6[YEssential] §a已从 {target_name} 扣除 {amount} 金币。")
                        else:
                            sender.send_message(f"§c{target_name} 余额不足。")
                    elif action == "set":
                        self.economy.set_money(target_name, amount)
                        sender.send_message(f"§6[YEssential] §a已设置 {target_name} 的余额为 {amount} 金币。")
                except ValueError:
                    sender.send_message("§c金额必须是数字。")
            else:
                sender.send_message("§c用法: /money [player] | /money give/take/set <player> <amount>")
            return True

        # ── home ───────────────────────────────────────────
        elif cmd == "home":
            if len(args) == 0:
                self.home.open_home_gui(sender)
            elif len(args) == 2 and args[0] == "set":
                self.home.set_home(sender, args[1])
            elif len(args) == 2 and args[0] == "del":
                self.home.del_home(sender, args[1])
            elif len(args) == 1:
                self.home.teleport_home(sender, args[0])
            else:
                sender.send_message("§c用法: /home [name] | /home set <name> | /home del <name>")
            return True

        # ── warp ───────────────────────────────────────────
        elif cmd == "warp":
            if len(args) == 0:
                self.warp.open_warp_gui(sender)
            elif len(args) == 2 and args[0] == "set" and sender.has_permission("yessential.command.warp.admin"):
                self.warp.set_warp(sender, args[1])
            elif len(args) == 2 and args[0] == "del" and sender.has_permission("yessential.command.warp.admin"):
                self.warp.del_warp(sender, args[1])
            elif len(args) == 1:
                self.warp.teleport_warp(sender, args[0])
            else:
                sender.send_message("§c用法: /warp [name] | /warp set <name> | /warp del <name>")
            return True

        # ── rtp ────────────────────────────────────────────
        elif cmd == "rtp":
            self.rtp.perform_rtp(sender)
            return True

        # ── tpa ────────────────────────────────────────────
        elif cmd == "tpa":
            if len(args) == 1:
                target = self.server.get_player(args[0])
                if target:
                    self.tpa.send_tpa_request(sender, target, "to")
                else:
                    sender.send_message(f"§c玩家 {args[0]} 不在线。")
            else:
                sender.send_message("§c用法: /tpa <player>")
            return True

        elif cmd == "tpayes":
            sender_name = sender.name
            request = self.tpa.pending_requests.get(sender_name)
            if not request:
                sender.send_message("§6[YEssential] §c没有待处理的传送请求。")
                return True
            self.tpa.handle_tpa_response(sender, sender_name, True)
            return True

        elif cmd == "tpano":
            sender_name = sender.name
            request = self.tpa.pending_requests.get(sender_name)
            if not request:
                sender.send_message("§6[YEssential] §c没有待处理的传送请求。")
                return True
            self.tpa.handle_tpa_response(sender, sender_name, False)
            return True

        # ── notice ─────────────────────────────────────────
        elif cmd == "notice":
            if len(args) == 0:
                self.notice.show_notice(sender)
            elif len(args) >= 2 and args[0] == "add" and sender.has_permission("yessential.command.notice.admin"):
                content = " ".join(args[1:])
                self.notice.add_notice(sender, content)
            elif len(args) == 2 and args[0] == "del" and sender.has_permission("yessential.command.notice.admin"):
                try:
                    index = int(args[1]) - 1
                    if 0 <= index < len(self.notice.notices):
                        del self.notice.notices[index]
                        self.notice.save_notices()
                        sender.send_message(f"§6[YEssential] §a公告 {index+1} 已删除。")
                    else:
                        sender.send_message("§c无效的公告索引。")
                except ValueError:
                    sender.send_message("§c公告索引必须是数字。")
            else:
                sender.send_message("§c用法: /notice | /notice add <content> | /notice del <index>")
            return True

        # ── back ───────────────────────────────────────────
        elif cmd == "back":
            self.back.open_back_gui(sender)
            return True

        # ── pvp ────────────────────────────────────────────
        elif cmd == "pvp":
            if len(args) == 0:
                self.pvp.open_pvp_gui(sender)
            elif len(args) == 1 and args[0] == "on":
                self.pvp.set_pvp(sender, True)
            elif len(args) == 1 and args[0] == "off":
                self.pvp.set_pvp(sender, False)
            else:
                sender.send_message("§c用法: /pvp | /pvp on | /pvp off")
            return True

        # ── wh (maintenance) ───────────────────────────────
        elif cmd == "wh":
            if not sender.has_permission("yessential.command.wh"):
                sender.send_message("§c你没有权限使用此命令。")
                return True
            wh_config = self.maintenance.config
            if not wh_config.get("EnableModule", True):
                sender.send_message("§6[YEssential] §c该模块未启用。")
                return True
            new_state = self.maintenance.toggle()
            if new_state:
                sender.send_message("§6[YEssential] §c维护模式已开启。")
                self.motd.pause()
                self.maintenance.enable()
            else:
                sender.send_message("§6[YEssential] §a维护模式已关闭。")
                self.motd.resume()
            return True

        # ── servers ────────────────────────────────────────
        elif cmd == "servers":
            self.servers.open_server_list(sender)
            return True

        # ── hub ────────────────────────────────────────────
        elif cmd == "hub":
            self.hub.open_hub_gui(sender)
            return True

        elif cmd == "sethub":
            self.hub.set_hub(sender)
            return True

        # ── menu / cd ──────────────────────────────────────
        elif cmd == "menu":
            self.cd.open_menu(sender)
            return True

        elif cmd == "cd":
            if len(args) > 0 and args[0] == "set":
                self.cd.open_settings(sender)
            else:
                self.cd.open_menu(sender)
            return True

        elif cmd == "getclock":
            self.cd.getclock(sender)
            return True

        # ── fcam ───────────────────────────────────────────
        elif cmd == "fcam":
            self.fcam.toggle_fcam(sender)
            return True

        # ── rp (redpacket) ─────────────────────────────────
        elif cmd == "rp":
            self.redpacket.on_command(sender, args)
            return True

        # ── crash ──────────────────────────────────────────
        elif cmd == "crash":
            if sender.has_permission("yessential.command.crash"):
                self.crash.on_command(sender)
            else:
                sender.send_message("§6[YEssential] §c你没有权限使用此命令。")
            return True

        # ── clean ──────────────────────────────────────────
        elif cmd == "clean":
            self.cleanmgr.handle_command(sender, args[0] if args else "")
            return True

        # ── suicide ────────────────────────────────────────
        elif cmd == "suicide":
            self.suicide.handle_command(sender)
            return True

        # ── sign (签到) ────────────────────────────────────
        elif cmd == "sign":
            if hasattr(self, 'sign_system') and self.sign_system:
                self.sign_system.open_sign_form(sender)
            return True

        # ── signset (签到管理) ──────────────────────────────
        elif cmd == "signset":
            if not sender.has_permission("yessential.command.signset"):
                sender.send_message("§c你没有权限管理签到系统。")
                return True
            if hasattr(self, 'sign_system') and self.sign_system:
                self.sign_system.open_settings(sender)
            return True

        return False

    # ══════════════════════════════════════════════════════════
    # Helpers
    # ══════════════════════════════════════════════════════════

    pass
