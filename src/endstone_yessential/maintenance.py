from typing import Optional
from endstone import Player
from endstone.command import CommandSender
import asyncio

class MaintenanceSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self._motd_task: Optional[asyncio.Task] = None
        self._original_motd: Optional[str] = None
    
    @property
    def config(self):
        return self.plugin.config_manager.get("wh", {
            "EnableModule": True,
            "status": 0,
            "whmotdmsg": "服务器维护中，请勿进入！",
            "whgamemsg": "服务器正在维护中，请您稍后再来!"
        })
    
    @property
    def is_active(self) -> bool:
        return self.config.get("status", 0) == 1
    
    def set_status(self, status: bool) -> bool:
        wh_config = self.config.copy()
        wh_config["status"] = 1 if status else 0
        self.plugin.config_manager.set("wh", wh_config)
        return status
    
    def toggle(self) -> bool:
        new_state = not self.is_active
        self.set_status(new_state)
        return new_state
    
    async def enable(self):
        if self._motd_task:
            self._motd_task.cancel()
            self._motd_task = None
        
        wh_config = self.config
        self.plugin.server.set_motd(wh_config.get("whmotdmsg", "服务器维护中，请勿进入！"))
        
        for player in self.plugin.server.online_players:
            if not player.is_op and not player.is_simulated_player():
                player.kick(wh_config.get("whgamemsg", "服务器正在维护中，请您稍后再来!"))
    
    async def disable(self):
        self.plugin.motd.start_rotation()
    
    def on_player_pre_join(self, player: Player) -> bool:
        if player.is_simulated_player():
            return True
        if not self.config.get("EnableModule", True):
            return True
        if player.is_op:
            return True
        if self.is_active:
            wh_config = self.config
            player.kick(wh_config.get("whgamemsg", "服务器正在维护中，请您稍后再来!"))
            return False
        return True
