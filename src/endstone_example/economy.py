import json
import os
import time
from typing import Dict, List, Optional
from endstone import Player, CommandSender

class EconomySystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.server = plugin.server
        self.money_data = {}
        self.money_history = {}
        self.ranking_data = {}
        
    def init_player_economy(self, player: Player):
        """初始化玩家经济数据"""
        if self.plugin.config_manager.get("Economy.system") == "scoreboard":
            scoreboard = self.plugin.config_manager.get("Economy.scoreboard_name", "money")
            if player.get_score(scoreboard) is None:
                player.set_score(scoreboard, 0)
        # 如果是LLMoney，通常会自动初始化
    
    def get_balance(self, player: Player) -> float:
        """获取玩家余额"""
        if self.plugin.config_manager.get("Economy.system") == "scoreboard":
            scoreboard = self.plugin.config_manager.get("Economy.scoreboard_name", "money")
            return player.get_score(scoreboard) or 0
        else:
            # 使用LLMoney
            return getattr(player, 'get_money', lambda: 0)()
    
    def set_balance(self, player: Player, amount: float):
        """设置玩家余额"""
        if self.plugin.config_manager.get("Economy.system") == "scoreboard":
            scoreboard = self.plugin.config_manager.get("Economy.scoreboard_name", "money")
            player.set_score(scoreboard, int(amount))
        else:
            # 使用LLMoney
            if hasattr(player, 'set_money'):
                player.set_money(amount)
    
    def add_balance(self, player: Player, amount: float):
        """增加玩家余额"""
        current = self.get_balance(player)
        self.set_balance(player, current + amount)
        self._record_history(player, "add", amount, current + amount)
    
    def reduce_balance(self, player: Player, amount: float) -> bool:
        """减少玩家余额"""
        current = self.get_balance(player)
        if current < amount:
            return False
        
        self.set_balance(player, current - amount)
        self._record_history(player, "reduce", amount, current - amount)
        return True
    
    def transfer_money(self, from_player: Player, to_player: Player, amount: float, note: str = "") -> bool:
        """转账"""
        if not self.reduce_balance(from_player, amount):
            return False
        
        tax_rate = self.plugin.config_manager.get("Economy.PayTaxRate", 0)
        tax = amount * tax_rate / 100
        actual_amount = amount - tax
        
        self.add_balance(to_player, actual_amount)
        
        # 记录历史
        self._record_history(from_player, "transfer_out", amount, self.get_balance(from_player), f"to:{to_player.name},{note}")
        self._record_history(to_player, "transfer_in", actual_amount, self.get_balance(to_player), f"from:{from_player.name},{note}")
        
        # 发送消息
        from_player.send_message(self.plugin.get_text("economy.transfer.success", amount=actual_amount, tax=tax))
        to_player.send_message(self.plugin.get_text("economy.transfer.received", player=from_player.name, amount=actual_amount))
        
        return True
    
    def _record_history(self, player: Player, action: str, amount: float, balance: float, note: str = ""):
        """记录经济历史"""
        if player.name not in self.money_history:
            self.money_history[player.name] = []
        
        record = {
            "time": time.time(),
            "action": action,
            "amount": amount,
            "balance": balance,
            "note": note
        }
        
        self.money_history[player.name].append(record)
        
        # 只保留最近50条记录
        if len(self.money_history[player.name]) > 50:
            self.money_history[player.name] = self.money_history[player.name][-50:]
    
    def get_history(self, player: Player, limit: int = 10) -> List[Dict]:
        """获取经济历史"""
        return self.money_history.get(player.name, [])[-limit:]
    
    def sync_economy_data(self):
        """同步经济数据到排行榜"""
        if not self.plugin.config_manager.get("Economy.ranking_enabled", True):
            return
        
        for player in self.server.get_online_players():
            balance = self.get_balance(player)
            self.ranking_data[player.name] = balance
        
        # 保存排行榜数据
        self._save_ranking_data()
    
    def _save_ranking_data(self):
        """保存排行榜数据"""
        ranking_path = os.path.join(self.plugin.data_folder, "economy_ranking.json")
        try:
            with open(ranking_path, 'w', encoding='utf-8') as f:
                json.dump(self.ranking_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.plugin.logger.error(f"保存排行榜数据失败: {e}")
    
    def get_ranking(self, limit: int = 50) -> List[tuple]:
        """获取财富排行榜"""
        sorted_ranking = sorted(self.ranking_data.items(), key=lambda x: x[1], reverse=True)
        return sorted_ranking[:limit]
    
    def open_money_gui(self, player: Player):
        """打开经济系统GUI"""
        from endstone import SimpleForm, CustomForm
        
        form = SimpleForm()
        form.title = self.plugin.get_text("economy.title")
        form.content = self.plugin.get_text("economy.balance", balance=self.get_balance(player))
        
        form.add_button(self.plugin.get_text("economy.query"), callback=lambda p, _: self._show_balance(p))
        form.add_button(self.plugin.get_text("economy.transfer"), callback=lambda p, _: self._open_transfer_gui(p))
        form.add_button(self.plugin.get_text("economy.history"), callback=lambda p, _: self._show_history(p))
        form.add_button(self.plugin.get_text("economy.ranking"), callback=lambda p, _: self._show_ranking(p))
        
        if self.plugin.config_manager.get("RedPacket.enabled", False):
            form.add_button(self.plugin.get_text("redpacket.menu"), callback=lambda p, _: self.plugin.redpacket.open_redpacket_gui(p))
        
        player.send_form(form)
    
    def _show_balance(self, player: Player):
        """显示余额"""
        balance = self.get_balance(player)
        player.send_message(self.plugin.get_text("economy.balance", balance=balance))
    
    def _open_transfer_gui(self, player: Player):
        """打开转账GUI"""
        from endstone import CustomForm
        
        online_players = [p for p in self.server.get_online_players() if p != player]
        
        form = CustomForm()
        form.title = self.plugin.get_text("economy.transfer.title")
        
        form.add_label(self.plugin.get_text("economy.transfer.tax", rate=self.plugin.config_manager.get("Economy.PayTaxRate", 0)))
        form.add_label(self.plugin.get_text("economy.balance", balance=self.get_balance(player)))
        
        if online_players:
            player_names = [p.name for p in online_players]
            form.add_dropdown(self.plugin.get_text("economy.transfer.select"), player_names)
        else:
            form.add_label(self.plugin.get_text("economy.transfer.no_players"))
            player.send_form(form)
            return
        
        form.add_input(self.plugin.get_text("economy.transfer.amount"), "100")
        form.add_input(self.plugin.get_text("economy.transfer.note"), "")
        
        def callback(p, data):
            if not data:
                return
            
            target_index = data[2]
            amount_str = data[3]
            note = data[4]
            
            try:
                amount = float(amount_str)
                if amount <= 0:
                    p.send_message(self.plugin.get_text("economy.transfer.invalid_amount"))
                    return
                
                target_player = online_players[target_index]
                if self.transfer_money(p, target_player, amount, note):
                    p.send_message(self.plugin.get_text("success"))
                else:
                    p.send_message(self.plugin.get_text("economy.transfer.failed"))
                    
            except (ValueError, IndexError):
                p.send_message(self.plugin.get_text("economy.transfer.invalid_amount"))
        
        player.send_form(form, callback)
    
    def _show_history(self, player: Player):
        """显示经济历史"""
        history = self.get_history(player, 20)
        
        if not history:
            player.send_message(self.plugin.get_text("economy.history.empty"))
            return
        
        from endstone import SimpleForm
        form = SimpleForm()
        form.title = self.plugin.get_text("economy.history.title")
        
        content = ""
        for record in reversed(history):
            time_str = time.strftime("%H:%M:%S", time.localtime(record["time"]))
            content += f"{time_str} {record['action']}: {record['amount']} -> {record['balance']}\n"
            if record["note"]:
                content += f"  {record['note']}\n"
        
        form.content = content
        player.send_form(form)
    
    def _show_ranking(self, player: Player):
        """显示财富排行榜"""
        ranking = self.get_ranking(20)
        
        if not ranking:
            player.send_message(self.plugin.get_text("economy.ranking.empty"))
            return
        
        from endstone import SimpleForm
        form = SimpleForm()
        form.title = self.plugin.get_text("economy.ranking.title")
        
        content = ""
        for i, (name, balance) in enumerate(ranking, 1):
            content += f"§6{i}. §e{name}: §a{balance}\n"
        
        form.content = content
        player.send_form(form)
    
    def open_op_money_gui(self, player: Player):
        """打开OP经济管理GUI"""
        from endstone import SimpleForm
        
        form = SimpleForm()
        form.title = self.plugin.get_text("economy.op.title")
        
        form.add_button(self.plugin.get_text("economy.op.add"), callback=lambda p, _: self._open_op_add_gui(p))
        form.add_button(self.plugin.get_text("economy.op.remove"), callback=lambda p, _: self._open_op_remove_gui(p))
        form.add_button(self.plugin.get_text("economy.op.set"), callback=lambda p, _: self._open_op_set_gui(p))
        form.add_button(self.plugin.get_text("economy.op.view"), callback=lambda p, _: self._open_op_view_gui(p))
        form.add_button(self.plugin.get_text("economy.op.history"), callback=lambda p, _: self._open_op_history_gui(p))
        form.add_button(self.plugin.get_text("economy.ranking"), callback=lambda p, _: self._show_ranking(p))
        
        player.send_form(form)
    
    def _open_op_add_gui(self, player: Player):
        """打开OP增加余额GUI"""
        self._open_op_amount_gui(player, "add")
    
    def _open_op_remove_gui(self, player: Player):
        """打开OP减少余额GUI"""
        self._open_op_amount_gui(player, "remove")
    
    def _open_op_set_gui(self, player: Player):
        """打开OP设置余额GUI"""
        self._open_op_amount_gui(player, "set")
    
    def _open_op_amount_gui(self, player: Player, action: str):
        """打开OP金额操作GUI"""
        from endstone import CustomForm
        
        online_players = [p for p in self.server.get_online_players()]
        
        form = CustomForm()
        form.title = self.plugin.get_text(f"economy.op.{action}.title")
        
        if online_players:
            player_names = [p.name for p in online_players]
            form.add_dropdown(self.plugin.get_text("economy.op.select_player"), player_names)
        else:
            form.add_label(self.plugin.get_text("economy.transfer.no_players"))
            player.send_form(form)
            return
        
        form.add_input(self.plugin.get_text(f"economy.op.{action}.amount"), "100")
        
        def callback(p, data):
            if not data:
                return
            
            target_index = data[0]
            amount_str = data[1]
            
            try:
                amount = float(amount_str)
                if amount <= 0:
                    p.send_message(self.plugin.get_text("economy.transfer.invalid_amount"))
                    return
                
                target_player = online_players[target_index]
                
                if action == "add":
                    self.add_balance(target_player, amount)
                    p.send_message(self.plugin.get_text("success"))
                elif action == "remove":
                    if self.reduce_balance(target_player, amount):
                        p.send_message(self.plugin.get_text("success"))
                    else:
                        p.send_message(self.plugin.get_text("economy.no.enough"))
                elif action == "set":
                    self.set_balance(target_player, amount)
                    p.send_message(self.plugin.get_text("success"))
                
                # 显示操作后余额
                new_balance = self.get_balance(target_player)
                p.send_message(self.plugin.get_text("economy.balance", balance=new_balance))
                
            except (ValueError, IndexError):
                p.send_message(self.plugin.get_text("economy.transfer.invalid_amount"))
        
        player.send_form(form, callback)
    
    def _open_op_view_gui(self, player: Player):
        """打开OP查看余额GUI"""
        from endstone import CustomForm
        
        online_players = [p for p in self.server.get_online_players()]
        
        form = CustomForm()
        form.title = self.plugin.get_text("economy.op.view.title")
        
        if online_players:
            player_names = [p.name for p in online_players]
            form.add_dropdown(self.plugin.get_text("economy.op.select_player"), player_names)
        else:
            form.add_label(self.plugin.get_text("economy.transfer.no_players"))
            player.send_form(form)
            return
        
        def callback(p, data):
            if not data:
                return
            
            target_index = data[0]
            target_player = online_players[target_index]
            balance = self.get_balance(target_player)
            
            p.send_message(self.plugin.get_text("economy.op.view.result", player=target_player.name, balance=balance))
        
        player.send_form(form, callback)
    
    def _open_op_history_gui(self, player: Player):
        """打开OP查看历史GUI"""
        from endstone import CustomForm
        
        online_players = [p for p in self.server.get_online_players()]
        
        form = CustomForm()
        form.title = self.plugin.get_text("economy.op.history.title")
        
        if online_players:
            player_names = [p.name for p in online_players]
            form.add_dropdown(self.plugin.get_text("economy.op.select_player"), player_names)
        else:
            form.add_label(self.plugin.get_text("economy.transfer.no_players"))
            player.send_form(form)
            return
        
        def callback(p, data):
            if not data:
                return
            
            target_index = data[0]
            target_player = online_players[target_index]
            
            # 显示目标玩家的历史
            self._show_op_history(p, target_player)
        
        player.send_form(form, callback)
    
    def _show_op_history(self, player: Player, target: Player):
        """显示OP视角的历史记录"""
        history = self.get_history(target, 50)
        
        if not history:
            player.send_message(self.plugin.get_text("economy.history.empty"))
            return
        
        from endstone import SimpleForm
        form = SimpleForm()
        form.title = self.plugin.get_text("economy.op.history.view", player=target.name)
        
        content = ""
        for record in reversed(history):
            time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record["time"]))
            content += f"{time_str} {record['action']}: {record['amount']} -> {record['balance']}\n"
            if record["note"]:
                content += f"  {record['note']}\n"
        
        form.content = content
        player.send_form(form)
    
    def get_player_economy_data(self, player: Player) -> Dict:
        """获取玩家经济数据（用于保存）"""
        return {
            "balance": self.get_balance(player),
            "history": self.money_history.get(player.name, [])[-10:]  # 只保存最近10条
        }
