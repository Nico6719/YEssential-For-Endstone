from endstone import Player, Location
from endstone.form import ActionForm

class HubSystem:
    def __init__(self, plugin):
        self.plugin = plugin
    
    @property
    def config(self):
        return self.plugin.config_manager.get("Hub", {
            "EnabledModule": True,
            "x": 0,
            "y": -60,
            "z": 0,
            "dimid": 0
        })
    
    def is_enabled(self) -> bool:
        return self.config.get("EnabledModule", True)
    
    def get_hub_location(self) -> Location:
        hub_config = self.config
        world = self.plugin.server.get_world("default")
        if world is None:
            world = self.plugin.server.worlds[0] if self.plugin.server.worlds else None
        
        if world is None:
            return None
        
        return Location(
            world,
            hub_config.get("x", 0),
            hub_config.get("y", -60),
            hub_config.get("z", 0)
        )
    
    def open_hub_gui(self, player: Player):
        if not self.is_enabled():
            player.send_message("§6[YEssential] §c该模块未启用。")
            return
        
        hub_config = self.config
        x = hub_config.get("x", 0)
        y = hub_config.get("y", -60)
        z = hub_config.get("z", 0)
        dimid = hub_config.get("dimid", 0)
        dim_name = self._get_dimension_name(dimid)
        
        form = ActionForm(title="§6回城菜单")
        form.content = f"§e目标位置：\n§bX: §f{x}\n§bY: §f{y}\n§bZ: §f{z}\n§b维度: §f{dim_name}"
        
        form.add_button("§a立即传送")
        form.add_button("§c取消")
        
        def on_submit(selected_player, selected_id):
            if selected_id == 0:
                self.teleport_to_hub(selected_player)
        
        form.on_submit = on_submit
        player.send_form(form)
    
    def teleport_to_hub(self, player: Player):
        location = self.get_hub_location()
        if location is None:
            player.send_message("§6[YEssential] §c无法获取传送位置。")
            return
        
        player.teleport(location)
        player.send_message("§6[YEssential] §a已传送至回城点。")
    
    def set_hub(self, player: Player):
        if not player.is_op:
            player.send_message("§6[YEssential] §c你没有权限设置回城点。")
            return
        
        hub_data = {
            "EnabledModule": True,
            "x": round(player.location.x, 1),
            "y": round(player.location.y, 1),
            "z": round(player.location.z, 1),
            "dimid": self._get_dimension_id(player.location.world)
        }
        self.plugin.config_manager.set("Hub", hub_data)
        player.send_message("§6[YEssential] §a回城点已设置为：")
        player.send_message(f"§bX: §f{round(player.location.x, 1)}")
        player.send_message(f"§bY: §f{round(player.location.y, 1)}")
        player.send_message(f"§bZ: §f{round(player.location.z, 1)}")
        player.send_message(f"§b维度: §f{self._get_dimension_name(hub_data['dimid'])}")
    
    def _get_dimension_name(self, dimid: int) -> str:
        names = {0: "主世界", 1: "下界", 2: "末地"}
        return names.get(dimid, "未知")
    
    def _get_dimension_id(self, world) -> int:
        return 0
