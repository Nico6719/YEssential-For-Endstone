from typing import Dict
from endstone import Player
from endstone.event import event_handler
from endstone.event.entity import EntityDamageEvent

class PVPSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.server = plugin.server
        self.pvp_states = {}  # 玩家PVP状态
    
    def set_pvp_state(self, player: Player, enabled: bool) -> bool:
        """设置玩家PVP状态"""
        if not self.plugin.is_module_enabled("PVP"):
            player.send_message(self.plugin.get_text("module.no.enabled"))
            return False
        
        self.pvp_states[player.name] = enabled
        
        if enabled:
            player.send_message(self.plugin.get_text("pvp.enabled"))
        else:
            player.send_message(self.plugin.get_text("pvp.disabled"))
        
        return True
    
    def get_pvp_state(self, player: Player) -> bool:
        """获取玩家PVP状态"""
        return self.pvp_states.get(player.name, self.plugin.config_manager.get("PVP.default_enabled", False))
    
    def toggle_pvp_state(self, player: Player) -> bool:
        """切换玩家PVP状态"""
        current = self.get_pvp_state(player)
        return self.set_pvp_state(player, not current)
    
    @event_handler(EntityDamageEvent)
    def on_entity_damage(self, event: EntityDamageEvent):
        """实体伤害事件处理"""
        if not self.plugin.is_module_enabled("PVP"):
            return
        
        # 检查是否是玩家之间的伤害
        if not event.damage_source or not event.damage_source.is_player():
            return
        
        if not event.entity or not event.entity.is_player():
            return
        
        attacker = event.damage_source.to_player()
        victim = event.entity.to_player()
        
        # 获取PVP状态
        attacker_pvp = self.get_pvp_state(attacker)
        victim_pvp = self.get_pvp_state(victim)
        
        # 如果攻击者关闭了PVP
        if not attacker_pvp:
            attacker.send_message(self.plugin.get_text("pvp.self.disabled"))
            event.cancelled = True
            return
        
        # 如果受害者关闭了PVP
        if not victim_pvp:
            attacker.send_message(self.plugin.get_text("pvp.other.disabled"))
            event.cancelled = True
            return
    
    def open_pvp_gui(self, player: Player):
        """打开PVP设置GUI"""
        from endstone import SimpleForm
        
        current_state = self.get_pvp_state(player)
        status_text = self.plugin.get_text("pvp.status_enabled") if current_state else self.plugin.get_text("pvp.status_disabled")
        
        form = SimpleForm()
        form.title = self.plugin.get_text("pvp.gui.title")
        form.content = self.plugin.get_text("pvp.gui.status", status=status_text)
        
        form.add_button(
            self.plugin.get_text("pvp.gui.toggle"),
            callback=lambda p, data: self.toggle_pvp_state(p)
        )
        
        form.add_button(
            self.plugin.get_text("pvp.gui.enable"),
            callback=lambda p, data: self.set_pvp_state(p, True)
        )
        
        form.add_button(
            self.plugin.get_text("pvp.gui.disable"),
            callback=lambda p, data: self.set_pvp_state(p, False)
        )
        
        player.send_form(form)
