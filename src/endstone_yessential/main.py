from endstone.plugin import Plugin
from endstone.event import event_handler, PlayerJoinEvent, PlayerQuitEvent, PlayerDeathEvent, PlayerRespawnEvent, PlayerHurtEvent, PlayerSpawnEvent
from endstone.command import Command, CommandSender
from endstone import Player
from typing import List
import os
import asyncio

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
from .log import plugin_print
from .constant import *

class YEssentialPlugin(Plugin):
    api_version = "0.5"
    commands = {
        "yest": {
            "description": "YEssential 主命令",
            "usages": ["/yest", "/yest reload"],
            "permissions": ["yessential.command.yest"],
        },
        "money": {
            "description": "经济系统",
            "usages": ["/money", "/money give <player: target> <amount: int>", "/money take <player: target> <amount: int>", "/money set <player: target> <amount: int>"],
            "permissions": ["yessential.command.money"],
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
    }

    def on_enable(self):
        self.logger.info("§6YEssential (Python) §a已启用！")
        
        self.config_manager = ConfigManager(self)
        self.config_manager.load_config()
        
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
        
        self.rtp.start_cooltime_task()
        
        if self.maintenance.is_active:
            asyncio.create_task(self.maintenance.enable())
        else:
            self.motd.start_rotation()

    def on_disable(self):
        self.motd.stop_rotation()
        self.logger.info("§6YEssential (Python) §c已禁用！")

    @event_handler
    def on_player_join(self, event: PlayerJoinEvent):
        player = event.player
        player.send_message(f"§6[YEssential] §a欢迎回到服务器, {player.name}!")
        # 可以在这里显示公告
        self.notice.show_notice(player)

    @event_handler
    def on_player_death(self, event: PlayerDeathEvent):
        player = event.player
        # 记录死亡点
        self.back.record_death(player)

    def on_command(self, sender: CommandSender, command: Command, args: List[str]) -> bool:

        cmd = command.name
        if cmd == "yest":
            if len(args) > 0 and args[0] == "reload" and sender.has_permission("yessential.command.yest.admin"):
                # 重载配置
                self.config_manager.load_config()
                if not isinstance(sender, Player):
                    plugin_print("[YEssential] 配置已重载！")
                    return True
                else:
                    sender.send_message("§6[YEssential] §a配置已重载！")
                    return True
            else:
                if not isinstance(sender, Player):
                    plugin_print(f"[YEssential] Version {plugin_version} (Python Refactored)")
                    return True
                else:
                    sender.send_message(f"§6[YEssential] §7Version {plugin_version} (Python Refactored)")
                    return True
                return True
        
        if not isinstance(sender, Player):
            sender.send_message("§c该命令只能由玩家执行。")
            return True

        elif cmd == "money":
            if len(args) == 0:
                self.economy.open_money_gui(sender)
            elif len(args) == 1:
                # 查看其他玩家余额
                target_name = args[0]
                balance = self.economy.get_money(target_name)
                sender.send_message(f"§6[YEssential] §a玩家 {target_name} 的余额为: §e{balance} §a金币")
            elif len(args) == 3 and args[0] in ["give", "take", "set"] and sender.has_permission("yessential.command.money.admin"):
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
                            sender.send_message(f"§c{target_name} 余额不足，无法扣除 {amount} 金币。")
                    elif action == "set":
                        self.economy.set_money(target_name, amount)
                        sender.send_message(f"§6[YEssential] §a已设置 {target_name} 的余额为 {amount} 金币。")
                except ValueError:
                    sender.send_message("§c金额必须是数字。")
            else:
                sender.send_message("§c用法: /money [player] | /money give/take/set <player> <amount>")
            return True
            
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
            
        elif cmd == "rtp":
            self.rtp.teleport_random(sender)
            return True
            
        elif cmd == "tpa":
            if len(args) == 1:
                target_name = args[0]
                target = self.plugin.server.get_player(target_name)
                if target:
                    self.tpa.send_tpa_request(sender, target, "to")
                else:
                    sender.send_message(f"§c玩家 {target_name} 不在线。")
            else:
                sender.send_message("§c用法: /tpa <player>")
            return True
        
        elif cmd == "tpayes":
            # sender is the person who received the request and is accepting it
            # We need to find the request where this player is the target
            sender_name = sender.name
            # Find the request where sender_name is the original requester
            request = self.tpa.pending_requests.get(sender_name)
            if not request:
                sender.send_message("§6[YEssential] §c没有待处理的传送请求。")
                return True
            # Handle the response - target is sender (the one accepting), sender_name is the original requester
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
            
        elif cmd == "notice":
            if len(args) == 0:
                self.notice.show_notice(sender)
            elif len(args) >= 2 and args[0] == "add" and sender.has_permission("yessential.command.notice.admin"):
                content = " ".join(args[1:])
                self.notice.add_notice(sender, content)
            elif len(args) == 2 and args[0] == "del" and sender.has_permission("yessential.command.notice.admin"):
                try:
                    index = int(args[1]) - 1 # 转换为0索引
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
            
        elif cmd == "back":
            self.back.open_back_gui(sender)
            return True
            
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
                asyncio.create_task(self.maintenance.enable())
            else:
                sender.send_message("§6[YEssential] §a维护模式已关闭。")
                asyncio.create_task(self.maintenance.disable())
            return True
        
        elif cmd == "servers":
            self.servers.open_server_list(sender)
            return True
        
        elif cmd == "hub":
            self.hub.open_hub_gui(sender)
            return True
        
        elif cmd == "sethub":
            self.hub.set_hub(sender)
            return True

        return False
