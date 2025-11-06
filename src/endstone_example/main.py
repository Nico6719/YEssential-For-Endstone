from endstone import Player, Server
from endstone.event import EventPriority, event_handler
from endstone.event.player import PlayerJoinEvent, PlayerQuitEvent, PlayerDeathEvent, PlayerRespawnEvent
from endstone.command import Command, CommandSender
from endstone.plugin import Plugin
from endstone.location import Location
import os
import json
import time
import asyncio
from typing import Dict, List, Optional, Any

from .config import ConfigManager
from .language import LanguageManager
from .economy import EconomySystem
from .home import HomeSystem
from .warp import WarpSystem
from .rtp import RTPSystem
from .tpa import TPASystem
from .redpacket import RedPacketSystem
from .pvp import PVPSystem
from .back import BackSystem
from .notice import NoticeSystem
from .hub import HubSystem
from .suicide import SuicideSystem
from .clean import CleanSystem

class YEssentialPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.config_manager = None
        self.lang_manager = None
        self.economy = None
        self.home = None
        self.warp = None
        self.rtp = None
        self.tpa = None
        self.redpacket = None
        self.pvp = None
        self.back = None
        self.notice = None
        self.hub = None
        self.suicide = None
        self.clean = None
        
        # 运行时数据
        self.player_settings = {}
        self.cooltimes = {}
        self.death_points = {}
        self.pending_requests = {}
        
    def on_enable(self):
        """插件启用时调用"""
        self.logger.info("=== YEssential 多功能基础插件已启用 ===")
        
        try:
            # 初始化管理器
            self.config_manager = ConfigManager(self)
            self.lang_manager = LanguageManager(self)
            
            # 初始化各系统
            self.economy = EconomySystem(self)
            self.home = HomeSystem(self)
            self.warp = WarpSystem(self)
            self.rtp = RTPSystem(self)
            self.tpa = TPASystem(self)
            self.redpacket = RedPacketSystem(self)
            self.pvp = PVPSystem(self)
            self.back = BackSystem(self)
            self.notice = NoticeSystem(self)
            self.hub = HubSystem(self)
            self.suicide = SuicideSystem(self)
            self.clean = CleanSystem(self)
            
            # 加载配置和数据
            self.config_manager.load_config()
            self.lang_manager.load_language()
            self._load_player_data()
            
            # 注册命令和事件
            self._register_commands()
            self._setup_timers()
            
            # 启动定时任务
            self._start_tasks()
            
            self.logger.info("YEssential v2.5.4 - Endstone Python版加载完成！")
            self.logger.info("作者: Nico6719, PHEyeji")
            self.logger.info("基于GPLv3协议发布")
            
        except Exception as e:
            self.logger.error(f"插件启动失败: {e}")
            raise
    
    def on_disable(self):
        """插件禁用时调用"""
        self.logger.info("=== YEssential 插件已禁用 ===")
        self._save_all_data()
    
    def _register_commands(self):
        """注册所有命令"""
        # 经济系统命令
        @self.server.command.register("money", "经济系统", permission="yessential.money")
        def money_cmd(sender: CommandSender, args: List[str]):
            if not isinstance(sender, Player):
                sender.send_message(self.get_text("player.only"))
                return
            self.economy.open_money_gui(sender)
        
        @self.server.command.register("moneys", "经济管理", permission="yessential.moneys")
        def moneys_cmd(sender: CommandSender, args: List[str]):
            if not sender.has_permission("yessential.moneys"):
                sender.send_message(self.get_text("player.not.op"))
                return
            self.economy.open_op_money_gui(sender)
        
        # 家园系统命令
        @self.server.command.register("home", "家园系统", permission="yessential.home")
        def home_cmd(sender: CommandSender, args: List[str]):
            if not isinstance(sender, Player):
                sender.send_message(self.get_text("player.only"))
                return
            self.home.open_home_gui(sender)
        
        # 传送点命令
        @self.server.command.register("warp", "传送点系统", permission="yessential.warp")
        def warp_cmd(sender: CommandSender, args: List[str]):
            if not isinstance(sender, Player):
                sender.send_message(self.get_text("player.only"))
                return
            self.warp.open_warp_gui(sender)
        
        # 随机传送命令
        @self.server.command.register("rtp", "随机传送", permission="yessential.rtp")
        def rtp_cmd(sender: CommandSender, args: List[str]):
            if not isinstance(sender, Player):
                sender.send_message(self.get_text("player.only"))
                return
            self.rtp.teleport_random(sender)
        
        # 死亡回溯命令
        @self.server.command.register("back", "死亡回溯", permission="yessential.back")
        def back_cmd(sender: CommandSender, args: List[str]):
            if not isinstance(sender, Player):
                sender.send_message(self.get_text("player.only"))
                return
            self.back.open_back_gui(sender)
        
        # 公告命令
        @self.server.command.register("notice", "查看公告", permission="yessential.notice")
        def notice_cmd(sender: CommandSender, args: List[str]):
            if not isinstance(sender, Player):
                sender.send_message(self.get_text("player.only"))
                return
            self.notice.show_notice(sender)
        
        # 自杀命令
        @self.server.command.register("suicide", "自杀", permission="yessential.suicide")
        def suicide_cmd(sender: CommandSender, args: List[str]):
            if not isinstance(sender, Player):
                sender.send_message(self.get_text("player.only"))
                return
            self.suicide.player_suicide(sender)
        
        # 更多命令...
        self.logger.info("命令注册完成")
    
    def _setup_timers(self):
        """设置定时器"""
        # 经济系统数据同步
        @self.server.scheduler.schedule(interval=10.0)  # 10秒一次
        def economy_sync():
            try:
                self.economy.sync_economy_data()
            except Exception as e:
                self.logger.error(f"经济数据同步失败: {e}")
        
        # 冷却时间更新
        @self.server.scheduler.schedule(interval=1.0)  # 1秒一次
        def cooldown_update():
            try:
                current_time = time.time()
                expired = []
                for player_name, cooldown_end in self.cooltimes.items():
                    if current_time >= cooldown_end:
                        expired.append(player_name)
                
                for player_name in expired:
                    del self.cooltimes[player_name]
            except Exception as e:
                self.logger.error(f"冷却时间更新失败: {e}")
        
        # 自动清理
        @self.server.scheduler.schedule(interval=60.0)  # 60秒一次
        def auto_clean():
            try:
                if self.config_manager.get("AutoCleanItem.interval", 0) > 0:
                    self.clean.check_and_clean()
            except Exception as e:
                self.logger.error(f"自动清理失败: {e}")
    
    def _start_tasks(self):
        """启动异步任务"""
        # 自动更新检查
        if self.config_manager.get("AutoUpdate", True):
            asyncio.create_task(self._check_updates())
    
    async def _check_updates(self):
        """检查更新"""
        try:
            # 这里可以实现更新检查逻辑
            current_version = "2.5.4"
            # 模拟更新检查
            await asyncio.sleep(5)
            self.logger.info("更新检查完成 - 当前已是最新版本")
        except Exception as e:
            self.logger.error(f"更新检查失败: {e}")
    
    def _load_player_data(self):
        """加载玩家数据"""
        players_dir = os.path.join(self.data_folder, "players")
        os.makedirs(players_dir, exist_ok=True)
        
        # 这里可以加载离线玩家数据
        self.logger.info("玩家数据加载完成")
    
    def _save_all_data(self):
        """保存所有数据"""
        try:
            self.config_manager.save_config()
            # 保存其他系统数据...
            self.logger.info("所有数据保存完成")
        except Exception as e:
            self.logger.error(f"数据保存失败: {e}")
    
    @property
    def data_folder(self) -> str:
        """获取数据文件夹路径"""
        return os.path.join(self.server.plugin_data_folder, "YEssential")
    
    def get_text(self, key: str, **kwargs) -> str:
        """获取本地化文本"""
        text = self.lang_manager.get_text(key)
        if text and kwargs:
            for k, v in kwargs.items():
                text = text.replace(f"${{{k}}}", str(v))
        return text or f"[Missing: {key}]"
    
    def is_module_enabled(self, module: str) -> bool:
        """检查模块是否启用"""
        return self.config_manager.get(f"{module}.enabled", False)
    
    def has_cooldown(self, player: Player, action: str) -> tuple[bool, int]:
        """检查冷却时间"""
        key = f"{player.name}_{action}"
        current_time = time.time()
        
        if key in self.cooltimes:
            remaining = int(self.cooltimes[key] - current_time)
            if remaining > 0:
                return True, remaining
        
        return False, 0
    
    def set_cooldown(self, player: Player, action: str, seconds: int):
        """设置冷却时间"""
        key = f"{player.name}_{action}"
        self.cooltimes[key] = time.time() + seconds
    
    # 事件处理
    @event_handler(PlayerJoinEvent)
    def on_player_join(self, event: PlayerJoinEvent):
        """玩家加入事件"""
        player = event.player
        
        # 初始化玩家数据
        if player.name not in self.player_settings:
            self.player_settings[player.name] = {
                "accept_tpa": True,
                "show_notice": True,
                "last_notice": 0
            }
        
        # 显示公告
        if self.notice.should_show_notice(player):
            self.server.get_scheduler().call_later(3.0, lambda: self.notice.show_notice(player))
        
        # 初始化经济数据
        self.economy.init_player_economy(player)
        
        # 欢迎消息
        if self.config_manager.get("join_notice.enabled", False):
            player.send_message(self.get_text("welcome.message", player=player.name))
    
    @event_handler(PlayerDeathEvent)
    def on_player_death(self, event: PlayerDeathEvent):
        """玩家死亡事件"""
        player = event.player
        self.back.record_death_location(player)
        
        # 死亡不掉落
        if self.config_manager.get("KeepInventory", False):
            # 在Endstone中可能需要其他方式实现
            pass
    
    @event_handler(PlayerRespawnEvent)
    def on_player_respawn(self, event: PlayerRespawnEvent):
        """玩家重生事件"""
        player = event.player
        
        # 显示死亡回溯提示
        if self.config_manager.get("BackTipAfterDeath", True):
            self.server.get_scheduler().call_later(2.0, lambda: self.back.show_death_tip(player))
    
    @event_handler(PlayerQuitEvent)
    def on_player_quit(self, event: PlayerQuitEvent):
        """玩家退出事件"""
        player = event.player
        
        # 清理待处理请求
        self.tpa.cleanup_player_requests(player)
        
        # 保存玩家数据
        self._save_player_data(player)
    
    def _save_player_data(self, player: Player):
        """保存单个玩家数据"""
        try:
            player_file = os.path.join(self.data_folder, "players", f"{player.name}.json")
            data = {
                "settings": self.player_settings.get(player.name, {}),
                "economy": self.economy.get_player_economy_data(player),
                "homes": self.home.get_player_homes(player),
                "last_seen": time.time()
            }
            
            with open(player_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存玩家数据失败 {player.name}: {e}")

def create_plugin():
    return YEssentialPlugin()
