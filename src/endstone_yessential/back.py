from typing import Dict
from endstone import Player
from endstone.level import Location
from endstone.form import ActionForm

class BackSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.death_points: Dict[str, Location] = {}

    def record_death(self, player: Player):
        """记录玩家死亡点"""
        self.death_points[player.name] = player.location
        player.send_message("§6[YEssential] §c死亡点已记录，输入 /back 返回。")

    def teleport_back(self, player: Player):
        """传送到死亡点"""
        if player.name in self.death_points:
            loc = self.death_points[player.name]
            player.teleport(loc)
            player.send_message("§6[YEssential] §a已返回死亡点。")
            # 传送后清除记录，防止重复传送
            del self.death_points[player.name]
        else:
            player.send_message("§c没有记录的死亡点。")

    def open_back_gui(self, player: Player):
        """打开返回死亡点 GUI"""
        form = ActionForm(title="§6死亡回溯")
        if player.name in self.death_points:
            loc = self.death_points[player.name]
            form.content = f"§7您上次死亡的位置: §e({int(loc.x)}, {int(loc.y)}, {int(loc.z)})"
            form.add_button("§a立即返回", on_click=lambda p: self.teleport_back(p))
        else:
            form.content = "§c当前没有记录的死亡点。"
        
        form.add_button("§c关闭")
        player.send_form(form)
