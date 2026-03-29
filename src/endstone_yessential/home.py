import os
import json
from typing import Dict, Any, List
import ast
from endstone import Player
from endstone.level import Location
from endstone.form import ActionForm, ModalForm, TextInput

from .log import plugin_print

class HomeSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.data_folder = plugin.data_folder
        self.home_path = os.path.join(self.data_folder, "homes.json")
        self.home_data: Dict[str, Dict[str, Dict[str, float]]] = {}
        self.load_homes()

    def load_homes(self):
        if not os.path.exists(self.home_path):
            self.home_data = {}
            self.save_homes()
        else:
            try:
                with open(self.home_path, "r", encoding="utf-8") as f:
                    self.home_data = json.load(f)
            except Exception as e:
                plugin_print(f"Failed to load home data: {e}")
                self.home_data = {}

    def save_homes(self):
        try:
            with open(self.home_path, "w", encoding="utf-8") as f:
                json.dump(self.home_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            plugin_print(f"Failed to save home data: {e}")

    def set_home(self, player: Player, home_name: str):
        # 如果 home_name 是 JSON 字符串，解析它
        if isinstance(home_name, str) and home_name.startswith('['):
            try:
                home_name = json.loads(home_name)[0]
            except:
                pass
        plugin_print(f"Debug: home_name = {repr(home_name)}")
        player_name = player.name
        if player_name not in self.home_data:
            self.home_data[player_name] = {}

        loc = player.location
        self.home_data[player_name][home_name] = {
            "x": loc.x,
            "y": loc.y,
            "z": loc.z,
            "dimension": loc.dimension.name,
            "pitch": loc.pitch,
            "yaw": loc.yaw
        }
        self.save_homes()
        player.send_message(f"§6[YEssential] §a家园 §e{home_name} §a已设置。")

    def del_home(self, player: Player, home_name: str):
        player_name = player.name
        if player_name in self.home_data and home_name in self.home_data[player_name]:
            del self.home_data[player_name][home_name]
            self.save_homes()
            player.send_message(f"§6[YEssential] §c家园 §e{home_name} §c已删除。")
            # 删除后重新打开主界面
            self.open_home_gui(player)
        else:
            player.send_message(f"§c家园 §e{home_name} §c不存在。")

    def teleport_home(self, player: Player, home_name: str):
        player_name = player.name
        if player_name in self.home_data and home_name in self.home_data[player_name]:
            data = self.home_data[player_name][home_name]
            # 注意：Endstone 的 Location 构造函数需要 dimension 对象作为第一个参数
            # Location(dimension, x, y, z, pitch, yaw)
            # 获取玩家当前位置的 dimension
            current_loc = player.location
            loc = Location(current_loc.dimension, data["x"], data["y"], data["z"], data["pitch"], data["yaw"])
            player.teleport(loc)
            player.send_message(f"§6[YEssential] §a已传送到家园 §e{home_name}§a。")
        else:
            player.send_message(f"§c家园 §e{home_name} §c不存在。")

    def open_home_gui(self, player: Player):
        player_name = player.name
        homes = self.home_data.get(player_name, {})

        form = ActionForm(title="§6家园系统")
        form.add_button("§a设置新家", on_click=lambda p: self.open_set_home_gui(p))

        for home_name in homes.keys():
            form.add_button(f"§e{home_name}", on_click=lambda p, h=home_name: self.open_home_options_gui(p, h))

        player.send_form(form)

    def open_home_options_gui(self, player: Player, home_name: str):
        """打开家园选项界面，提供传送和删除选项"""
        form = ActionForm(title=f"§6家园: {home_name}")
        form.add_button("§a传送到此家", on_click=lambda p: self.teleport_home(p, home_name))
        form.add_button("§c删除此家", on_click=lambda p: self.del_home(p, home_name))
        form.add_button("§c返回", on_click=lambda p: self.open_home_gui(p))
        player.send_form(form)

    def open_set_home_gui(self, player: Player):
        form = ModalForm(
            title="§6设置家园",
            controls=[TextInput(label="请输入家园名称", placeholder="例如: home1", default_value="home")],
            on_submit=lambda p, data: (plugin_print(f"Debug: data = {repr(data)}"), self.set_home(p, json.loads(data)[0]))
        )
        player.send_form(form)
