from endstone import Player
from endstone.level import Location
from .i18n import tr
from endstone.form import ActionForm

class HubSystem:
    def __init__(self, plugin):
        self.plugin = plugin
    
    @property
    def config(self):
        return self.plugin.config_manager.get("Hub", {
            "EnabledModule": True,
            "x": 0,
            "y": 0,
            "z": 0,
            "dimid": 0
        })
    
    def is_enabled(self) -> bool:
        return self.config.get("EnabledModule", True)
    
    def get_hub_location(self):
        hub_config = self.config
        level = self.plugin.server.level
        if level is None:
            return None

        dimid = hub_config.get("dimid", 0)
        dimension = self._get_dimension(level, dimid)
        if dimension is None:
            return None

        return Location(
            dimension,
            hub_config.get("x", 0),
            hub_config.get("y", -60),
            hub_config.get("z", 0)
        )
    
    def open_hub_gui(self, player: Player):
        if not self.is_enabled():
            player.send_message(tr("hub.disabled"))
            return
        
        hub_config = self.config
        x = hub_config.get("x", 0)
        y = hub_config.get("y", -60)
        z = hub_config.get("z", 0)
        dimid = hub_config.get("dimid", 0)
        dim_name = self._get_dimension_name(dimid)
        
        form = ActionForm(title=tr("hub.title"))
        form.content = f"§e目标位置：\n§bX: §f{x}\n§bY: §f{y}\n§bZ: §f{z}\n§b维度: §f{dim_name}"
        
        form.add_button(tr("hub.teleport_now"))
        form.add_button(tr("hub.cancel"))
        
        def on_submit(selected_player, selected_id):
            if selected_id == 0:
                self.teleport_to_hub(selected_player)
        
        form.on_submit = on_submit
        player.send_form(form)
    
    def teleport_to_hub(self, player: Player):
        location = self.get_hub_location()
        if location is None:
            player.send_message(tr("hub.no_location"))
            return
        
        player.teleport(location)
        player.send_message(tr("hub.teleported"))
    
    def set_hub(self, player: Player):
        if not player.is_op:
            player.send_message(tr("hub.no_perm"))
            return
        
        hub_data = {
            "EnabledModule": True,
            "x": round(player.location.x, 1),
            "y": round(player.location.y, 1),
            "z": round(player.location.z, 1),
            "dimid": self._get_dimension_id(player.location.dimension)
        }
        self.plugin.config_manager.set("Hub", hub_data)
        player.send_message(tr("hub.set"))
        player.send_message(f"§bX: §f{round(player.location.x, 1)}")
        player.send_message(f"§bY: §f{round(player.location.y, 1)}")
        player.send_message(f"§bZ: §f{round(player.location.z, 1)}")
        player.send_message(f"§b维度: §f{self._get_dimension_name(hub_data['dimid'])}")
    
    def _get_dimension(self, level, dimid: int):
        """根据 dimid 获取 Dimension 对象"""
        names = {0: "Overworld", 1: "Nether", 2: "The End"}
        dim_name = names.get(dimid, "Overworld")
        try:
            return level.get_dimension(dim_name)
        except Exception:
            self.plugin.logger.warning(f"Hub: dimension lookup failed for dimid={dimid}, falling back to first dimension")
            dims = level.dimensions
            return dims[0] if dims else None

    def _get_dimension_name(self, dimid: int) -> str:
        names = {0: tr("hub.dim_overworld"), 1: tr("hub.dim_nether"), 2: tr("hub.dim_end")}
        return names.get(dimid, tr("hub.dim_unknown"))

    def _get_dimension_id(self, dim) -> int:
        """从 Dimension 对象获取 dimid"""
        dim_name = getattr(dim, 'name', '')
        name_map = {"Overworld": 0, "Nether": 1, "The End": 2}
        return name_map.get(dim_name, 0)
