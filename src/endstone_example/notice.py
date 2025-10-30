import os
import time
from typing import List
from endstone import Player

class NoticeSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.server = plugin.server
        self.notice_content = ""
        self.last_update = 0
        self._load_notice()
    
    def show_notice(self, player: Player):
        """显示公告给玩家"""
        if not self.plugin.is_module_enabled("Notice"):
            return
        
        # 检查玩家设置
        settings = self.plugin.player_settings.get(player.name, {})
        if not settings.get("show_notice", True):
            return
        
        # 检查强制显示
        force_show = self.plugin.config_manager.get("Notice.force_show_on_update", True)
        last_seen = settings.get("last_notice", 0)
        
        if not force_show and last_seen >= self.last_update:
            return
        
        # 显示公告
        from endstone import CustomForm
        form = CustomForm()
        form.title = self.plugin.get_text("notice.title")
        
        # 添加公告内容
        lines = self.notice_content.split('\n')
        for line in lines:
            if line.strip():
                form.add_label(line)
        
        # 添加设置选项
        form.add_toggle(
            self.plugin.get_text("notice.dont.show"),
            not settings.get("show_notice", True)
        )
        
        def callback(p, data):
            if data is None:
                return
            
            # 更新玩家设置
            settings = self.plugin.player_settings.get(p.name, {})
            settings["show_notice"] = not data[-1]  # 最后一个元素是toggle状态
            settings["last_notice"] = time.time()
            self.plugin.player_settings[p.name] = settings
            
            if settings["show_notice"]:
                p.send_message(self.plugin.get_text("notice.show_enabled"))
            else:
                p.send_message(self.plugin.get_text("notice.show_disabled"))
        
        player.send_form(form, callback)
    
    def should_show_notice(self, player: Player) -> bool:
        """检查是否应该显示公告给玩家"""
        if not self.plugin.is_module_enabled("Notice"):
            return False
        
        if not self.plugin.config_manager.get("Notice.show_on_join", True):
            return False
        
        # 检查玩家设置
        settings = self.plugin.player_settings.get(player.name, {})
        if not settings.get("show_notice", True):
            return False
        
        # 检查强制显示
        force_show = self.plugin.config_manager.get("Notice.force_show_on_update", True)
        last_seen = settings.get("last_notice", 0)
        
        return force_show or last_seen < self.last_update
    
    def set_notice(self, content: str, player: Player = None) -> bool:
        """设置公告内容"""
        if player and not player.has_permission("yessential.notice.set"):
            player.send_message(self.plugin.get_text("player.not.op"))
            return False
        
        self.notice_content = content
        self.last_update = time.time()
        
        # 保存公告
        self._save_notice()
        
        if player:
            player.send_message(self.plugin.get_text("notice.set_success"))
        
        return True
    
    def _load_notice(self):
        """加载公告内容"""
        try:
            notice_path = os.path.join(self.plugin.data_folder, "notice.txt")
            if os.path.exists(notice_path):
                with open(notice_path, 'r', encoding='utf-8') as f:
                    self.notice_content = f.read().strip()
            else:
                self.notice_content = self.plugin.get_text("notice.default_content")
                self._save_notice()
        except Exception as e:
            self.plugin.logger.error(f"加载公告失败: {e}")
            self.notice_content = self.plugin.get_text("notice.default_content")
    
    def _save_notice(self):
        """保存公告内容"""
        try:
            notice_path = os.path.join(self.plugin.data_folder, "notice.txt")
            os.makedirs(os.path.dirname(notice_path), exist_ok=True)
            
            with open(notice_path, 'w', encoding='utf-8') as f:
                f.write(self.notice_content)
                
        except Exception as e:
            self.plugin.logger.error(f"保存公告失败: {e}")
    
    def open_notice_editor(self, player: Player):
        """打开公告编辑器（OP专用）"""
        if not player.has_permission("yessential.notice.edit"):
            player.send_message(self.plugin.get_text("player.not.op"))
            return
        
        from endstone import CustomForm
        form = CustomForm()
        form.title = self.plugin.get_text("notice.editor.title")
        
        form.add_input(
            self.plugin.get_text("notice.editor.content"),
            self.notice_content,
            self.plugin.get_text("notice.editor.placeholder")
        )
        
        def callback(p, data):
            if not data or not data[0]:
                return
            
            new_content = data[0]
            self.set_notice(new_content, p)
        
        player.send_form(form, callback)
