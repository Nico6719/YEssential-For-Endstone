from endstone import Player, Location

class HubSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.server = plugin.server
    
    def set_hub_location(self, player: Player) -> bool:
        """设置中心传送点"""
        if not player.has_permission("yessential.hub.set"):
            player.send_message(self.plugin.get_text("player.not.op"))
            return False
        
        location = player.location
        hub_data = {
            "x": location.x,
            "y": location.y,
            "z": location.z,
            "dimension": location.dimension,
            "world": location.world.name if location.world else "overworld",
            "is_set": True
        }
        
        self.plugin.config_manager.set("Hub", hub_data)
        player.send_message(self.plugin.get_text("hub.set_success"))
        return True
    
    def teleport_to_hub(self, player: Player) -> bool:
        """传送到中心点"""
        if not self.plugin.is_module_enabled("Hub"):
            player.send_message(self.plugin.get_text("module.no.enabled"))
            return False
        
        hub_data = self.plugin.config_manager.get("Hub", {})
        if not hub_data.get("is_set", False):
            player.send_message(self.plugin.get_text("hub.not_set"))
            return False
        
        try:
            world = self.server.get_world(hub_data.get("world", "overworld"))
            location = Location(
                x=hub_data["x"],
                y=hub_data["y"],
                z=hub_data["z"],
                world=world,
                dimension=hub_data.get("dimension", 0)
            )
            
            player.teleport(location)
            player.send_message(self.plugin.get_text("hub.teleport_success"))
            return True
            
        except Exception as e:
            self.plugin.logger.error(f"传送到中心点失败: {e}")
            player.send_message(self.plugin.get_text("hub.teleport_failed"))
            return False
    
    def open_hub_gui(self, player: Player):
        """打开中心传送GUI"""
        hub_data = self.plugin.config_manager.get("Hub", {})
        
        from endstone import SimpleForm
        form = SimpleForm()
        form.title = self.plugin.get_text("hub.gui.title")
        
        if hub_data.get("is_set", False):
            form.content = self.plugin.get_text("hub.gui.location", 
                                               x=hub_data["x"], 
                                               y=hub_data["y"], 
                                               z=hub_data["z"])
            
            form.add_button(
                self.plugin.get_text("hub.gui.teleport"),
                callback=lambda p, data: self.teleport_to_hub(p)
            )
        else:
            form.content = self.plugin.get_text("hub.gui.not_set")
        
        if player.has_permission("yessential.hub.set"):
            form.add_button(
                self.plugin.get_text("hub.gui.set"),
                callback=lambda p, data: self.set_hub_location(p)
            )
        
        player.send_form(form)
