"""
YEssential Sign-In System
"""
import json, os, random
from datetime import datetime
from endstone import Player
from endstone.form import ActionForm, ModalForm, Dropdown, TextInput, Label, Toggle
from .i18n import tr


class SignData:
    def __init__(self, data_folder: str):
        self.base_dir = os.path.normpath(os.path.join(data_folder, "..", "..", "data", "Sign"))
        os.makedirs(self.base_dir, exist_ok=True)
        self.sign_path = os.path.join(self.base_dir, "signdata.json")
        self.reward_path = os.path.join(self.base_dir, "reward.json")

    def load_sign(self) -> dict:
        try:
            if os.path.exists(self.sign_path):
                with open(self.sign_path, encoding="utf-8") as f:
                    return json.load(f)
        except: pass
        return {}

    def save_sign(self, d):
        try:
            with open(self.sign_path, "w", encoding="utf-8") as f:
                json.dump(d, f, indent=2, ensure_ascii=False)
        except: pass

    def load_rewards(self) -> list:
        dft = ['{"Count":1b,"Damage":0s,"Name":"minecraft:cooked_chicken","WasPickedUp":0b}',
               '{"Count":1b,"Damage":0s,"Name":"minecraft:bread","WasPickedUp":0b}',
               '{"Count":1b,"Damage":0s,"Name":"minecraft:apple","WasPickedUp":0b}',
               '{"Count":1b,"Damage":0s,"Name":"minecraft:enchanted_golden_apple","WasPickedUp":0b}']
        try:
            if os.path.exists(self.reward_path):
                with open(self.reward_path, encoding="utf-8") as f:
                    return json.load(f)
        except: pass
        return dft


class SignConfig:
    def __init__(self, plugin): self.plugin = plugin
    def _get(self): return self.plugin.config_manager.config_data.get("Sign", {})
    @property
    def enabled(self): return self._get().get("enable", True)
    @property
    def cols(self): return self._get().get("gui_arrange", 3)
    @property
    def rm_min(self): return self._get().get("random_money", {}).get("min_money", 1000)
    @property
    def rm_max(self): return self._get().get("random_money", {}).get("max_money", 10000)
    @property
    def re_min(self): return self._get().get("random_exp", {}).get("min_exp", 100)
    @property
    def re_max(self): return self._get().get("random_exp", {}).get("max_exp", 1000)
    @property
    def reward_seq(self):
        return self._get().get("reward", ["item_1","item_2","money_1000","money_1000","random_money","item_1","money_1000","item_3","item_4","random_money","item_1","item_2","money_2000","item_3","random_money","item_4","money_1000","item_1","random_exp","item_2","money_1000","item_3","item_4","random_money","money_2000","item_1","item_2","random_exp","money_1000","item_3","item_4"])
    @property
    def addition(self): return self._get().get("addition", {"3":"item_1","5":"money_500","7":"item_2","15":"item_2","30":"money_2000"})
    @property
    def coin_name(self): return self.plugin.config_manager.config_data.get("Economy", {}).get("CoinName", "金币")


_ITEM_ZH = {"minecraft:apple":"苹果","minecraft:golden_apple":"金苹果","minecraft:enchanted_golden_apple":"附魔金苹果","minecraft:bread":"面包","minecraft:cooked_chicken":"熟鸡肉","minecraft:cooked_beef":"牛排","minecraft:diamond":"钻石","minecraft:emerald":"绿宝石","minecraft:gold_ingot":"金锭","minecraft:iron_ingot":"铁锭","minecraft:netherite_ingot":"下界合金锭","minecraft:experience_bottle":"附魔之瓶","minecraft:book":"书","minecraft:enchanted_book":"附魔书","minecraft:elytra":"鞘翅","minecraft:totem_of_undying":"不死图腾","minecraft:ender_pearl":"末影珍珠","minecraft:nether_star":"下界之星","minecraft:name_tag":"命名牌","minecraft:saddle":"鞍"}


class SignSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.data = SignData(plugin.data_folder)
        self.cfg = SignConfig(plugin)
        self.prefix = "§l§6[-YEST-] §r"

    # ── date helpers ────────────────────────────────────
    def _today(self): n=datetime.now(); return f"{n.year}-{n.month:02d}-{n.day:02d}"
    def _days_in_month(self):
        n = datetime.now()
        nxt = datetime(n.year+1,1,1) if n.month==12 else datetime(n.year,n.month+1,1)
        return (nxt-datetime(n.year,n.month,1)).days

    # ── player data ──────────────────────────────────────
    def _player(self, p: Player):
        d = self.data.load_sign()
        return d.get(p.name, {"count":0,"weekly_count":0,"monthly_count":0,"cont_sign":0,"sign_date":"---"})
    def _save(self, name, d):
        all_d = self.data.load_sign(); all_d[name]=d; self.data.save_sign(all_d)

    def _diff(self, p: Player):
        last = self._player(p).get("sign_date","---")
        if last=="---": return 99
        try: return (datetime.strptime(self._today(),"%Y-%m-%d")-datetime.strptime(last,"%Y-%m-%d")).days
        except: return 99

    def can_sign(self, p: Player): return self._player(p).get("count",0)==0 or self._diff(p)>0

    def do_sign(self, p: Player):
        name, today, d = p.name, self._today(), self._player(p)
        if d.get("count",0)==0 or d.get("sign_date")=="---":
            d = {"count":1,"weekly_count":1,"monthly_count":1,"cont_sign":1,"sign_date":today}
        else:
            d["count"]=d.get("count",0)+1; n=datetime.now()
            d["weekly_count"]=1 if n.weekday()==6 else d.get("weekly_count",0)+1
            d["monthly_count"]=1 if n.day==1 else d.get("monthly_count",0)+1
            d["cont_sign"]=d.get("cont_sign",0)+1 if self._diff(p)<=1 else 1
            d["sign_date"]=today
        self._save(name, d)

    # ── rewards ──────────────────────────────────────────
    def _item_name(self, snbt):
        for k,v in _ITEM_ZH.items():
            if k in snbt: return v
        return tr("sign.item")

    def _parse(self, token):
        token=token.strip(); coin=self.cfg.coin_name
        if token=="random_money":
            m=random.randint(self.cfg.rm_min,self.cfg.rm_max); return {"name":tr("sign.money_fmt",coin,m),"reward":m,"type":"money"}
        if token=="random_item":
            items=self.data.load_rewards()
            return {"name":tr("sign.random_item"),"reward":random.choice(items) if items else "","type":"item_snbt"}
        if token=="random_exp":
            e=random.randint(self.cfg.re_min,self.cfg.re_max); return {"name":tr("sign.exp_fmt",e),"reward":e,"type":"exp"}
        p=token.split("_",1); t=p[0]; s=p[1] if len(p)>1 else ""
        if t=="item":
            items=self.data.load_rewards()
            try:
                idx=int(s)-1
                if 0<=idx<len(items): return {"name":self._item_name(items[idx]),"reward":items[idx],"type":"item_snbt"}
            except: pass
            return {"name":tr("sign.none"),"reward":0,"type":"none"}
        if t=="money":
            try: return {"name":f"{coin}x{int(s)}","reward":int(s),"type":"money"}
            except: pass
        if t=="exp":
            try: return {"name":tr("sign.exp_fmt",int(s)),"reward":int(s),"type":"exp"}
            except: pass
        return {"name":tr("sign.none"),"reward":0,"type":"none"}

    def _monthly_rewards(self):
        seq, days = self.cfg.reward_seq, self._days_in_month()
        r=[self._parse(seq[i%len(seq)]) for i in range(days)]
        return r

    def _give(self, p: Player, rw: dict):
        if rw["type"]=="money":
            if hasattr(self.plugin,'economy') and self.plugin.economy:
                self.plugin.economy.add_money_internal(p, rw["reward"])
        elif rw["type"]=="exp":
            p.give_exp(rw["reward"])
        elif rw["type"]=="item_snbt":
            try: p.perform_command(f'give @s {rw["reward"]}')
            except: pass

    def _check_addition(self, p: Player):
        cont=self._player(p).get("cont_sign",0); adds=self.cfg.addition
        k=str(cont)
        if k in adds:
            bonus=self._parse(adds[k]); self._give(p, bonus)
            p.send_message(self.prefix+tr("sign.milestone",cont,bonus['name']))

    # ══════════════════════════════════════════════════════
    # 签到主界面
    # ══════════════════════════════════════════════════════
    def open_sign_form(self, p: Player):
        if not self.cfg.enabled: p.send_message(f"{self.prefix}§7{tr('sign.disabled')}"); return
        rewards, today, can, d = self._monthly_rewards(), datetime.now().day, self.can_sign(p), self._player(p)

        # 三列布局，空格对齐
        import re
        def _vpad(s, w):
            plain=re.sub(r"§[0-9a-fk-or]","",s)
            v=sum(2 if ord(c)>0x2E7F else 1 for c in plain)
            return s+" "*(max(0,w-v))

        cells=[]
        for i,r in enumerate(rewards):
            day=i+1; name=r['name'][:6]
            if day<today:    cell=f"§8{day:02d}.§8{name}§r"
            elif day==today: cell=f"§e§l▶{day:02d}.§a{name}§r"
            else:            cell=f"§7{day:02d}.{name}§r"
            cells.append(_vpad(cell, 14))

        lines=[]
        for j in range(0, len(cells), 3):
            a=cells[j]
            b=cells[j+1] if j+1<len(cells) else ""
            c=cells[j+2] if j+2<len(cells) else ""
            lines.append(f"§r{a}{b}{c}")

        content = (
            tr("sign.stats", d.get('monthly_count',0), d.get('cont_sign',0), d.get('count',0))
            + "\n\n"
            + tr("sign.monthly_title") + "\n"
            + "\n".join(lines) + "\n\n"
            + (tr("sign.prompt_sign") if can else tr("sign.prompt_done"))
        )

        form = ActionForm(title=tr("sign.title"), content=content)
        if can:
            form.add_button(tr("sign.sign_btn"), icon="textures/items/emerald")
        else:
            form.add_button(tr("sign.signed_btn"), icon="textures/ui/confirm")

        def cb(pl, idx):
            if idx is None: return
            if not can: pl.send_message(f"{self.prefix}{tr('sign.already')}"); return
            rw=rewards[today-1]; self._give(pl, rw); self.do_sign(pl); self._check_addition(pl)
            cnt=self._player(pl).get("cont_sign",1)
            pl.send_message(self.prefix+tr("sign.success",cnt,rw['name']))

        form.on_submit = cb
        p.send_form(form)

    # ══════════════════════════════════════════════════════
    # 管理后台
    # ══════════════════════════════════════════════════════
    def open_settings(self, p: Player):
        if not p.is_op: p.send_message(f"{self.prefix}§c{tr('sign.admin_only')}"); return
        form=ActionForm(title=tr("sign.admin_title"), content=tr("sign.admin_content"))
        form.add_button(tr("sign.admin_economy"), icon="textures/items/gold_ingot")
        form.add_button(tr("sign.admin_params"), icon="textures/ui/settings_glyph_color_2x")
        form.add_button(tr("sign.admin_reward"), icon="textures/ui/recipe_book_icon")
        form.add_button(tr("sign.admin_items"), icon="textures/blocks/chest_front")
        form.add_button(tr("sign.admin_addition"), icon="textures/items/diamond")
        def cb(_, idx):
            if idx==0: self._gui_money_view(p)
            elif idx==1: self._gui_params(p)
            elif idx==2: self._gui_daily(p)
            elif idx==3: self._gui_items(p)
            elif idx==4: self._gui_addition_list(p)
        form.on_submit=cb; p.send_form(form)

    def _gui_money_view(self, p: Player):
        eco=self.plugin.config_manager.config_data.get("Economy",{})
        mode=eco.get("mode","scoreboard"); sb=eco.get("Scoreboard","money"); coin=eco.get("CoinName",tr("economy.coin"))
        form=ModalForm(title=tr("sign.gui_economy_title"), controls=[
            Label(text=tr("sign.gui_economy_mode", mode)),
            Label(text=tr("sign.gui_economy_sb", sb)),
            Label(text=tr("sign.gui_economy_coin", coin)),
            Label(text=tr("sign.gui_economy_note"))
        ])
        form.on_submit=lambda _,__: self.open_settings(p); p.send_form(form)

    def _gui_params(self, p: Player):
        sc=self.cfg._get()
        rm=sc.get("random_money",{"min_money":1000,"max_money":10000})
        re=sc.get("random_exp",{"min_exp":100,"max_exp":1000})
        sw=sc.get("enable",True)
        form=ModalForm(title=tr("sign.gui_params_title"), controls=[
            Toggle(label=tr("sign.gui_params_switch", tr("sign.gui_on") if sw else tr("sign.gui_off")), default_value=sw),
            Label(text=tr("sign.gui_params_money_label")),
            TextInput(label=tr("sign.gui_params_money_min", rm['min_money']), placeholder="1000", default_value=str(rm['min_money'])),
            TextInput(label=tr("sign.gui_params_money_max", rm['max_money']), placeholder="10000", default_value=str(rm['max_money'])),
            Label(text=tr("sign.gui_params_exp_label")),
            TextInput(label=tr("sign.gui_params_exp_min", re['min_exp']), placeholder="100", default_value=str(re['min_exp'])),
            TextInput(label=tr("sign.gui_params_exp_max", re['max_exp']), placeholder="1000", default_value=str(re['max_exp'])),
            Label(text=tr("sign.gui_params_layout_label")),
            TextInput(label=tr("sign.gui_params_layout", sc.get("gui_arrange",3)), placeholder="3", default_value=str(sc.get("gui_arrange",3)))
        ])
        def cb(_, data):
            if not data: self.open_settings(p); return
            data = json.loads(data) if isinstance(data, str) else data
            try:
                cur=self.plugin.config_manager.config_data
                cur["Sign"]={**sc, "enable":data[0],"gui_arrange":max(1,min(10,int(data[7]) if data[7].strip() else 3)),
                    "random_money":{"min_money":int(data[2]) if data[2].strip() else rm["min_money"],"max_money":int(data[3]) if data[3].strip() else rm["max_money"]},
                    "random_exp":{"min_exp":int(data[5]) if data[5].strip() else re["min_exp"],"max_exp":int(data[6]) if data[6].strip() else re["max_exp"]}}
                self.plugin.config_manager.save_config(); p.send_message(self.prefix+tr("sign.gui_updated")); self.open_settings(p)
            except Exception as e: self._gui_params(p)
        form.on_submit=cb; p.send_form(form)

    def _gui_daily(self, p: Player):
        seq=self.cfg.reward_seq; days=self._days_in_month()
        items=[self._parse(seq[i%len(seq)]).get("name","?") for i in range(days)]
        form=ActionForm(title=tr("sign.gui_daily_title"), content=tr("sign.gui_daily_content", days))
        for i in range(days): form.add_button(tr("sign.gui_daily_day", i+1, items[i][:20]))
        form.add_button(tr("sign.gui_back"))
        def cb(_, idx):
            if idx is None or idx==days: self.open_settings(p); return
            self._gui_day_edit(p, idx)
        form.on_submit=cb; p.send_form(form)

    def _gui_day_edit(self, p: Player, day_idx: int):
        form=ModalForm(title=tr("sign.gui_day_edit_title", day_idx+1), controls=[
            Dropdown(label=tr("sign.gui_day_edit_type"), options=[tr("sign.random_item"),tr("sign.random_money"),tr("sign.random_exp")], default_index=0),
            TextInput(label=tr("sign.gui_day_edit_amount"), placeholder="1000", default_value="1000")
        ])
        def cb(_, data):
            if not data: self._gui_daily(p); return
            data = json.loads(data) if isinstance(data, str) else data
            typ=int(data[0]); amt=int(data[1]) if data[1].strip() else 1000
            token={"0":"random_item","1":"random_money","2":"random_exp"}.get(str(typ),f"money_{amt}")
            cur=self.plugin.config_manager.config_data; sc=cur.get("Sign",{})
            rl=list(sc.get("reward",self.cfg.reward_seq))
            while len(rl)<=day_idx: rl.append("money_1000")
            rl[day_idx]=token; sc["reward"]=rl; cur["Sign"]=sc
            self.plugin.config_manager.save_config()
            p.send_message(self.prefix+tr("sign.gui_day_updated", day_idx+1)); self._gui_daily(p)
        form.on_submit=cb; p.send_form(form)

    def _gui_items(self, p: Player):
        items=self.data.load_rewards()
        lines=[tr("sign.gui_items_content", len(items))]
        for i,snbt in enumerate(items): lines.append(f"  §f{i+1}. §a{self._item_name(snbt)}")
        form=ActionForm(title=tr("sign.gui_items_title"), content="\n".join(lines[:30]))
        form.add_button(tr("sign.gui_back"))
        form.on_submit=lambda _,__: self.open_settings(p); p.send_form(form)

    def _gui_addition_list(self, p: Player):
        adds=self.cfg.addition; keys=sorted(adds.keys(),key=int)
        lines=[tr("sign.gui_addition_list_title")]
        for k in keys: lines.append(tr("sign.gui_addition_item", k, self._parse(adds[k])['name']))
        if not keys: lines.append(tr("sign.gui_addition_empty"))
        form=ActionForm(title=tr("sign.gui_addition_title"), content="\n".join(lines))
        form.add_button(tr("sign.gui_addition_add")); form.add_button(tr("sign.gui_addition_del")); form.add_button(tr("sign.gui_back"))
        def cb(_, idx):
            if idx==0: self._gui_addition_edit(p)
            elif idx==1: self._gui_addition_del(p)
            else: self.open_settings(p)
        form.on_submit=cb; p.send_form(form)

    def _gui_addition_edit(self, p: Player):
        form=ModalForm(title=tr("sign.gui_addition_edit_title"), controls=[
            TextInput(label=tr("sign.gui_addition_days"), placeholder="7", default_value=""),
            Dropdown(label=tr("sign.gui_day_edit_type"), options=[tr("sign.random_item"),tr("sign.random_money"),tr("sign.random_exp")]),
            TextInput(label=tr("sign.gui_day_edit_amount"), placeholder="1000", default_value="1000")
        ])
        def cb(_, data):
            if not data: self._gui_addition_list(p); return
            data = json.loads(data) if isinstance(data, str) else data
            try:
                day=int(data[0].strip()); typ=int(data[1]); amt=int(data[2]) if data[2].strip() else 1000
                token={"0":"random_item","1":"random_money","2":"random_exp"}.get(str(typ),f"money_{amt}")
                cur=self.plugin.config_manager.config_data; sc=cur.get("Sign",{})
                adds=dict(sc.get("addition",{})); adds[str(day)]=token
                sc["addition"]=adds; cur["Sign"]=sc; self.plugin.config_manager.save_config()
                p.send_message(self.prefix+tr("sign.gui_addition_set", day)); self._gui_addition_list(p)
            except: pass
        form.on_submit=cb; p.send_form(form)

    def _gui_addition_del(self, p: Player):
        adds=self.cfg.addition; keys=sorted(adds.keys(),key=int)
        if not keys: p.send_message(self.prefix+tr("sign.gui_addition_none")); self._gui_addition_list(p); return
        form=ActionForm(title=tr("sign.gui_addition_del_title"), content=tr("sign.gui_addition_del_content"))
        for k in keys: form.add_button(tr("sign.gui_addition_day", k, self._parse(adds[k])['name']))
        form.add_button(tr("sign.gui_back"))
        def cb(_, idx):
            if idx is None or idx==len(keys): self._gui_addition_list(p); return
            cur=self.plugin.config_manager.config_data; sc=cur.get("Sign",{})
            adds=dict(sc.get("addition",{})); del adds[keys[idx]]
            sc["addition"]=adds; cur["Sign"]=sc; self.plugin.config_manager.save_config()
            p.send_message(self.prefix+tr("sign.gui_addition_deleted", keys[idx])); self._gui_addition_list(p)
        form.on_submit=cb; p.send_form(form)

    # ── 上线弹窗 ─────────────────────────────────────────
    def on_player_join(self, p: Player):
        if not self.cfg.enabled or p.name.endswith("_sp"): return
        if self.can_sign(p):
            def popup():
                pl=self.plugin.server.get_player(p.name)
                if pl: self.open_sign_form(pl)
            self.plugin.server.scheduler.run_task(self.plugin, popup, 60)
