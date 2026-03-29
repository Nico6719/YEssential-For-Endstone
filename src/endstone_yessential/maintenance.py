from typing import Optional

class MaintenanceSystem:
    def __init__(self, plugin):
        self.plugin = plugin
    
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
    
    def enable(self):
        for player in self.plugin.server.online_players:
            if not player.is_op and not player.is_simulated_player():
                player.kick(self.config.get("whgamemsg", "服务器正在维护中，请您稍后再来!"))
    
    def disable(self):
        pass
    
    def on_player_pre_join(self, player) -> bool:
        if player.is_simulated_player():
            return True
        if not self.config.get("EnableModule", True):
            return True
        if player.is_op:
            return True
        if self.is_active:
            player.kick(self.config.get("whgamemsg", "服务器正在维护中，请您稍后再来!"))
            return False
        return True
