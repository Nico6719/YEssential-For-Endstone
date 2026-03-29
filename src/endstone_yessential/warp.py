import os
import json
from typing import Dict, Any
from endstone import Player
from endstone.level import Location
from endstone.form import ActionForm, ModalForm, TextInput

from .log import plugin_print

class WarpSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.data_folder = plugin.data_folder
        self.warp_path = os.path.join(self.data_folder, "warps.json")
        self.warp_data: Dict[str, Dict[str, float]] = {}
        self.load_warps()

    def load_warps(self):
        if not os.path.exists(self.warp_path):
            self.warp_data = {}
            self.save_warps()
        else:
            try:
                with open(self.warp_path, "r", encoding="utf-8") as f:
                    self.warp_data = json.load(f)
            except Exception as e:
                plugin_print(f"Failed to load warp data: {e}")
                self.warp_data = {}

    def save_warps(self):
        try:
            with open(self.warp_path, "w", encoding="utf-8") as f:
                json.dump(self.warp_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            plugin_print(f"Failed to save warp data: {e}")

    def set_warp(self, player: Player, warp_name: str):
        if not player.is_op:
            player.send_message("§c只有管理员可以设置传送点。")
            return

        loc = player.location
        self.warp_data[warp_name] = {
            "x": loc.x,
            "y": loc.y,
            "z": loc.z,
            "dimension": loc.dimension.name,
            "pitch": loc.pitch,
            "yaw": loc.yaw
        }
        self.save_warps()
        player.send_message(f"§6[YEssential] §a传送点 §e{warp_name} §a已设置。")

    def del_warp(self, player: Player, warp_name: str):
        if not player.is_op:
            player.send_message("§c只有管理员可以删除传送点。")
            return

        if warp_name in self.warp_data:
            del self.warp_data[warp_name]
            self.save_warps()
            player.send_message(f"§6[YEssential] §c传送点 §e{warp_name} §c已删除。")
        else:
            player.send_message(f"§c传送点 §e{warp_name} §c不存在。")

    def teleport_warp(self, player: Player, warp_name: str):
        if warp_name in self.warp_data:
            data = self.warp_data[warp_name]
            # 获取玩家当前位置的 dimension
            current_loc = player.location
            loc = Location(current_loc.dimension, data["x"], data["y"], data["z"], data["pitch"], data["yaw"])
            player.teleport(loc)
            player.send_message(f"§6[YEssential] §a已传送到传送点 §e{warp_name}§a。")
        else:
            player.send_message(f"§c传送点 §e{warp_name} §c不存在。")

    def open_warp_gui(self, player: Player):
        form = ActionForm(title="§6传送点系统")
        
        if player.is_op:
            form.add_button("§a设置新传送点", on_click=lambda p: self.open_set_warp_gui(p))
        
        for warp_name in self.warp_data.keys():
            form.add_button(f"§e{warp_name}", on_click=lambda p, w=warp_name: self.teleport_warp(p, w))
            
        player.send_form(form)

    def open_set_warp_gui(self, player: Player):
        form = ModalForm(
            title="§6设置传送点",
            controls=[TextInput(label="请输入传送点名称", placeholder="例如: spawn", default_value="spawn")],
            on_submit=lambda p, data: self.set_warp(p, data[0])
        )
        player.send_form(form)
