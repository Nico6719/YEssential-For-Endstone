import os
import json
from typing import List
from endstone import Player
from endstone.form import ActionForm, ModalForm, TextInput

from .log import plugin_print

class NoticeSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.data_folder = plugin.data_folder
        self.notice_path = os.path.join(self.data_folder, "notices.json")
        self.notices: List[str] = []
        self.load_notices()

    def load_notices(self):
        if not os.path.exists(self.notice_path):
            self.notices = ["欢迎来到服务器！", "请遵守服务器规则。"]
            self.save_notices()
        else:
            try:
                with open(self.notice_path, "r", encoding="utf-8") as f:
                    self.notices = json.load(f)
            except Exception as e:
                plugin_print(f"Failed to load notice data: {e}")
                self.notices = []

    def save_notices(self):
        try:
            with open(self.notice_path, "w", encoding="utf-8") as f:
                json.dump(self.notices, f, indent=4, ensure_ascii=False)
        except Exception as e:
            plugin_print(f"Failed to save notice data: {e}")

    def show_notice(self, player: Player):
        """显示公告"""
        content = "\n".join([f"§7- §f{n}" for n in self.notices])
        form = ActionForm(
            title="§6服务器公告",
            content=content
        )
        if player.is_op:
            form.add_button("§a添加公告", on_click=lambda p: self.open_add_notice_gui(p))
        
        form.add_button("§c关闭")
        player.send_form(form)

    def open_add_notice_gui(self, player: Player):
        form = ModalForm(
            title="§6添加公告",
            controls=[TextInput(label="请输入公告内容", placeholder="例如: 祝大家游戏愉快！")],
            on_submit=lambda p, data: self.add_notice(p, data[0])
        )
        player.send_form(form)

    def add_notice(self, player: Player, content: str):
        if content:
            self.notices.append(content)
            self.save_notices()
            player.send_message("§6[YEssential] §a公告已添加。")
            self.show_notice(player)
