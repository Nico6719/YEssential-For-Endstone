import os
import json
from typing import Dict, Any
from endstone import Player
from endstone.form import ActionForm, Toggle

from .log import plugin_print

class PVPSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.data_folder = plugin.data_folder
        self.pvp_path = os.path.join(self.data_folder, "pvp_settings.json")
        self.pvp_settings: Dict[str, bool] = {}
        self.load_pvp_settings()

    def load_pvp_settings(self):
        if not os.path.exists(self.pvp_path):
            self.pvp_settings = {}
            self.save_pvp_settings()
        else:
            try:
                with open(self.pvp_path, "r", encoding="utf-8") as f:
                    self.pvp_settings = json.load(f)
            except Exception as e:
                plugin_print(f"Failed to load PVP settings: {e}")
                self.pvp_settings = {}

    def save_pvp_settings(self):
        try:
            with open(self.pvp_path, "w", encoding="utf-8") as f:
                json.dump(self.pvp_settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            plugin_print(f"Failed to save PVP settings: {e}")

    def is_pvp_enabled(self, player_name: str) -> bool:
        """检查玩家是否开启了 PVP"""
        return self.pvp_settings.get(player_name, True)

    def set_pvp(self, player: Player, enabled: bool):
        """设置玩家 PVP 状态"""
        self.pvp_settings[player.name] = enabled
        self.save_pvp_settings()
        status = "§a开启" if enabled else "§c关闭"
        player.send_message(f"§6[YEssential] §7您的 PVP 状态已设置为: {status}§7。")

    def open_pvp_gui(self, player: Player):
        """打开 PVP 设置 GUI"""
        current_status = self.is_pvp_enabled(player.name)
        form = ActionForm(
            title="§6PVP 设置",
            content=f"§7当前状态: {'§a开启' if current_status else '§c关闭'}"
        )
        form.add_button("§a开启 PVP", on_click=lambda p: self.set_pvp(p, True))
        form.add_button("§c关闭 PVP", on_click=lambda p: self.set_pvp(p, False))
        form.add_button("§c关闭")
        player.send_form(form)
