from endstone import Player

class SuicideSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.server = plugin.server
    
    def player_suicide(self, player: Player) -> bool:
        """玩家自杀"""
        if not self.plugin.is_module_enabled("Suicide"):
            player.send_message(self.plugin.get_text("module.no.enabled"))
            return False
        
        # 检查费用
        cost = self.plugin.config_manager.get("Suicide.cost", 0)
        if cost > 0 and not self.plugin.economy.reduce_balance(player, cost):
            player.send_message(self.plugin.get_text("economy.no.enough"))
            return False
        
        # 确认自杀
        from endstone import CustomForm
        form = CustomForm()
        form.title = self.plugin.get_text("suicide.gui.title")
        
        form.add_label(self.plugin.get_text("suicide.gui.warning"))
        form.add_label(self.plugin.get_text("suicide.gui.cost", cost=cost))
        form.add_label(self.plugin.get_text("economy.balance", balance=self.plugin.economy.get_balance(player)))
        
        def callback(p, data):
            if data is not None:
                try:
                    p.kill()
                    p.send_message(self.plugin.get_text("suicide.success"))
                except Exception as e:
                    self.plugin.logger.error(f"玩家自杀失败: {e}")
                    p.send_message(self.plugin.get_text("suicide.failed"))
        
        player.send_form(form, callback)
        return True
