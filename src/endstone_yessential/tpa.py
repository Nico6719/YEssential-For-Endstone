import time
from typing import Dict, Any, Optional
from endstone import Player
from .i18n import tr
from endstone.form import ActionForm, MessageForm

class TPASystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.pending_requests: Dict[str, Dict[str, Any]] = {}
        tpa_cfg = plugin.config_manager.config_data.get("tpa", {})
        self.timeout = tpa_cfg.get("timeout", 60)

    def send_tpa_request(self, sender: Player, target: Player, request_type: str = "to"):
        """
        发送 TPA 请求
        :param sender: 发送者
        :param target: 目标玩家
        :param request_type: "to" (tpa) 或 "here" (tpahere)
        """
        sender_name = sender.name
        target_name = target.name

        # 目标已屏蔽所有请求
        if self.is_blocked(target_name):
            sender.send_message(tr("tpa.target_blocked", target_name))
            return

        # 已有待处理请求则拒绝
        if sender_name in self.pending_requests:
            sender.send_message(tr("tpa.already_pending"))
            return

        # 记录请求 - 使用 sender_name 作为 key，这样 tpayes 可以通过发送者的名字找到请求
        self.pending_requests[sender_name] = {
            "target": target_name,
            "type": request_type,
            "time": time.time()
        }

        # 通知发送者
        sender.send_message(tr("tpa.sent", target_name))

        # 通知目标玩家（使用 MessageForm 弹窗）
        title = tr("tpa.request_title")
        content = tr("tpa.request_to", sender_name) if request_type == "to" else tr("tpa.request_here", sender_name)
        
        form = MessageForm(
            title=title,
            content=content,
            button1=tr("tpa.accept"),
            button2=tr("tpa.reject"),
            on_submit=lambda p, idx: self.handle_tpa_response(p, sender_name, idx == 0)
        )
        target.send_form(form)

    def handle_tpa_response(self, target: Player, sender_name: str, accepted: bool):
        """
        处理 TPA 响应
        :param target: 响应者（接受或拒绝请求的玩家）
        :param sender_name: 原始请求发送者的名字
        :param accepted: 是否接受
        """
        # pending_requests 使用 sender_name 作为 key
        if sender_name not in self.pending_requests:
            target.send_message(tr("tpa.no_pending"))
            return

        request = self.pending_requests.pop(sender_name)
        if time.time() - request["time"] > self.timeout:
            target.send_message(tr("tpa.timeout"))
            return

        # 获取原始请求发送者（要传送的玩家）
        sender = self.plugin.server.get_player(sender_name)
        if not sender:
            target.send_message(tr("tpa.offline", sender_name))
            return

        target_name = target.name
        request_type = request["type"]

        if accepted:
            target.send_message(tr("tpa.accepted", sender_name))
            sender.send_message(tr("tpa.sender_accepted", target_name))
            
            # 执行传送
            if request_type == "to":
                # 发送者传送到目标位置
                sender.teleport(target.location)
            else:
                # 目标传送到发送者位置 (tpahere)
                target.teleport(sender.location)
        else:
            target.send_message(tr("tpa.rejected", sender_name))
            sender.send_message(tr("tpa.sender_rejected", target_name))

    def open_tpa_gui(self, player: Player):
        """打开 TPA 玩家选择界面"""
        online_players = self.plugin.server.online_players
        form = ActionForm(title=tr("tpa.title"))

        # 过滤掉自己
        targets = [p for p in online_players if p.name != player.name]

        if not targets:
            form.content = tr("tpa.no_players")
            form.add_button(tr("tpa.close"))
        else:
            for target in targets:
                form.add_button(f"§a{target.name}", on_click=lambda p, t=target: self.send_tpa_request(p, t))

        player.send_form(form)

    def toggle_settings(self, player: Player):
        """开关 TPA 设置：是否自动拒绝所有请求"""
        name = player.name
        blocked = getattr(self, '_blocked', set())
        if name in blocked:
            blocked.discard(name)
            player.send_message(tr("tpa.settings_on"))
        else:
            blocked.add(name)
            player.send_message(tr("tpa.settings_off"))
        self._blocked = blocked

    def is_blocked(self, player_name: str) -> bool:
        return player_name in getattr(self, '_blocked', set())
