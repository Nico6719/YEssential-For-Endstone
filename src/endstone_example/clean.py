import time
from typing import List
from endstone import Player, Entity

class CleanSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.server = plugin.server
        self.last_clean_time = 0
        self.clean_countdown = 0
    
    def check_and_clean(self):
        """检查并执行清理"""
        if not self.plugin.is_module_enabled("AutoClean"):
            return
        
        current_time = time.time()
        interval = self.plugin.config_manager.get("AutoClean.interval", 60)
        
        # 检查是否到达清理时间
        if current_time - self.last_clean_time < interval:
            return
        
        # 执行清理
        self.perform_clean()
        self.last_clean_time = current_time
    
    def perform_clean(self, player: Player = None):
        """执行清理操作"""
        try:
            # 获取所有掉落物实体
            item_entities = []
            for entity in self.server.get_entities():
                if entity.is_item_entity():
                    item_entities.append(entity)
            
            total_count = len(item_entities)
            
            if total_count == 0:
                if player:
                    player.send_message(self.plugin.get_text("clean.no_items"))
                return
            
            # 批量清理
            batch_size = self.plugin.config_manager.get("AutoClean.batch_size", 200)
            cleaned_count = 0
            
            for i, entity in enumerate(item_entities):
                if i >= batch_size:
                    break
                entity.despawn()
                cleaned_count += 1
            
            # 发送清理结果
            message = self.plugin.get_text("clean.result", count=cleaned_count, total=total_count)
            if player:
                player.send_message(message)
            else:
                self.server.broadcast_message(message)
            
            self.plugin.logger.info(f"清理完成: {cleaned_count}/{total_count} 个掉落物")
            
        except Exception as e:
            self.plugin.logger.error(f"执行清理失败: {e}")
            if player:
                player.send_message(self.plugin.get_text("clean.failed"))
    
    def start_countdown(self, player: Player = None):
        """开始清理倒计时"""
        if not self.plugin.is_module_enabled("AutoClean"):
            if player:
                player.send_message(self.plugin.get_text("module.no.enabled"))
            return
        
        self.clean_countdown = self.plugin.config_manager.get("AutoClean.interval", 60)
        
        # 广播倒计时开始
        message = self.plugin.get_text("clean.countdown_start", seconds=self.clean_countdown)
        if player:
            player.send_message(message)
        else:
            self.server.broadcast_message(message)
        
        # 设置倒计时任务
        self._run_countdown()
    
    def _run_countdown(self):
        """运行清理倒计时"""
        if self.clean_countdown <= 0:
            self.perform_clean()
            return
        
        # 检查警告时间
        warn_times = self.plugin.config_manager.get("AutoClean.warn_times", [30, 15, 10, 5, 3, 2, 1])
        if self.clean_countdown in warn_times:
            message = self.plugin.get_text("clean.countdown_warn", seconds=self.clean_countdown)
            self.server.broadcast_message(message)
        
        # 减少倒计时并设置下一次检查
        self.clean_countdown -= 1
        self.server.get_scheduler().call_later(1.0, self._run_countdown)
    
    def open_clean_gui(self, player: Player):
        """打开清理系统GUI"""
        if not player.has_permission("yessential.clean.manage"):
            player.send_message(self.plugin.get_text("player.not.op"))
            return
        
        from endstone import SimpleForm
        form = SimpleForm()
        form.title = self.plugin.get_text("clean.gui.title")
        
        # 获取当前掉落物数量
        item_count = len([e for e in self.server.get_entities() if e.is_item_entity()])
        form.content = self.plugin.get_text("clean.gui.status", count=item_count)
        
        form.add_button(
            self.plugin.get_text("clean.gui.clean_now"),
            callback=lambda p, data: self.perform_clean(p)
        )
        
        form.add_button(
            self.plugin.get_text("clean.gui.start_countdown"),
            callback=lambda p, data: self.start_countdown(p)
        )
        
        player.send_form(form)
