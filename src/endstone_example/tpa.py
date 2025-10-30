import time
from typing import Dict, Optional
from endstone import Player

class TPASystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.server = plugin.server
        self.pending_requests = {}
    
    def send_tpa_request(self, from_player: Player, to_player: Player, direction: str = "to") -> bool:
        """发送传送请求"""
        if not self.plugin.is_module_enabled("TPA"):
            from_player.send_message(self.plugin.get_text("module.no.enabled"))
            return False
        
        # 检查目标玩家是否接受传送请求
        if not self._can_accept_tpa(to_player):
            from_player.send_message(self.plugin.get_text("tpa.target_refused"))
            return False
        
        # 检查是否已有待处理请求
        if to_player.name in self.pending_requests:
            from_player.send_message(self.plugin.get_text("tpa.pending_exists"))
            return False
        
        # 创建请求
        request_id = int(time.time())
        request = {
            "id": request_id,
            "from_player": from_player,
            "to_player": to_player,
            "direction": direction,  # "to" 或 "here"
            "sent_time": time.time(),
            "timeout": self.plugin.config_manager.get("TPA.request_timeout", 60)
        }
        
        self.pending_requests[to_player.name] = request
        
        # 发送请求通知
        direction_text = self.plugin.get_text("tpa.to_target") if direction == "to" else self.plugin.get_text("tpa.to_self")
        to_player.send_message(self.plugin.get_text("tpa.request.received", player=from_player.name, action=direction_text))
        to_player.send_message(self.plugin.get_text("tpa.request.actions"))
        
        from_player.send_message(self.plugin.get_text("tpa.request.sent", player=to_player.name))
        
        # 设置超时
        self._set_request_timeout(request_id, to_player.name)
        
        return True
    
    def accept_tpa_request(self, player: Player) -> bool:
        """接受传送请求"""
        if player.name not in self.pending_requests:
            player.send_message(self.plugin.get_text("tpa.no_requests"))
            return False
        
        request = self.pending_requests[player.name]
        from_player = request["from_player"]
        direction = request["direction"]
        
        # 检查玩家是否在线
        if not from_player.is_online():
            player.send_message(self.plugin.get_text("tpa.player_offline"))
            del self.pending_requests[player.name]
            return False
        
        # 执行传送
        try:
            if direction == "to":
                # 传送到目标玩家
                from_player.teleport(player.location)
            else:
                # 目标玩家传送到请求玩家
                player.teleport(from_player.location)
            
            # 发送成功消息
            player.send_message(self.plugin.get_text("tpa.accepted"))
            from_player.send_message(self.plugin.get_text("tpa.accepted"))
            
            # 清理请求
            del self.pending_requests[player.name]
            return True
            
        except Exception as e:
            self.plugin.logger.error(f"传送请求执行失败: {e}")
            player.send_message(self.plugin.get_text("tpa.failed"))
            from_player.send_message(self.plugin.get_text("tpa.failed"))
            del self.pending_requests[player.name]
            return False
    
    def deny_tpa_request(self, player: Player) -> bool:
        """拒绝传送请求"""
        if player.name not in self.pending_requests:
            player.send_message(self.plugin.get_text("tpa.no_requests"))
            return False
        
        request = self.pending_requests[player.name]
        from_player = request["from_player"]
        
        # 发送拒绝消息
        player.send_message(self.plugin.get_text("tpa.denied.self"))
        if from_player.is_online():
            from_player.send_message(self.plugin.get_text("tpa.denied.by_target"))
        
        # 清理请求
        del self.pending_requests[player.name]
        return True
    
    def _can_accept_tpa(self, player: Player) -> bool:
        """检查玩家是否可以接受传送请求"""
        # 检查玩家设置
        settings = self.plugin.player_settings.get(player.name, {})
        return settings.get("accept_tpa", True)
    
    def _set_request_timeout(self, request_id: int, player_name: str):
        """设置请求超时"""
        timeout = self.plugin.config_manager.get("TPA.request_timeout", 60)
        
        def timeout_callback():
            if player_name in self.pending_requests and self.pending_requests[player_name]["id"] == request_id:
                request = self.pending_requests[player_name]
                from_player = request["from_player"]
                
                # 发送超时消息
                if from_player.is_online():
                    from_player.send_message(self.plugin.get_text("tpa.timeout"))
                
                # 清理请求
                del self.pending_requests[player_name]
        
        # 设置超时回调
        self.server.get_scheduler().call_later(timeout, timeout_callback)
    
    def cleanup_player_requests(self, player: Player):
        """清理玩家的所有请求"""
        # 清理玩家发送的请求
        expired_requests = []
        for target_name, request in self.pending_requests.items():
            if request["from_player"].name == player.name:
                expired_requests.append(target_name)
        
        for target_name in expired_requests:
            del self.pending_requests[target_name]
        
        # 清理玩家接收的请求
        if player.name in self.pending_requests:
            del self.pending_requests[player.name]
    
    def open_tpa_gui(self, player: Player):
        """打开传送请求GUI"""
        from endstone import SimpleForm
        
        form = SimpleForm()
        form.title = self.plugin.get_text("tpa.gui.title")
        
        # 获取在线玩家（排除自己）
        online_players = [p for p in self.server.get_online_players() if p != player]
        
        if not online_players:
            player.send_message(self.plugin.get_text("tpa.no_players"))
            return
        
        form.content = self.plugin.get_text("tpa.gui.select_target")
        
        for target in online_players:
            form.add_button(
                target.name,
                callback=lambda p, data, t=target: self._open_tpa_direction_gui(p, t)
            )
        
        player.send_form(form)
    
    def _open_tpa_direction_gui(self, player: Player, target: Player):
        """打开传送方向选择GUI"""
        from endstone import SimpleForm
        
        form = SimpleForm()
        form.title = self.plugin.get_text("tpa.gui.direction.title")
        form.content = self.plugin.get_text("tpa.gui.direction.select", player=target.name)
        
        form.add_button(
            self.plugin.get_text("tpa.to_target"),
            callback=lambda p, data, t=target: self.send_tpa_request(p, t, "to")
        )
        
        form.add_button(
            self.plugin.get_text("tpa.to_self"),
            callback=lambda p, data, t=target: self.send_tpa_request(p, t, "here")
        )
        
        player.send_form(form)
    
    def open_tpa_manage_gui(self, player: Player):
        """打开传送管理GUI"""
        from endstone import SimpleForm
        
        form = SimpleForm()
        form.title = self.plugin.get_text("tpa.gui.manage.title")
        
        # 检查是否有待处理请求
        if player.name in self.pending_requests:
            form.add_button(
                self.plugin.get_text("tpa.gui.manage.accept"),
                callback=lambda p, data: self.accept_tpa_request(p)
            )
            form.add_button(
                self.plugin.get_text("tpa.gui.manage.deny"),
                callback=lambda p, data: self.deny_tpa_request(p)
            )
        else:
            form.content = self.plugin.get_text("tpa.no_requests")
        
        # 设置选项
        settings = self.plugin.player_settings.get(player.name, {})
        accept_tpa = settings.get("accept_tpa", True)
        
        status_text = self.plugin.get_text("tpa.gui.manage.status_enabled") if accept_tpa else self.plugin.get_text("tpa.gui.manage.status_disabled")
        form.add_button(
            f"{self.plugin.get_text('tpa.gui.manage.toggle')} ({status_text})",
            callback=lambda p, data: self._toggle_tpa_setting(p)
        )
        
        player.send_form(form)
    
    def _toggle_tpa_setting(self, player: Player):
        """切换传送设置"""
        settings = self.plugin.player_settings.get(player.name, {})
        current = settings.get("accept_tpa", True)
        settings["accept_tpa"] = not current
        
        self.plugin.player_settings[player.name] = settings
        
        if settings["accept_tpa"]:
            player.send_message(self.plugin.get_text("tpa.settings.enabled"))
        else:
            player.send_message(self.plugin.get_text("tpa.settings.disabled"))
