import os
import json
from typing import List
from endstone import Player
from endstone.form import ActionForm, ModalForm, TextInput

from .log import plugin_print
from .i18n import tr

class NoticeSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.data_folder = plugin.data_folder
        self.notice_path = os.path.join(self.data_folder, "notices.json")
        self.notices: List[str] = []
        self.load_notices()

    def load_notices(self):
        if not os.path.exists(self.notice_path):
            self.notices = [tr("notice.welcome"), tr("notice.rules")]
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
            title=tr("notice.title"),
            content=content
        )
        if player.is_op:
            form.add_button(tr("notice.add_btn"), on_click=lambda p: self.open_add_notice_gui(p))
        
        form.add_button(tr("notice.close"))
        player.send_form(form)

    def open_add_notice_gui(self, player: Player):
        form = ModalForm(
            title=tr("notice.add_title"),
            controls=[TextInput(label=tr("notice.content_label"), placeholder="例如: 祝大家游戏愉快！")],
            on_submit=lambda p, data: self.add_notice(p, data[0])
        )
        player.send_form(form)

    def add_notice(self, player: Player, content: str):
        if content:
            self.notices.append(content)
            self.save_notices()
            player.send_message(tr("notice.added"))
            self.show_notice(player)
