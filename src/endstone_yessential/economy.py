"""
YEssential Economy System - 完整经济系统
支持双模式(计分板/LLMoney), 转账, 历史, 排行榜, 税率, 离线缓存, 通知
全 i18n 支持
"""
import os, json, time
from typing import Dict, List, Any
from endstone import Player
from endstone.form import ActionForm, ModalForm, MessageForm, Dropdown, TextInput, Label
from endstone.command import CommandSenderWrapper
from .i18n import tr as _tr
from .log import plugin_print

def tr(key: str, *args) -> str:
    return _tr(key, *args)


class EconomyConfig:
    def __init__(self, plugin):
        self.plugin = plugin
    def _get(self): return self.plugin.config_manager.config_data.get("Economy", {})
    @property
    def mode(self): return self._get().get("mode", "scoreboard")
    @property
    def is_scoreboard(self): return self.mode != "llmoney"
    @property
    def scoreboard_name(self): return self._get().get("Scoreboard", "money")
    @property
    def coin_name(self): return self._get().get("CoinName", tr("economy.coin"))
    @property
    def ranking_model(self): return self._get().get("RankingModel", "New")
    @property
    def pay_tax_rate(self): return self._get().get("PayTaxRate", 0)


class OfflineMoneyCache:
    def __init__(self, data_folder: str):
        self.path = os.path.join(data_folder, "offline_money.json")
        self._data: Dict[str, List[dict]] = {}
        self.load()
    def load(self):
        try:
            if os.path.exists(self.path):
                with open(self.path, 'r', encoding='utf-8') as f: self._data = json.load(f)
        except: self._data = {}
    def save(self):
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, 'w', encoding='utf-8') as f: json.dump(self._data, f, indent=2, ensure_ascii=False)
        except: pass
    def add(self, name: str, op_type: str, amount: int, note: str = ""):
        if name not in self._data: self._data[name] = []
        self._data[name].append({"type": op_type, "amount": amount, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "note": note})
        self.save()
    def get(self, name: str): return self._data.get(name, [])
    def clear(self, name: str):
        if name in self._data: del self._data[name]; self.save()
    def apply(self, player: Player, economy):
        ops = self.get(player.name)
        if not ops: return
        for op in ops:
            if op["type"] == "add": economy.add_money_internal(player, op["amount"])
            elif op["type"] == "reduce": economy.reduce_money_internal(player, op["amount"])
            elif op["type"] == "set": economy.set_money_internal(player, op["amount"])
        self.clear(player.name)


class EconomyNotify:
    def __init__(self, data_folder: str):
        self.path = os.path.join(data_folder, "offline_notify.json")
        self._data: Dict[str, List[str]] = {}
        self.load()
    def load(self):
        try:
            if os.path.exists(self.path):
                with open(self.path, 'r', encoding='utf-8') as f: self._data = json.load(f)
        except: self._data = {}
    def save(self):
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, 'w', encoding='utf-8') as f: json.dump(self._data, f, indent=2, ensure_ascii=False)
        except: pass
    def send(self, p, msg: str):
        if isinstance(p, Player): p.send_message(msg)
        else:
            name = str(p)
            if EconomyNotify._server:
                online = EconomyNotify._server.get_player(name)
                if online: online.send_message(msg); return
            self._data.setdefault(name, []).append(msg); self.save()
    def apply(self, player: Player):
        msgs = self._data.pop(player.name, [])
        if msgs: self.save(); [player.send_message(m) for m in msgs]
EconomyNotify._server = None


class MoneyHistory:
    def __init__(self, data_folder: str):
        self.path = os.path.join(data_folder, "money_history.json")
        self._data: Dict[str, Dict[str, str]] = {}
        self.load()
    def load(self):
        try:
            if os.path.exists(self.path):
                with open(self.path, 'r', encoding='utf-8') as f: self._data = json.load(f)
        except: self._data = {}
    def save(self):
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, 'w', encoding='utf-8') as f: json.dump(self._data, f, indent=2, ensure_ascii=False)
        except: pass
    def add(self, name: str, msg: str):
        key = f"{time.strftime('%Y-%m-%d %H:%M:%S')}-{int(time.time()*1000)%1000:03d}"
        self._data.setdefault(name, {})[key] = msg; self.save()
    def get_recent(self, name: str, n=50):
        entries = list(self._data.get(name, {}).items())
        entries.sort(key=lambda x: x[0], reverse=True)
        return entries[:n]


class MoneyRanking:
    def __init__(self, data_folder: str):
        self.path = os.path.join(data_folder, "money_ranking.json")
        self._cache: Dict[str, float] = {}
        self._dirty = False; self.load()
    def load(self):
        try:
            if os.path.exists(self.path):
                with open(self.path, 'r', encoding='utf-8') as f: self._cache = json.load(f)
        except: self._cache = {}
    def save(self):
        try:
            with open(self.path, 'w', encoding='utf-8') as f: json.dump(self._cache, f, indent=2, ensure_ascii=False)
        except: pass
    def update(self, name, val):
        if self._cache.get(name) != val: self._cache[name] = val; self._dirty = True
    def batch_save(self):
        if self._dirty: self.save(); self._dirty = False
    def get_top(self, n=50):
        return sorted(self._cache.items(), key=lambda x: x[1], reverse=True)[:n]


class TaxCalculator:
    @staticmethod
    def calc(amount: int, balance: int, cfg) -> dict:
        if isinstance(cfg, (int, float)):
            r = float(cfg)
            return {"tax": int(amount*(r/100)), "rate": r, "tip": f"{r}%"} if r > 0 else {"tax": 0, "rate": 0, "tip": "0%"}
        if isinstance(cfg, list):
            for t in cfg:
                if balance >= t.get("min", 0) and (t.get("max", -1) == -1 or balance < t["max"]):
                    r = t.get("rate", 0); return {"tax": int(amount*(r/100)), "rate": r, "tip": f"{r}%"}
        return {"tax": 0, "rate": 0, "tip": "0%"}


class EconomySystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.config = EconomyConfig(plugin)
        self.data_folder = plugin.data_folder
        self.money_path = os.path.join(self.data_folder, "money.json")
        self.money_data: Dict[str, float] = {}
        self.offline_cache = OfflineMoneyCache(self.data_folder)
        self.notify = EconomyNotify(self.data_folder)
        self.history = MoneyHistory(self.data_folder)
        self.ranking = MoneyRanking(self.data_folder)
        EconomyNotify._server = plugin.server
        self.load_money()
        self._init_scoreboard()
        self._start_timers()

    def load_money(self):
        try:
            if os.path.exists(self.money_path):
                with open(self.money_path, 'r', encoding='utf-8') as f: self.money_data = json.load(f)
        except: self.money_data = {}
    def save_money(self):
        try:
            os.makedirs(os.path.dirname(self.money_path), exist_ok=True)
            with open(self.money_path, 'w', encoding='utf-8') as f: json.dump(self.money_data, f, indent=2, ensure_ascii=False)
        except: pass

    def _init_scoreboard(self):
        if not self.config.is_scoreboard: return
        sb = self.config.scoreboard_name
        try:
            sboard = self.plugin.server.scoreboard
            existing = [o.name for o in sboard.objectives] if sboard else []
            if sb not in existing:
                self.plugin.server.dispatch_command(CommandSenderWrapper(self.plugin.server.command_sender), f"scoreboard objectives add {sb} dummy")
        except: pass

    # ── 内部 API ──────────────────────────────────────────
    def get_money_internal(self, target):
        if isinstance(target, Player):
            if self.config.is_scoreboard:
                try:
                    for obj in target.scoreboard.objectives:
                        if obj.name == self.config.scoreboard_name: return float(obj.get_score(target).value)
                except: pass
                return 0.0
            return self.money_data.get(target.name, 0.0)
        return self.money_data.get(str(target), 0.0)

    def _cmd(self, cmd: str):
        self.plugin.server.dispatch_command(CommandSenderWrapper(self.plugin.server.command_sender), cmd)

    def _sb_set(self, p: Player, amt: float):
        self._cmd(f'scoreboard players set "{p.name}" {self.config.scoreboard_name} {int(amt)}')

    def add_money_internal(self, target, amount: float):
        name = target.name if isinstance(target, Player) else str(target)
        if isinstance(target, Player) and self.config.is_scoreboard:
            self._sb_set(target, self.get_money_internal(target) + amount)
        else: self.money_data[name] = self.money_data.get(name, 0.0) + amount; self.save_money()

    def reduce_money_internal(self, target, amount: float) -> bool:
        name = target.name if isinstance(target, Player) else str(target)
        cur = self.get_money_internal(target)
        if cur >= amount:
            if isinstance(target, Player) and self.config.is_scoreboard:
                self._sb_set(target, cur - amount)
            else: self.money_data[name] = cur - amount; self.save_money()
            return True
        return False

    def set_money_internal(self, target, amount: float):
        name = target.name if isinstance(target, Player) else str(target)
        if isinstance(target, Player) and self.config.is_scoreboard: self._sb_set(target, amount)
        else: self.money_data[name] = amount; self.save_money()

    # ── 公开 API ──────────────────────────────────────────
    def get_money(self, name: str) -> float:
        p = self.plugin.server.get_player(name)
        return self.get_money_internal(p) if p else self.money_data.get(name, 0.0)
    def add_money(self, name: str, amount: float):
        p = self.plugin.server.get_player(name)
        if p: self.add_money_internal(p, amount)
        else: self.money_data[name] = self.money_data.get(name, 0.0) + amount; self.save_money()
    def reduce_money(self, name: str, amount: float) -> bool:
        p = self.plugin.server.get_player(name)
        if p: return self.reduce_money_internal(p, amount) if self.get_money_internal(p) >= amount else False
        if self.money_data.get(name, 0.0) >= amount: self.money_data[name] -= amount; self.save_money(); return True
        return False
    def set_money(self, name: str, amount: float):
        p = self.plugin.server.get_player(name)
        if p: self.set_money_internal(p, amount)
        else: self.money_data[name] = amount; self.save_money()

    def on_player_join(self, player: Player):
        name = player.name
        if self.config.is_scoreboard:
            if self.get_money_internal(player) == 0 and name not in self.money_data: self._sb_set(player, 0)
        elif name not in self.money_data: self.money_data[name] = 0.0; self.save_money()
        self.offline_cache.apply(player, self)
        self.notify.apply(player)
        self.ranking.update(name, self.get_money_internal(player))

    def _start_timers(self):
        def sample():
            for p in self.plugin.server.online_players:
                if not p.name.endswith("_sp"):
                    try: self.ranking.update(p.name, float(self.get_money_internal(p)))
                    except: pass
        self.plugin.server.scheduler.run_task(self.plugin, sample, 600, 600)
        self.plugin.server.scheduler.run_task(self.plugin, self.ranking.batch_save, 1200, 1200)

    def _rp_enabled(self):
        return self.plugin.config_manager.config_data.get("RedPacket", {}).get("EnabledModule", False)

    def open_money_gui(self, player: Player):
        if player.is_op: self._gui_op(player)
        else: self._gui_player(player)

    def _gui_player(self, p: Player):
        coin = self.config.coin_name
        f = ActionForm(title=f"§6{coin}")
        f.add_button(f"§a{tr('economy.query', coin)}", icon="textures/ui/MCoin")
        f.add_button(f"§a{tr('economy.transfer', coin)}", icon="textures/ui/trade_icon")
        f.add_button(f"§a{tr('economy.transfer_offline')}", icon="textures/ui/FriendsDiversity")
        f.add_button(f"§a{tr('economy.history', coin)}", icon="textures/ui/book_addtextpage_default")
        f.add_button(f"§a{tr('economy.ranking', coin)}", icon="textures/ui/icon_book_writable")
        if self._rp_enabled(): f.add_button(f"§a{tr('economy.redpacket')}", icon="textures/ui/gift_square")
        def cb(_, idx):
            if idx is None: return
            rp = self._rp_enabled()
            if idx == 0: self._show_balance(p)
            elif idx == 1: self._transfer(p)
            elif idx == 2: self._offline_transfer(p)
            elif idx == 3: self._show_history(p, p.name)
            elif idx == 4: self._ranking(p)
            elif idx == 5 and rp and hasattr(self.plugin, 'redpacket'): self.plugin.redpacket.show_redpacket_list(p)
            else: self._gui_player(p)
        f.on_submit = cb; p.send_form(f)

    def _gui_op(self, p: Player):
        coin = self.config.coin_name
        f = ActionForm(title=f"§6(OP) {coin}")
        f.add_button(f"§a{tr('economy.admin_add', coin)}", icon="textures/ui/icon_best3")
        f.add_button(f"§a{tr('economy.admin_reduce', coin)}", icon="textures/ui/redX1")
        f.add_button(f"§a{tr('economy.admin_set', coin)}", icon="textures/ui/gear")
        f.add_button(f"§a{tr('economy.admin_offline')}", icon="textures/ui/FriendsDiversity")
        f.add_button(f"§a{tr('economy.admin_look', coin)}", icon="textures/ui/MCoin")
        f.add_button(f"§a{tr('economy.admin_history', coin)}", icon="textures/ui/book_addtextpage_default")
        f.add_button(f"§a{tr('economy.admin_ranking', coin)}", icon="textures/ui/icon_book_writable")
        if self._rp_enabled(): f.add_button(f"§a{tr('economy.redpacket')}", icon="textures/ui/gift_square")
        f.add_button(f"§a{tr('economy.player_menu')}", icon="textures/ui/icon_multiplayer")
        def cb(_, idx):
            if idx is None: return
            rp = self._rp_enabled()
            if idx == 0: self._op_select(p, "add", tr("economy.add_op"))
            elif idx == 1: self._op_select(p, "reduce", tr("economy.reduce_op"))
            elif idx == 2: self._op_select(p, "set", tr("economy.set_op"))
            elif idx == 3: self._op_offline(p)
            elif idx == 4: self._op_select(p, "get", tr("economy.admin_look", coin))
            elif idx == 5: self._op_select(p, "history", tr("economy.admin_history", coin))
            elif idx == 6: self._ranking(p)
            elif idx == 7 and rp and hasattr(self.plugin, 'redpacket'): self.plugin.redpacket.show_redpacket_list(p)
            elif idx == (8 if rp else 7): self._gui_player(p)
            else: self._gui_op(p)
        f.on_submit = cb; p.send_form(f)

    def _show_balance(self, p: Player):
        bal = int(self.get_money_internal(p))
        coin = self.config.coin_name
        f = ActionForm(title=f"§6{tr('economy.query', coin)}", content=tr("economy.balance", bal, coin))
        f.add_button(tr("economy.back_btn"))
        f.on_submit = lambda _, __: self._gui_player(p); p.send_form(f)

    def _transfer(self, p: Player):
        coin = self.config.coin_name
        my = int(self.get_money_internal(p))
        tax_cfg = self.config.pay_tax_rate
        ti = TaxCalculator.calc(0, my, tax_cfg)
        names = [pl.name for pl in self.plugin.server.online_players if pl.name != p.name and not pl.name.endswith("_sp")]
        if not names: p.send_message(tr("economy.no_online")); self._gui_player(p); return
        fm = ModalForm(title=tr("economy.transfer_title", coin), controls=[
            Label(text=tr("economy.balance", my, coin) + f"\n{tr("economy.tax_info", ti["tip"])}"),
            Dropdown(label=tr("economy.select_player"), options=names),
            TextInput(label=tr("economy.amount_label"), placeholder="100 / all", default_value=""),
            TextInput(label=tr("economy.note_label"), placeholder="", default_value="")
        ])
        def cb(_, data):
            if not data: self._gui_player(p); return
            data = json.loads(data) if isinstance(data, str) else data
            try:
                tname = names[int(data[0])]; amt_s = str(data[1]).strip().lower(); note = str(data[2]).strip()
                myb = int(self.get_money_internal(p))
                amt = myb if amt_s == "all" else (int(amt_s) if amt_s.isdigit() else 0)
                if amt <= 0: p.send_message(tr("economy.must_positive")); return
                tg = self.plugin.server.get_player(tname)
                if not tg: p.send_message(tr("economy.player_offline", tname)); return
                trs = TaxCalculator.calc(amt, myb, tax_cfg); tax = trs["tax"]; recv = amt - tax
                if recv <= 0: p.send_message(tr("economy.tax_too_high")); return
                if myb < amt: p.send_message(tr("economy.not_enough")); return
                def conf(cp, ok):
                    if ok and self.reduce_money_internal(cp, amt):
                        self.add_money_internal(tg, recv)
                        self.history.add(cp.name, f"→ {tname}: -{amt} {coin} (tax {tax})")
                        self.history.add(tname, f"← {cp.name}: +{recv} {coin}")
                        cp.send_message(tr("economy.send_success", amt, "→", tname))
                        tg.send_message(tr("economy.receive_from", cp.name, recv, coin)+(f" {tr('economy.transfer_note', note)}" if note else ""))
                        self.ranking.update(cp.name, self.get_money_internal(cp))
                        self.ranking.update(tname, self.get_money_internal(tg))
                    self._gui_player(cp)
                cfm = MessageForm(title=tr("economy.confirm_title"), content=f"§7→ §a{tname}\n§7{tr('economy.amount_label')}: §e{amt}\n§7Tax: §c{tax}\n§7→ §a{recv} {coin}"+(f"\n{tr('economy.transfer_note', note)}" if note else ""), button1=tr("economy.confirm_btn"), button2=tr("economy.cancel_btn"))
                cfm.on_submit = conf; p.send_form(cfm)
            except: self._gui_player(p)
        fm.on_submit = cb; p.send_form(fm)

    def _offline_transfer(self, p: Player):
        coin = self.config.coin_name; my = int(self.get_money_internal(p))
        tax_cfg = self.config.pay_tax_rate; ti = TaxCalculator.calc(0, my, tax_cfg)
        fm = ModalForm(title=tr("economy.confirm_offline_title"), controls=[
            Label(text=tr("economy.balance", my, coin)+f"\n{tr("economy.tax_info", ti["tip"])}"),
            TextInput(label=tr("economy.offline_target"), placeholder="Steve", default_value=""),
            TextInput(label=tr("economy.amount_label"), placeholder="100 / all", default_value=""),
            TextInput(label=tr("economy.note_label"), placeholder="", default_value="")
        ])
        def cb(_, data):
            if not data: self._gui_player(p); return
            data = json.loads(data) if isinstance(data, str) else data
            tname = str(data[0]).strip(); amt_s = str(data[1]).strip().lower(); note = str(data[2]).strip()
            if not tname: p.send_message(tr("economy.need_player_name")); return
            if tname == p.name: p.send_message(tr("economy.cannot_self")); return
            if self.plugin.server.get_player(tname): p.send_message(tr("economy.offline_target_online")); return
            myb = int(self.get_money_internal(p)); amt = myb if amt_s == "all" else (int(amt_s) if amt_s.isdigit() else 0)
            if amt <= 0: p.send_message(tr("economy.must_positive")); return
            trs = TaxCalculator.calc(amt, myb, tax_cfg); tax = trs["tax"]; recv = amt - tax
            if recv <= 0: p.send_message(tr("economy.tax_too_high")); return
            if myb < amt: p.send_message(tr("economy.not_enough")); return
            def conf(cp, ok):
                if ok and self.reduce_money_internal(cp, amt):
                    self.offline_cache.add(tname, "add", recv, note)
                    self.history.add(cp.name, f"→ {tname}(offline): -{amt} {coin}")
                    cp.send_message(f"§a{tr('economy.send_success', amt, '→', tname)}")
                    self.notify.send(tname, tr("economy.receive_from", cp.name, recv, coin))
                self._gui_player(cp)
            cfm = MessageForm(title=tr("economy.confirm_offline_title"), content=f"§7→ §c{tname}(offline)\n§7{tr('economy.amount_label')}: §e{amt}\n§7Tax: §c{tax}\n§7→ §a{recv} {coin}\n\n{tr('economy.offline_warn')}"+(f"\n{tr('economy.transfer_note', note)}" if note else ""), button1=tr("economy.confirm_btn2"), button2=tr("economy.cancel_btn"))
            cfm.on_submit = conf; p.send_form(cfm)
        fm.on_submit = cb; p.send_form(fm)

    def _show_history(self, p: Player, name: str):
        coin = self.config.coin_name; entries = self.history.get_recent(name, 50)
        content = "\n".join([f"§7[{k[:16]}]§r {v}" for k, v in entries]) if entries else tr("economy.no_history")
        f = ActionForm(title=tr("economy.history_title", name, coin), content=content)
        f.add_button(tr("economy.back_btn"))
        f.on_submit = lambda _, __: (self._gui_op(p) if p.is_op else self._gui_player(p)); p.send_form(f)

    def _ranking(self, p: Player):
        coin = self.config.coin_name; my = int(self.get_money_internal(p))
        top = self.ranking.get_top(50)
        if not top: p.send_message(tr("economy.no_ranking")); return
        total = sum(v for _, v in top)
        def fmt(amt):
            if amt >= 1e6: return f"{amt/1e6:.1f}M"
            if amt >= 1e3: return f"{amt/1e3:.1f}K"
            return str(int(amt))
        content_lines = [tr("economy.ranking_total", fmt(total)), tr("economy.ranking_yours", fmt(my)), "§8"+"═"*20]
        f = ActionForm(title=tr("economy.ranking_title", len(top)), content="\n".join(content_lines))
        for i, (n, b) in enumerate(top):
            r = i+1; pfx = ["§b☆","§c◆","§a▣"][min(2,r-1)]
            entry = f"§e[Me] {n}" if n == p.name else n
            pct = (b/total*100) if total > 0 else 0
            f.add_button(f"{pfx} §l{r}. §r{entry}\n§c├: {fmt(b)} §a{pct:.1f}%")
        f.add_button(tr("economy.back_btn"))
        f.on_submit = lambda _, __: self.open_money_gui(p); p.send_form(f)

    def _op_select(self, admin: Player, op: str, label: str):
        names = [pl.name for pl in self.plugin.server.online_players if not pl.name.endswith("_sp")]
        pls = [pl for pl in self.plugin.server.online_players if not pl.name.endswith("_sp")]
        if not names: admin.send_message(tr("economy.no_online")); self._gui_op(admin); return
        if op in ("get", "history"):
            f = ActionForm(title=f"§6{label}")
            for n in names: f.add_button(f"§a{n}")
            def cb(_, idx):
                if idx is None: self._gui_op(admin); return
                t = pls[idx]
                if op == "get":
                    admin.send_message(tr("economy.player_balance", t.name, int(self.get_money_internal(t))))
                else: self._show_history(admin, t.name)
                self._gui_op(admin)
            f.on_submit = cb; admin.send_form(f)
        else:
            fm = ModalForm(title=f"§6{label}", controls=[Dropdown(label=tr("economy.select_player"), options=names), TextInput(label=tr("economy.amount_label"), placeholder="0", default_value="")])
            def cb(_, data):
                if not data: self._gui_op(admin); return
                data = json.loads(data) if isinstance(data, str) else data
                t = pls[int(data[0])]; amt_s = str(data[1]).strip()
                if not amt_s.isdigit(): admin.send_message(tr("economy.need_valid_number")); return
                amt = int(amt_s)
                if op != "set" and amt <= 0: admin.send_message(tr("economy.must_positive")); return
                if op == "set" and amt < 0: admin.send_message(tr("economy.must_nonneg")); return
                coin = self.config.coin_name
                if op == "add": self.add_money_internal(t, amt); admin.send_message(tr("economy.admin_give", t.name, amt, coin)); self.history.add(t.name, f"admin +{amt}"); t.send_message(tr("economy.admin_give", t.name, amt, coin))
                elif op == "reduce":
                    if self.reduce_money_internal(t, amt): admin.send_message(tr("economy.admin_take", t.name, amt, coin)); self.history.add(t.name, f"admin -{amt}"); t.send_message(tr("economy.admin_take", t.name, amt, coin))
                    else: admin.send_message(tr("economy.not_enough"))
                elif op == "set": self.set_money_internal(t, amt); admin.send_message(tr("economy.admin_set_to", t.name, coin, amt)); self.history.add(t.name, f"admin ={amt}"); t.send_message(tr("economy.admin_set_to", t.name, coin, amt))
                self.ranking.update(t.name, self.get_money_internal(t)); self._gui_op(admin)
            fm.on_submit = cb; admin.send_form(fm)

    def _op_offline(self, admin: Player):
        coin = self.config.coin_name
        fm = ModalForm(title=tr("economy.confirm_admin_title"), controls=[
            TextInput(label=tr("economy.offline_target"), placeholder="Steve", default_value=""),
            Dropdown(label=tr("economy.op_type_label"), options=[tr("economy.add_op"), tr("economy.reduce_op"), tr("economy.set_op")]),
            TextInput(label=tr("economy.amount_label"), placeholder="0", default_value=""),
            TextInput(label=tr("economy.note_label"), placeholder="", default_value="")
        ])
        def cb(_, data):
            if not data: self._gui_op(admin); return
            data = json.loads(data) if isinstance(data, str) else data
            tname = str(data[0]).strip(); op_idx = int(data[1]); amt_s = str(data[2]).strip(); note = str(data[3]).strip()
            if not tname: admin.send_message(tr("economy.need_player_name")); return
            if not amt_s.isdigit(): admin.send_message(tr("economy.need_valid_number")); return
            amt = int(amt_s)
            ops = ["add","reduce","set"]; op = ops[op_idx]
            if op != "set" and amt <= 0: admin.send_message(tr("economy.must_positive")); return
            if self.plugin.server.get_player(tname): admin.send_message(tr("economy.offline_target_online")); return
            def conf(cp, ok):
                if ok:
                    self.offline_cache.add(tname, op, amt, note)
                    self.history.add(tname, f"admin({cp.name}) {op}: {amt} {coin}")
                    cp.send_message(f"§a{tr('economy.offline_cached', tname)}")
                self._gui_op(cp)
            cfm = MessageForm(title=tr("economy.confirm_admin_title"), content=f"§7→ §c{tname}(offline)\n§7{tr('economy.op_type_label')}: §e{op}\n§7{tr('economy.amount_label')}: §e{amt} {coin}"+(f"\n{tr('economy.transfer_note', note)}" if note else ""), button1=tr("economy.confirm_btn2"), button2=tr("economy.cancel_btn"))
            cfm.on_submit = conf; admin.send_form(cfm)
        fm.on_submit = cb; admin.send_form(fm)

    def handle_moneys_command(self, sender, args: list) -> bool:
        coin = self.config.coin_name
        if len(args) < 2: sender.send_message(f"§c/moneys <add|del|set|get|history> <player> [amount]"); return True
        op = args[0].lower(); tname = args[1]
        tg = self.plugin.server.get_player(tname)
        if op == "get":
            bal = self.get_money(tname); sender.send_message(tr("economy.player_balance", tname, int(bal))); return True
        if op == "history":
            if isinstance(sender, Player): self._show_history(sender, tname)
            else:
                for k, v in self.history.get_recent(tname, 10): sender.send_message(f"  [{k[:16]}] {v}")
            return True
        if len(args) < 3: sender.send_message(f"§c/moneys {op} <player> <amount>"); return True
        try: amt = int(args[2])
        except: sender.send_message(tr("economy.need_number")); return True
        if op == "add":
            if tg: self.add_money_internal(tg, amt); sender.send_message(tr("economy.admin_give", tname, amt, coin)); self.history.add(tname, f"admin +{amt}"); tg.send_message(tr("economy.admin_give", tname, amt, coin)); self.ranking.update(tname, self.get_money_internal(tg))
            else: self.offline_cache.add(tname, "add", amt); sender.send_message(tr("economy.offline_cached", tname))
        elif op == "del":
            if amt <= 0: sender.send_message(tr("economy.must_positive")); return True
            if tg:
                if self.reduce_money_internal(tg, amt): sender.send_message(tr("economy.admin_take", tname, amt, coin)); self.history.add(tname, f"admin -{amt}"); tg.send_message(tr("economy.admin_take", tname, amt, coin)); self.ranking.update(tname, self.get_money_internal(tg))
                else: sender.send_message(tr("economy.not_enough"))
            else: self.offline_cache.add(tname, "reduce", amt); sender.send_message(tr("economy.offline_cached", tname))
        elif op == "set":
            if amt < 0: sender.send_message(tr("economy.must_nonneg")); return True
            if tg: self.set_money_internal(tg, amt); sender.send_message(tr("economy.admin_set_to", tname, coin, amt)); self.history.add(tname, f"admin ={amt}"); tg.send_message(tr("economy.admin_set_to", tname, coin, amt)); self.ranking.update(tname, amt)
            else: self.offline_cache.add(tname, "set", amt); sender.send_message(tr("economy.offline_cached", tname))
        return True
