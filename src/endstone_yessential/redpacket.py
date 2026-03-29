import json
import os
import time
import random
import threading
from typing import Dict, List, Any, Optional
from endstone import Player
from endstone.form import ActionForm, CustomForm

class RedpacketDB:
    def __init__(self, plugin):
        self.plugin = plugin
        self.data_path = "./plugins/YEssential/data/Redpacketdata/Redpacket.json"
        self.data: Dict[str, Any] = {"nextId": 1, "packets": {}}
        self.ensure_directory()
        self.load()

    def ensure_directory(self):
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)

    def load(self):
        try:
            if os.path.exists(self.data_path):
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                    if "packets" not in self.data:
                        self.data["packets"] = {}
                    if "nextId" not in self.data:
                        self.data["nextId"] = 1
        except Exception as e:
            self.plugin.logger.error(f"[红包] 数据加载失败: {e}")
            self.data = {"nextId": 1, "packets": {}}

    def save(self):
        try:
            self.ensure_directory()
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.plugin.logger.error(f"[红包] 数据保存失败: {e}")

    def get_packet(self, packet_id: str):
        return self.data["packets"].get(packet_id)

    def set_packet(self, packet_id: str, packet: dict):
        self.data["packets"][packet_id] = packet
        self.save()

    def del_packet(self, packet_id: str):
        if packet_id in self.data["packets"]:
            del self.data["packets"][packet_id]
            self.save()

    def all_packets(self) -> Dict[str, dict]:
        return self.data["packets"]

    def next_id(self) -> int:
        packet_id = self.data["nextId"]
        self.data["nextId"] += 1
        self.save()
        return packet_id


class RedpacketEconomy:
    def __init__(self, plugin):
        self.plugin = plugin
        self.coin_name = "金币"

    def get(self, player: Player) -> float:
        if hasattr(self.plugin, 'economy') and self.plugin.economy:
            return self.plugin.economy.get_money(player.name)
        return 0.0

    def add(self, player: Player, amount: float):
        if hasattr(self.plugin, 'economy') and self.plugin.economy:
            self.plugin.economy.add_money(player.name, amount)

    def reduce(self, player: Player, amount: float) -> bool:
        if hasattr(self.plugin, 'economy') and self.plugin.economy:
            return self.plugin.economy.reduce_money(player.name, amount)
        return False

    def add_offline(self, name: str, amount: float):
        if hasattr(self.plugin, 'economy') and self.plugin.economy:
            self.plugin.economy.add_money(name, amount)


class RedpacketSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.db = RedpacketDB(plugin)
        self.economy = RedpacketEconomy(plugin)
        self.info_prefix = "§l§6[-YEST-] §r"
        self.expiry_queue: List[Dict] = []
        self.init_expiry_queue()
        self.start_expiry_checker()

    def init_expiry_queue(self):
        for packet in self.db.all_packets().values():
            if packet.get("remaining", 0) > 0:
                self.expiry_queue.append({
                    "id": str(packet["id"]),
                    "expireAt": packet.get("expireAt", 0)
                })
        self.expiry_queue.sort(key=lambda x: x["expireAt"])

    def start_expiry_checker(self):
        def check():
            while True:
                time.sleep(30)
                now = int(time.time() * 1000)
                while self.expiry_queue and self.expiry_queue[0]["expireAt"] <= now:
                    item = self.expiry_queue.pop(0)
                    packet = self.db.get_packet(item["id"])
                    if packet and packet.get("expireAt", 0) <= now:
                        self.expire_packet(packet)

                for pid, packet in list(self.db.all_packets().items()):
                    if packet.get("remaining", 0) > 0 and packet.get("remainingAmount", 0) < packet.get("remaining", 1):
                        self.expire_packet(packet)

        thread = threading.Thread(target=check, daemon=True)
        thread.start()

    def is_enabled(self) -> bool:
        config = self.plugin.config_manager.get_config()
        return config.get("RedPacket", {}).get("EnabledModule", False)

    def get_config(self) -> dict:
        config = self.plugin.config_manager.get_config()
        return config.get("RedPacket", {})

    def calc_random(self, remaining: int, remaining_amount: int) -> int:
        if remaining == 1:
            return remaining_amount
        safe_max = remaining_amount - (remaining - 1)
        if safe_max <= 1:
            return 1
        max_amt = min(int((remaining_amount / remaining) * 2), safe_max)
        return max(1, random.randint(1, max_amt))

    def expire_packet(self, packet: dict):
        if not packet:
            return

        if packet.get("remainingAmount", 0) > 0:
            refund = packet["remainingAmount"]
            sender = packet.get("sender", "")
            if sender:
                self.economy.add_offline(sender, refund)

        self.db.del_packet(str(packet.get("id", "")))

    def send_redpacket(self, player: Player, amount: int, count: int, target_player: str = "", message: str = "", packet_type: str = "random") -> bool:
        if not self.is_enabled():
            player.send_message(self.info_prefix + "§c该模块未启用")
            return False

        cfg = self.get_config()
        if not cfg:
            player.send_message(self.info_prefix + "§c该模块未启用")
            return False

        max_amount = cfg.get("maxAmount", 10000)
        max_count = cfg.get("maxCount", 100)
        min_amount = cfg.get("minAmount", 1)
        expire_time = cfg.get("expireTime", 300)

        if amount < min_amount or amount > max_amount:
            player.send_message(self.info_prefix + f"§c总金额需在 {min_amount}~{max_amount} 之间")
            return False

        if count < 1 or count > max_count:
            player.send_message(self.info_prefix + f"§c个数需在 1~{max_count} 之间")
            return False

        if amount < count:
            player.send_message(self.info_prefix + f"§c总金额({amount})不能少于红包个数({count})")
            return False

        balance = self.economy.get(player)
        if balance < amount:
            player.send_message(self.info_prefix + "§c余额不足")
            return False

        self.economy.reduce(player, amount)

        packet_id = self.db.next_id()
        is_specific = bool(target_player and target_player.strip())

        packet = {
            "id": packet_id,
            "sender": player.name,
            "amount": amount,
            "count": count,
            "remaining": count,
            "remainingAmount": amount,
            "recipients": [],
            "targetType": "specific" if is_specific else "all",
            "targetPlayer": (target_player or "").strip(),
            "message": message or f"{player.name} 发来一个红包",
            "packetType": "average" if packet_type == "average" else "random",
            "createdAt": int(time.time() * 1000),
            "expireAt": int(time.time() * 1000) + (expire_time * 1000)
        }

        self.db.set_packet(str(packet_id), packet)
        self.expiry_queue.append({"id": str(packet_id), "expireAt": packet["expireAt"]})
        self.expiry_queue.sort(key=lambda x: x["expireAt"])

        type_name = "拼手气" if packet_type == "random" else "普通"

        if is_specific:
            target = self.plugin.server.get_player(packet["targetPlayer"])
            if target:
                target.send_message(self.info_prefix + f"{player.name} 给你发了一个{type_name}红包！")
            player.send_message(self.info_prefix + f"已向 {packet['targetPlayer']} 发送 {type_name}红包：{amount} × {count}")
        else:
            self.plugin.server.broadcast_message(
                self.info_prefix + f"{player.name} 发了一个{type_name}红包，快来抢！"
            )
            player.send_message(self.info_prefix + f"{type_name}红包发送成功：{amount} × {count}")

        return True

    def open_redpacket(self, player: Player) -> bool:
        now = int(time.time() * 1000)
        available = []

        for packet in self.db.all_packets().values():
            if packet.get("expireAt", 0) <= now:
                self.expire_packet(packet)
                continue
            if packet.get("remainingAmount", 0) < packet.get("remaining", 1):
                self.expire_packet(packet)
                continue
            if packet.get("remaining", 0) <= 0:
                continue
            if player.name in packet.get("recipients", []):
                continue
            if packet.get("targetType") == "specific" and packet.get("targetPlayer", "").lower() != player.name.lower():
                continue
            available.append(packet)

        if not available:
            player.send_message(self.info_prefix + "§c当前没有可领取的红包")
            return False

        available.sort(key=lambda x: x.get("createdAt", 0))
        packet = available[0]

        amount = packet.get("remainingAmount", 0)
        if packet.get("packetType") == "average":
            amount = max(1, int(packet["remainingAmount"] / packet["remaining"]))
        else:
            amount = self.calc_random(packet["remaining"], packet["remainingAmount"])

        amount = max(1, min(amount, packet["remainingAmount"]))

        packet["remaining"] -= 1
        packet["remainingAmount"] -= amount
        packet["recipients"].append(player.name)

        if packet["remaining"] <= 0:
            self.db.del_packet(str(packet["id"]))
        else:
            self.db.set_packet(str(packet["id"]), packet)

        self.economy.add(player, amount)

        type_name = "拼手气" if packet.get("packetType") == "random" else "普通"
        player.send_message(
            self.info_prefix + f"恭喜你领取到 {packet['sender']} 的{type_name}红包，获得 {amount} 金币！"
        )

        sender = self.plugin.server.get_player(packet["sender"])
        if sender and sender.name != player.name:
            sender.send_message(
                self.info_prefix + f"{player.name} 领取了你的红包，获得 {amount} 金币"
            )

        return True

    def show_redpacket_list(self, player: Player):
        now = int(time.time() * 1000)
        available = []

        for packet in self.db.all_packets().values():
            if packet.get("expireAt", 0) <= now:
                continue
            if packet.get("remainingAmount", 0) < packet.get("remaining", 1):
                continue
            if packet.get("remaining", 0) <= 0:
                continue
            if player.name in packet.get("recipients", []):
                continue
            if packet.get("targetType") == "specific" and packet.get("targetPlayer", "").lower() != player.name.lower():
                continue
            available.append(packet)

        if not available:
            player.send_message(self.info_prefix + "§c暂无可领红包")
            return

        available.sort(key=lambda x: x.get("createdAt", 0))

        form = ActionForm(title="可领红包")
        form.content = "点击红包立即领取"

        for packet in available:
            sec = max(0, (packet.get("expireAt", 0) - now) // 1000)
            t_name = "§c拼手气" if packet.get("packetType") == "random" else "§a普通"
            btn_text = (
                f"{t_name} §f{packet['sender']}的红包\n"
                f"§7总额:§f{packet['amount']} 剩余:§a{packet['remaining']}/{packet['count']} 到期:§e{sec}s"
            )
            form.add_button(btn_text)

        def on_submit(p, selected):
            if selected is not None:
                self.open_redpacket(p)

        form.on_submit = on_submit
        player.send_form(form)

    def show_redpacket_history(self, player: Player):
        history = [
            p for p in self.db.all_packets().values()
            if p.get("sender") == player.name or player.name in p.get("recipients", [])
        ]

        if not history:
            player.send_message(self.info_prefix + "§c暂无红包历史")
            return

        history.sort(key=lambda x: x.get("createdAt", 0), reverse=True)

        form = ActionForm(title="红包历史")
        form.content = "最近 10 条"

        for packet in history[:10]:
            is_sender = packet.get("sender") == player.name
            role = "§a已发" if is_sender else "§b已领"
            type_tag = "[拼手气]" if packet.get("packetType") == "random" else "[普通]"
            status = "§a进行中" if packet.get("remaining", 0) > 0 else "§7已结束"
            btn_text = (
                f"§l{role}{type_tag} §e{packet['sender']}的红包\n"
                f"§7总额:§f{packet['amount']} 状态:{status}"
            )
            form.add_button(btn_text)

        def on_submit(p, selected):
            pass

        form.on_submit = on_submit
        player.send_form(form)

    def show_help(self, player: Player):
        form = ActionForm(title="红包帮助")
        form.content = "选择查看详情:"
        form.add_button("发送红包")
        form.add_button("领取红包")
        form.add_button("红包列表")
        form.add_button("红包历史")

        def on_submit(p, selected):
            if selected == 0:
                p.send_message(self.info_prefix + "§a用法: /rp send <金额> <个数> [玩家] [留言]")
            elif selected == 1:
                p.send_message(self.info_prefix + "§a用法: /rp open 领取红包")
            elif selected == 2:
                self.show_redpacket_list(p)
            elif selected == 3:
                self.show_redpacket_history(p)

        form.on_submit = on_submit
        player.send_form(form)

    def on_command(self, player: Player, args: List[str]) -> bool:
        if not args:
            self.show_redpacket_list(player)
            return True

        sub = args[0].lower()

        if sub == "send":
            if len(args) < 3:
                player.send_message(self.info_prefix + "§c用法: /rp send <金额> <个数> [玩家] [留言]")
                return True
            try:
                amount = int(args[1])
                count = int(args[2])
                target = args[3] if len(args) > 3 else ""
                message = args[4] if len(args) > 4 else ""
                self.send_redpacket(player, amount, count, target, message)
            except ValueError:
                player.send_message(self.info_prefix + "§c金额和个数必须是数字")
            return True

        elif sub == "open":
            self.open_redpacket(player)
            return True

        elif sub == "list":
            self.show_redpacket_list(player)
            return True

        elif sub == "history":
            self.show_redpacket_history(player)
            return True

        elif sub == "help":
            self.show_help(player)
            return True

        return False
