import random
import time
import json
import os
from typing import Dict, List, Optional
from endstone import Player

class RedPacketSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.server = plugin.server
        self.red_packets = {}
        self.next_id = 1
        self._load_red_packets()
    
    def send_red_packet(self, player: Player, total_amount: float, count: int, 
                       packet_type: str = "random", target_player: str = None, 
                       message: str = "") -> bool:
        """发送红包"""
        if not self.plugin.is_module_enabled("RedPacket"):
            player.send_message(self.plugin.get_text("module.no.enabled"))
            return False
        
        # 参数验证
        config = self.plugin.config_manager.get("RedPacket", {})
        max_amount = config.get("max_amount", 10000)
        max_count = config.get("max_count", 50)
        min_amount = config.get("min_amount", 1)
        
        if total_amount < min_amount or total_amount > max_amount:
            player.send_message(self.plugin.get_text("redpacket.invalid_amount", min=min_amount, max=max_amount))
            return False
        
        if count < 1 or count > max_count:
            player.send_message(self.plugin.get_text("redpacket.invalid_count", min=1, max=max_count))
            return False
        
        # 检查余额
        if not self.plugin.economy.reduce_balance(player, total_amount):
            player.send_message(self.plugin.get_text("economy.no.enough"))
            return False
        
        # 创建红包
        packet_id = self.next_id
        self.next_id += 1
        
        red_packet = {
            "id": packet_id,
            "sender": player.name,
            "total_amount": total_amount,
            "remaining_amount": total_amount,
            "count": count,
            "remaining_count": count,
            "packet_type": packet_type,  # "random" 或 "average"
            "target_player": target_player,
            "message": message or self.plugin.get_text("redpacket.default_message", player=player.name),
            "created_time": time.time(),
            "expire_time": time.time() + config.get("expire_time", 300),
            "recipients": []
        }
        
        self.red_packets[packet_id] = red_packet
        
        # 广播红包消息
        if target_player:
            target = self.server.get_player(target_player)
            if target:
                target.send_message(self.plugin.get_text("redpacket.private_received", sender=player.name))
            player.send_message(self.plugin.get_text("redpacket.private_sent", target=target_player, amount=total_amount, count=count))
        else:
            self.server.broadcast_message(self.plugin.get_text("redpacket.public_announce", sender=player.name, amount=total_amount, count=count))
            player.send_message(self.plugin.get_text("redpacket.public_sent", amount=total_amount, count=count))
        
        # 保存数据
        self._save_red_packets()
        return True
    
    def open_red_packet(self, player: Player, packet_id: int) -> Optional[float]:
        """打开红包"""
        if packet_id not in self.red_packets:
            return None
        
        packet = self.red_packets[packet_id]
        
        # 检查过期
        if time.time() > packet["expire_time"]:
            self._handle_expired_packet(packet_id)
            return None
        
        # 检查目标玩家
        if packet["target_player"] and packet["target_player"] != player.name:
            return None
        
        # 检查是否已经领取过
        if player.name in packet["recipients"]:
            return None
        
        # 检查是否还有剩余
        if packet["remaining_count"] <= 0 or packet["remaining_amount"] <= 0:
            return None
        
        # 计算领取金额
        if packet["remaining_count"] == 1:
            # 最后一个红包，领取剩余全部金额
            amount = packet["remaining_amount"]
        else:
            if packet["packet_type"] == "random":
                # 随机红包
                max_amount = min(
                    packet["remaining_amount"] - packet["remaining_count"] + 1,
                    packet["remaining_amount"] / packet["remaining_count"] * 2
                )
                amount = random.randint(1, int(max_amount))
            else:
                # 平均红包
                amount = packet["remaining_amount"] // packet["remaining_count"]
        
        # 确保金额有效
        amount = max(1, min(amount, packet["remaining_amount"]))
        
        # 更新红包数据
        packet["remaining_amount"] -= amount
        packet["remaining_count"] -= 1
        packet["recipients"].append(player.name)
        
        # 给玩家发放金额
        self.plugin.economy.add_balance(player, amount)
        
        # 通知玩家
        player.send_message(self.plugin.get_text("redpacket.open_success", amount=amount))
        
        # 通知发送者
        sender = self.server.get_player(packet["sender"])
        if sender and sender.is_online():
            sender.send_message(self.plugin.get_text("redpacket.recipient_notify", player=player.name, amount=amount))
        
        # 检查红包是否已经领完
        if packet["remaining_count"] <= 0:
            self._handle_empty_packet(packet_id)
        
        # 保存数据
        self._save_red_packets()
        return amount
    
    def get_available_packets(self, player: Player) -> List[Dict]:
        """获取玩家可领取的红包"""
        available = []
        current_time = time.time()
        
        for packet_id, packet in self.red_packets.items():
            # 检查过期
            if current_time > packet["expire_time"]:
                continue
            
            # 检查是否已经领取
            if player.name in packet["recipients"]:
                continue
            
            # 检查是否还有剩余
            if packet["remaining_count"] <= 0:
                continue
            
            # 检查目标玩家限制
            if packet["target_player"] and packet["target_player"] != player.name:
                continue
            
            available.append(packet)
        
        return available
    
    def _handle_expired_packet(self, packet_id: int):
        """处理过期红包"""
        if packet_id not in self.red_packets:
            return
        
        packet = self.red_packets[packet_id]
        
        # 退还剩余金额给发送者
        if packet["remaining_amount"] > 0:
            sender = self.server.get_player(packet["sender"])
            if sender:
                self.plugin.economy.add_balance(sender, packet["remaining_amount"])
                sender.send_message(self.plugin.get_text("redpacket.expired_refund", amount=packet["remaining_amount"]))
        
        # 删除红包
        del self.red_packets[packet_id]
        self._save_red_packets()
    
    def _handle_empty_packet(self, packet_id: int):
        """处理已领完的红包"""
        # 可以在这里添加一些清理逻辑
        # 目前只是记录日志
        self.plugin.logger.info(f"红包 #{packet_id} 已被领完")
    
    def open_redpacket_gui(self, player: Player):
        """打开红包系统GUI"""
        from endstone import SimpleForm
        
        form = SimpleForm()
        form.title = self.plugin.get_text("redpacket.gui.title")
        
        form.add_button(self.plugin.get_text("redpacket.gui.send"), callback=lambda p, _: self._open_send_gui(p))
        form.add_button(self.plugin.get_text("redpacket.gui.open"), callback=lambda p, _: self._open_available_gui(p))
        form.add_button(self.plugin.get_text("redpacket.gui.history"), callback=lambda p, _: self._open_history_gui(p))
        form.add_button(self.plugin.get_text("redpacket.gui.help"), callback=lambda p, _: self._show_help(p))
        
        player.send_form(form)
    
    def _open_send_gui(self, player: Player):
        """打开发送红包GUI"""
        from endstone import CustomForm
        
        form = CustomForm()
        form.title = self.plugin.get_text("redpacket.gui.send.title")
        
        form.add_dropdown(
            self.plugin.get_text("redpacket.gui.send.type"),
            [
                self.plugin.get_text("redpacket.type.random"),
                self.plugin.get_text("redpacket.type.average")
            ]
        )
        form.add_input(self.plugin.get_text("redpacket.gui.send.amount"), "100")
        form.add_input(self.plugin.get_text("redpacket.gui.send.count"), "5")
        form.add_input(self.plugin.get_text("redpacket.gui.send.target"), "", self.plugin.get_text("redpacket.gui.send.target_placeholder"))
        form.add_input(self.plugin.get_text("redpacket.gui.send.message"), "", self.plugin.get_text("redpacket.gui.send.message_placeholder"))
        
        def callback(p, data):
            if not data:
                return
            
            try:
                packet_type = "random" if data[0] == 0 else "average"
                total_amount = float(data[1])
                count = int(data[2])
                target_player = data[3].strip() or None
                message = data[4].strip()
                
                self.send_red_packet(p, total_amount, count, packet_type, target_player, message)
                
            except (ValueError, IndexError):
                p.send_message(self.plugin.get_text("redpacket.invalid_input"))
        
        player.send_form(form, callback)
    
    def _open_available_gui(self, player: Player):
        """打开可领取红包GUI"""
        available_packets = self.get_available_packets(player)
        
        if not available_packets:
            player.send_message(self.plugin.get_text("redpacket.no_available"))
            return
        
        from endstone import SimpleForm
        form = SimpleForm()
        form.title = self.plugin.get_text("redpacket.gui.available.title")
        form.content = self.plugin.get_text("redpacket.gui.available.select")
        
        for packet in available_packets:
            # 计算剩余时间
            remaining_time = int(packet["expire_time"] - time.time())
            
            form.add_button(
                f"{packet['sender']}的红包\n剩余: {packet['remaining_count']}/{packet['count']} 金额: {packet['remaining_amount']}\n剩余时间: {remaining_time}秒",
                callback=lambda p, data, pid=packet['id']: self.open_red_packet(p, pid)
            )
        
        player.send_form(form)
    
    def _open_history_gui(self, player: Player):
        """打开红包历史GUI"""
        # 获取玩家相关的红包（发送或接收的）
        player_packets = []
        
        for packet in self.red_packets.values():
            if packet["sender"] == player.name or player.name in packet["recipients"]:
                player_packets.append(packet)
        
        if not player_packets:
            player.send_message(self.plugin.get_text("redpacket.no_history"))
            return
        
        from endstone import SimpleForm
        form = SimpleForm()
        form.title = self.plugin.get_text("redpacket.gui.history.title")
        
        for packet in player_packets[:10]:  # 只显示最近10个
            status = "已完成" if packet["remaining_count"] == 0 else f"剩余{packet['remaining_count']}"
            is_sender = packet["sender"] == player.name
            
            form.add_button(
                f"{'[发送]' if is_sender else '[接收]'} {packet['message']}\n状态: {status}",
                callback=lambda p, data, pid=packet['id']: self._show_packet_detail(p, pid)
            )
        
        player.send_form(form)
    
    def _show_packet_detail(self, player: Player, packet_id: int):
        """显示红包详情"""
        if packet_id not in self.red_packets:
            player.send_message(self.plugin.get_text("redpacket.not_found"))
            return
        
        packet = self.red_packets[packet_id]
        
        from endstone import CustomForm
        form = CustomForm()
        form.title = self.plugin.get_text("redpacket.gui.detail.title")
        
        form.add_label(self.plugin.get_text("redpacket.gui.detail.sender", sender=packet["sender"]))
        form.add_label(self.plugin.get_text("redpacket.gui.detail.message", message=packet["message"]))
        form.add_label(self.plugin.get_text("redpacket.gui.detail.type", type=self.plugin.get_text(f"redpacket.type.{packet['packet_type']}")))
        form.add_label(self.plugin.get_text("redpacket.gui.detail.total", total=packet["total_amount"]))
        form.add_label(self.plugin.get_text("redpacket.gui.detail.remaining", remaining=packet["remaining_amount"]))
        form.add_label(self.plugin.get_text("redpacket.gui.detail.recipients", count=len(packet["recipients"])))
        
        # 显示领取者列表
        if packet["recipients"]:
            form.add_label(self.plugin.get_text("redpacket.gui.detail.recipient_list"))
            for recipient in packet["recipients"]:
                form.add_label(f"  - {recipient}")
        
        player.send_form(form)
    
    def _show_help(self, player: Player):
        """显示红包帮助"""
        from endstone import CustomForm
        form = CustomForm()
        form.title = self.plugin.get_text("redpacket.gui.help.title")
        
        help_text = self.plugin.get_text("redpacket.help.content")
        form.add_label(help_text)
        
        player.send_form(form)
    
    def _load_red_packets(self):
        """加载红包数据"""
        try:
            redpackets_path = os.path.join(self.plugin.data_folder, "red_packets.json")
            if os.path.exists(redpackets_path):
                with open(redpackets_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.red_packets = data.get("packets", {})
                    self.next_id = data.get("next_id", 1)
        except Exception as e:
            self.plugin.logger.error(f"加载红包数据失败: {e}")
            self.red_packets = {}
            self.next_id = 1
    
    def _save_red_packets(self):
        """保存红包数据"""
        try:
            redpackets_path = os.path.join(self.plugin.data_folder, "red_packets.json")
            os.makedirs(os.path.dirname(redpackets_path), exist_ok=True)
            
            data = {
                "packets": self.red_packets,
                "next_id": self.next_id
            }
            
            with open(redpackets_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.plugin.logger.error(f"保存红包数据失败: {e}")
