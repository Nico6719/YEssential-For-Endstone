import time
from typing import Dict, Any, Optional
from endstone import Player
from endstone.form import ActionForm, MessageForm

class TPASystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.pending_requests: Dict[str, Dict[str, Any]] = {}
        self.timeout = 60  # 默认 60 秒超时

    def send_tpa_request(self, sender: Player, target: Player, request_type: str = "to"):
        """
        发送 TPA 请求
        :param sender: 发送者
        :param target: 目标玩家
        :param request_type: "to" (tpa) 或 "here" (tpahere)
        """
        sender_name = sender.name
        target_name = target.name

        # 记录请求 - 使用 sender_name 作为 key，这样 tpayes 可以通过发送者的名字找到请求
        self.pending_requests[sender_name] = {
            "target": target_name,
            "type": request_type,
            "time": time.time()
        }

        # 通知发送者
        sender.send_message(f"§6[YEssential] §7已向 §a{target_name} §7发送传送请求。")

        # 通知目标玩家（使用 MessageForm 弹窗）
        title = "§6传送请求"
        content = f"§a{sender_name} §7请求传送至您的位置。" if request_type == "to" else f"§a{sender_name} §7请求您传送至其位置。"
        
        form = MessageForm(
            title=title,
            content=content,
            button1="§a接受",
            button2="§c拒绝",
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
            target.send_message("§c没有待处理的传送请求。")
            return

        request = self.pending_requests.pop(sender_name)
        if time.time() - request["time"] > self.timeout:
            target.send_message("§c请求已超时。")
            return

        # 获取原始请求发送者（要传送的玩家）
        sender = self.plugin.server.get_player(sender_name)
        if not sender:
            target.send_message(f"§c玩家 {sender_name} 已离线。")
            return

        target_name = target.name
        request_type = request["type"]

        if accepted:
            target.send_message(f"§6[YEssential] §7您已接受来自 §a{sender_name} §7的传送请求。")
            sender.send_message(f"§6[YEssential] §a{target_name} §7接受了您的传送请求。")
            
            # 执行传送
            if request_type == "to":
                # 发送者传送到目标位置
                sender.teleport(target.location)
            else:
                # 目标传送到发送者位置 (tpahere)
                target.teleport(sender.location)
        else:
            target.send_message(f"§6[YEssential] §7您已拒绝来自 §a{sender_name} §7的传送请求。")
            sender.send_message(f"§6[YEssential] §a{target_name} §7拒绝了您的传送请求。")

    def open_tpa_gui(self, player: Player):
        """打开 TPA 玩家选择界面"""
        online_players = self.plugin.server.online_players
        form = ActionForm(title="§6传送请求 - 选择玩家")
        
        # 过滤掉自己
        targets = [p for p in online_players if p.name != player.name]
        
        if not targets:
            form.content = "§c当前没有其他在线玩家。"
            form.add_button("§c关闭")
        else:
            for target in targets:
                form.add_button(f"§a{target.name}", on_click=lambda p, t=target: self.send_tpa_request(p, t))
        
        player.send_form(form)
