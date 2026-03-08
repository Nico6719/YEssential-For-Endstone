import os
import json
from typing import Dict, Any
from endstone import Player

from .log import plugin_print

class EconomySystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.data_folder = plugin.data_folder
        self.money_path = os.path.join(self.data_folder, "money.json")
        self.money_data: Dict[str, float] = {}
        self.load_money()

    def load_money(self):
        if not os.path.exists(self.money_path):
            self.money_data = {}
            self.save_money()
        else:
            try:
                with open(self.money_path, "r", encoding="utf-8") as f:
                    self.money_data = json.load(f)
            except Exception as e:
                plugin_print(f"Failed to load money data: {e}")
                self.money_data = {}

    def save_money(self):
        try:
            with open(self.money_path, "w", encoding="utf-8") as f:
                json.dump(self.money_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            plugin_print(f"Failed to save money data: {e}")

    def get_money(self, player_name: str) -> float:
        return self.money_data.get(player_name, 0.0)

    def add_money(self, player_name: str, amount: float):
        current = self.get_money(player_name)
        self.money_data[player_name] = current + amount
        self.save_money()

    def reduce_money(self, player_name: str, amount: float) -> bool:
        current = self.get_money(player_name)
        if current >= amount:
            self.money_data[player_name] = current - amount
            self.save_money()
            return True
        return False

    def set_money(self, player_name: str, amount: float):
        self.money_data[player_name] = amount
        self.save_money()

    def open_money_gui(self, player: Player):
        # 示例：使用 Endstone Form API 创建简单的余额显示
        from endstone.form import ActionForm
        
        balance = self.get_money(player.name)
        form = ActionForm(
            title="§6经济系统",
            content=f"§7您的当前余额为: §a{balance} §7金币",
            on_submit=lambda p, idx: None
        )
        form.add_button("§c关闭")
        player.send_form(form)
