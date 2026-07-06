"""
YEssential Sign-In System - 每日签到系统
月历展示, 随机奖励, 连续签到里程碑, 物品库管理
"""
import json
import os
import time
import random
from datetime import datetime
from typing import Dict, List, Any
from endstone import Player
from endstone.form import ActionForm, ModalForm, Dropdown, TextInput, Label, Toggle, Slider

from .log import plugin_print
from .i18n import tr


# ═══════════════════════════════════════════════════════════════
# Sign-In Data Management
# ═══════════════════════════════════════════════════════════════

class SignData:
    """签到数据持久化"""
    def __init__(self, data_folder: str):
        self.base_dir = os.path.join(data_folder, "..", "..", "data", "Sign")
        os.makedirs(self.base_dir, exist_ok=True)
        self.sign_path = os.path.join(self.base_dir, "signdata.json")
        self.reward_path = os.path.join(self.base_dir, "reward.json")

    def load_sign_data(self) -> dict:
        try:
            if os.path.exists(self.sign_path):
                with open(self.sign_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}

    def save_sign_data(self, data: dict):
        try:
            with open(self.sign_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except:
            pass

    def load_rewards(self) -> list:
        default = [
            '{"Count":1b,"Damage":0s,"Name":"minecraft:cooked_chicken","WasPickedUp":0b}',
            '{"Count":1b,"Damage":0s,"Name":"minecraft:bread","WasPickedUp":0b}',
            '{"Count":1b,"Damage":0s,"Name":"minecraft:apple","WasPickedUp":0b}',
            '{"Count":1b,"Damage":0s,"Name":"minecraft:enchanted_golden_apple","WasPickedUp":0b}'
        ]
        try:
            if os.path.exists(self.reward_path):
                with open(self.reward_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return default

    def save_rewards(self, data: list):
        try:
            with open(self.reward_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except:
            pass


class SignConfig:
    """签到配置管理"""
    def __init__(self, plugin):
        self.plugin = plugin

    def _get(self):
        return self.plugin.config_manager.config_data.get("Sign", {})

    @property
    def enabled(self) -> bool:
        return self._get().get("enable", True)

    @property
    def gui_arrange(self) -> int:
        return self._get().get("gui_arrange", 3)

    @property
    def random_money_min(self) -> int:
        return self._get().get("random_money", {}).get("min_money", 1000)

    @property
    def random_money_max(self) -> int:
        return self._get().get("random_money", {}).get("max_money", 10000)

    @property
    def random_exp_min(self) -> int:
        return self._get().get("random_exp", {}).get("min_exp", 100)

    @property
    def random_exp_max(self) -> int:
        return self._get().get("random_exp", {}).get("max_exp", 1000)

    @property
    def reward_sequence(self) -> list:
        return self._get().get("reward", [
            "item_1", "item_2", "money_1000", "money_1000", "random_money",
            "item_1", "money_1000", "item_3", "item_4", "random_money",
            "item_1", "item_2", "money_2000", "item_3", "random_money",
            "item_4", "money_1000", "item_1", "random_exp", "item_2",
            "money_1000", "item_3", "item_4", "random_money", "money_2000",
            "item_1", "item_2", "random_exp", "money_1000", "item_3",
            "item_4"
        ])

    @property
    def addition(self) -> dict:
        return self._get().get("addition", {
            "3": "item_1", "5": "money_500", "7": "item_2",
            "15": "item_2", "30": "money_2000"
        })

    @property
    def coin_name(self) -> str:
        return self.plugin.config_manager.config_data.get("Economy", {}).get("CoinName", "金币")


# ═══════════════════════════════════════════════════════════════
# Main Sign-In System
# ═══════════════════════════════════════════════════════════════

class SignSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.data = SignData(plugin.data_folder)
        self.config = SignConfig(plugin)
        self.info_prefix = "§l§6[-YEST-] §r"

    # ── 日期工具 ─────────────────────────────────────────

    def today_str(self) -> str:
        n = datetime.now()
        return f"{n.year}-{n.month:02d}-{n.day:02d}"

    def days_in_month(self) -> int:
        n = datetime.now()
        if n.month == 12:
            nxt = datetime(n.year + 1, 1, 1)
        else:
            nxt = datetime(n.year, n.month + 1, 1)
        return (nxt - datetime(n.year, n.month, 1)).days

    # ── 玩家签到数据 ──────────────────────────────────────

    def get_player_data(self, player: Player) -> dict:
        all_data = self.data.load_sign_data()
        name = player.name
        if name not in all_data:
            return {"count": 0, "weekly_count": 0, "monthly_count": 0,
                    "cont_sign": 0, "sign_date": "---"}
        return all_data[name]

    def save_player_data(self, name: str, d: dict):
        all_data = self.data.load_sign_data()
        all_data[name] = d
        self.data.save_sign_data(all_data)

    def time_diff(self, player: Player) -> int:
        """计算距离上次签到的天数"""
        d = self.get_player_data(player)
        last = d.get("sign_date", "---")
        if last == "---":
            return 99
        try:
            last_date = datetime.strptime(last, "%Y-%m-%d")
            today = datetime.strptime(self.today_str(), "%Y-%m-%d")
            return (today - last_date).days
        except:
            return 99

    def can_sign(self, player: Player) -> bool:
        d = self.get_player_data(player)
        return d.get("count", 0) == 0 or self.time_diff(player) > 0

    def do_sign(self, player: Player):
        """执行签到"""
        name = player.name
        today = self.today_str()
        d = self.get_player_data(player)

        if d.get("count", 0) == 0 or d.get("sign_date") == "---":
            # 首次签到
            d = {"count": 1, "weekly_count": 1, "monthly_count": 1,
                 "cont_sign": 1, "sign_date": today}
        else:
            d["count"] = d.get("count", 0) + 1

            now = datetime.now()
            if now.weekday() == 6:  # 周日重置
                d["weekly_count"] = 1
            else:
                d["weekly_count"] = d.get("weekly_count", 0) + 1

            if now.day == 1:
                d["monthly_count"] = 1
            else:
                d["monthly_count"] = d.get("monthly_count", 0) + 1

            if self.time_diff(player) <= 1:
                d["cont_sign"] = d.get("cont_sign", 0) + 1
            else:
                d["cont_sign"] = 1

            d["sign_date"] = today

        self.save_player_data(name, d)

    # ── 奖励系统 ──────────────────────────────────────────

    def get_reward_items(self) -> list:
        return self.data.load_rewards()

    def parse_reward(self, token: str) -> dict:
        """解析奖励标识符 -> {name, reward, type}"""
        token = token.strip()
        coin = self.config.coin_name

        if token == "random_money":
            m = random.randint(self.config.random_money_min, self.config.random_money_max)
            return {"name": f"随机{coin}x{m}", "reward": m, "type": "money"}

        if token == "random_item":
            items = self.get_reward_items()
            if items:
                return {"name": f"随机物品", "reward": random.choice(items), "type": "item_snbt"}
            return {"name": "无奖励", "reward": 0, "type": "none"}

        if token == "random_exp":
            e = random.randint(self.config.random_exp_min, self.config.random_exp_max)
            return {"name": f"随机经验x{e}", "reward": e, "type": "exp"}

        parts = token.split("_", 1)
        typ = parts[0]
        sub = parts[1] if len(parts) > 1 else ""

        if typ == "item":
            items = self.get_reward_items()
            try:
                idx = int(sub) - 1
                if 0 <= idx < len(items):
                    return {"name": f"物品#{idx+1}", "reward": items[idx], "type": "item_snbt"}
            except:
                pass
            return {"name": "无奖励", "reward": 0, "type": "none"}

        if typ == "money":
            try:
                n = int(sub)
                return {"name": f"{coin}x{n}", "reward": n, "type": "money"}
            except:
                pass

        if typ == "exp":
            try:
                n = int(sub)
                return {"name": f"经验x{n}", "reward": n, "type": "exp"}
            except:
                pass

        return {"name": "无奖励", "reward": 0, "type": "none"}

    def build_monthly_rewards(self) -> list:
        seq = self.config.reward_sequence
        days = self.days_in_month()
        result = []
        for i in range(days):
            result.append(self.parse_reward(seq[i % len(seq)]))
        return result

    def give_reward(self, player: Player, reward: dict):
        """发放奖励给玩家"""
        if reward["type"] == "money":
            if hasattr(self.plugin, 'economy') and self.plugin.economy:
                self.plugin.economy.add_money_internal(player, reward["reward"])
            else:
                player.perform_command(f"scoreboard players add @s money {reward['reward']}")
        elif reward["type"] == "exp":
            player.give_exp(reward["reward"])
        elif reward["type"] == "item_snbt":
            # 通过 give 命令发放 NBT 物品
            try:
                # 尝试解析 SNBT 并 give
                snbt = reward["reward"]
                player.perform_command(f'give @s {snbt}')
            except Exception as e:
                plugin_print(f"[Sign] 物品发放失败: {e}")

    def check_addition(self, player: Player):
        """检查并发放连续签到奖励"""
        cont = self.get_player_data(player).get("cont_sign", 0)
        additions = self.config.addition
        key = str(cont)
        if key in additions:
            bonus = self.parse_reward(additions[key])
            self.give_reward(player, bonus)
            player.send_message(
                f"{self.info_prefix}§b连续签到里程碑！§r §e第 §6{cont}§e 天附加奖励：§f{bonus['name']}"
            )

    # ── 物品名称映射 ──────────────────────────────────────

    ITEM_ZH_NAMES = {
        "minecraft:apple": "苹果", "minecraft:golden_apple": "金苹果",
        "minecraft:enchanted_golden_apple": "附魔金苹果", "minecraft:bread": "面包",
        "minecraft:cooked_chicken": "熟鸡肉", "minecraft:cooked_beef": "牛排",
        "minecraft:diamond": "钻石", "minecraft:emerald": "绿宝石",
        "minecraft:gold_ingot": "金锭", "minecraft:iron_ingot": "铁锭",
        "minecraft:netherite_ingot": "下界合金锭", "minecraft:diamond_sword": "钻石剑",
        "minecraft:diamond_pickaxe": "钻石镐", "minecraft:experience_bottle": "附魔之瓶",
        "minecraft:book": "书", "minecraft:enchanted_book": "附魔书",
        "minecraft:elytra": "鞘翅", "minecraft:totem_of_undying": "不死图腾",
        "minecraft:ender_pearl": "末影珍珠", "minecraft:nether_star": "下界之星",
        "minecraft:name_tag": "命名牌", "minecraft:saddle": "鞍",
    }

    def item_zh_name(self, snbt: str) -> str:
        """从 SNBT 中提取物品名称并汉化"""
        for key, name in self.ITEM_ZH_NAMES.items():
            if key in snbt:
                return name
        return "物品"

    # ══════════════════════════════════════════════════════════
    # GUI - 签到主界面
    # ══════════════════════════════════════════════════════════

    def open_sign_form(self, player: Player):
        """打开签到 GUI"""
        if not self.config.enabled:
            player.send_message(f"{self.info_prefix}§7签到功能已关闭")
            return

        rewards = self.build_monthly_rewards()
        today = datetime.now().day
        can = self.can_sign(player)
        d = self.get_player_data(player)

        # 构建月历内容
        cols = self.config.gui_arrange
        lines = []
        for i, r in enumerate(rewards):
            day = i + 1
            day_str = f"{day:02d}"
            if day < today:
                cell = f"§8{day_str} §7已签§r"
            elif day == today:
                cell = f"§e§l{day_str} §a{r['name'][:8]}§r"
            else:
                cell = f"§7{day_str} {r['name'][:8]}"

            # 按视觉宽度对齐 (中文=2, ASCII=1)
            def vis_len(s):
                w = 0
                for ch in s:
                    w += 2 if ord(ch) > 0x2E7F else 1
                return w

            target_w = 22 if cols <= 2 else 15 if cols == 3 else 11
            while vis_len(cell) < target_w:
                cell += " "
            lines.append(cell)
            if day % cols == 0:
                lines.append("")

        reward_text = "\n".join(lines)

        content = (
            f"§e本月 §f{d.get('monthly_count', 0)} §7次  "
            f"§b连续 §f{d.get('cont_sign', 0)} §7天  "
            f"§a累计 §f{d.get('count', 0)} §7次\n\n"
            f"§7── 本月奖励一览 ──\n{reward_text}\n\n"
            + (f"§a▶ 点击签到领取今日奖励！" if can else f"§7今日已完成签到~")
        )

        form = ActionForm(title="§l§e每日签到", content=content)
        if can:
            form.add_button("§l§a立即签到", icon="textures/items/emerald")
        else:
            form.add_button("§8§l今日已签到", icon="textures/ui/confirm")

        def on_submit(p, idx):
            if idx is None:
                return
            if not can:
                p.send_message(f"{self.info_prefix}§e今日已签到，明天继续~")
                return

            today_reward = rewards[today - 1]
            self.give_reward(p, today_reward)
            self.do_sign(p)
            self.check_addition(p)

            cont = self.get_player_data(p).get("cont_sign", 1)
            p.send_message(
                f"{self.info_prefix}§a签到成功！§e连续 §6{cont} §e天 ✦ 奖励：§f{today_reward['name']}"
            )

        form.on_submit = on_submit
        player.send_form(form)

    # ══════════════════════════════════════════════════════════
    # GUI - 管理员设置主菜单
    # ══════════════════════════════════════════════════════════

    def open_settings(self, player: Player):
        if not player.is_op:
            player.send_message(f"{self.info_prefix}§c仅管理员可用")
            return

        form = ActionForm(title="§3签到管理后台", content="§7选择管理模块：")
        form.add_button("§e签到参数设置\n§8开关、随机范围、列数")
        form.add_button("§6每日奖励序列\n§8配置每天的签到奖励")
        form.add_button("§b连续签到奖励\n§8设置里程碑奖励")
        form.add_button("§d奖励物品库\n§8管理物品奖励列表")

        def on_submit(p, idx):
            if idx == 0:
                self._open_param_settings(p)
            elif idx == 1:
                self._open_daily_rewards(p)
            elif idx == 2:
                self._open_addition_settings(p)
            elif idx == 3:
                self._open_item_lib(p)

        form.on_submit = on_submit
        player.send_form(form)

    def _open_param_settings(self, player: Player):
        cfg = self.config._get()
        sign_cfg = cfg.get("sign", {"switch": True, "gui_arrange": 3})
        rm = cfg.get("random_money", {"min_money": 1000, "max_money": 10000})
        re = cfg.get("random_exp", {"min_exp": 100, "max_exp": 1000})

        form = ModalForm(
            title="签到参数设置",
            controls=[
                Toggle(label=f"签到开关 (当前: {'§a开' if sign_cfg.get('switch', True) else '§c关'})",
                       default_value=sign_cfg.get("switch", True)),
                TextInput(label=f"随机金币最小值({rm['min_money']})", placeholder="1000",
                         default_value=str(rm["min_money"])),
                TextInput(label=f"随机金币最大值({rm['max_money']})", placeholder="10000",
                         default_value=str(rm["max_money"])),
                TextInput(label=f"随机经验最小值({re['min_exp']})", placeholder="100",
                         default_value=str(re["min_exp"])),
                TextInput(label=f"随机经验最大值({re['max_exp']})", placeholder="1000",
                         default_value=str(re["max_exp"])),
                TextInput(label=f"月历列数({sign_cfg.get('gui_arrange', 3)})", placeholder="3",
                         default_value=str(sign_cfg.get("gui_arrange", 3)))
            ]
        )

        def on_submit(p, data):
            if not data:
                self.open_settings(p)
                return
            try:
                sw = data[0]
                mn = int(data[1]) if data[1].strip() else rm["min_money"]
                mx = int(data[2]) if data[2].strip() else rm["max_money"]
                emn = int(data[3]) if data[3].strip() else re["min_exp"]
                emx = int(data[4]) if data[4].strip() else re["max_exp"]
                ga = int(data[5]) if data[5].strip() else sign_cfg.get("gui_arrange", 3)

                cur = self.plugin.config_manager.config_data
                cur["Sign"] = {
                    **(cur.get("Sign", {})),
                    "sign": {"switch": sw, "gui_arrange": max(1, min(10, ga))},
                    "random_money": {"min_money": mn, "max_money": mx},
                    "random_exp": {"min_exp": emn, "max_exp": emx},
                }
                self.plugin.config_manager.save_config()
                p.send_message(f"{self.info_prefix}§a参数已更新")
                self.open_settings(p)
            except Exception as e:
                p.send_message(f"{self.info_prefix}§c参数错误: {e}")

        form.on_submit = on_submit
        player.send_form(form)

    def _open_daily_rewards(self, player: Player):
        seq = self.config.reward_sequence
        days = self.days_in_month()
        items = [self.parse_reward(seq[i % len(seq)]).get("name", "?") for i in range(days)]

        form = ActionForm(title="§6每日奖励序列", content=f"§7共 {days} 天\n选择要修改的天数：")
        for i in range(days):
            form.add_button(f"§e第{i+1}天 §f{items[i][:20]}")

        form.add_button("§c返回")

        def on_submit(p, idx):
            if idx is None or idx == days:
                self.open_settings(p)
                return
            self._edit_day_reward(p, idx)

        form.on_submit = on_submit
        player.send_form(form)

    def _edit_day_reward(self, player: Player, day_idx: int):
        seq = self.config.reward_sequence
        days = self.days_in_month()
        items = self.get_reward_items()

        item_options = [f"物品库 #{j+1}" for j in range(len(items))]
        reward_types = ["随机物品", "随机金币", "随机经验"]

        form = ModalForm(
            title=f"修改第{day_idx+1}天奖励",
            controls=[
                Dropdown(label="奖励类型", options=reward_types, default_index=0),
                Dropdown(label="指定物品(仅指定物品时)", options=item_options if item_options else ["(空)"]),
                TextInput(label="金币/经验数量(仅指定时)", placeholder="1000", default_value="1000")
            ]
        )

        def on_submit(p, data):
            if not data:
                self._open_daily_rewards(p)
                return
            typ = int(data[0])
            if typ == 0:
                token = "random_item"
            elif typ == 1:
                token = "random_money"
            elif typ == 2:
                token = "random_exp"
            else:
                token = "money_1000"

            # 更新配置中的奖励序列
            cur = self.plugin.config_manager.config_data
            sign_cfg = cur.get("Sign", {})
            reward_list = list(sign_cfg.get("reward", seq))
            if day_idx < len(reward_list):
                reward_list[day_idx] = token
            else:
                while len(reward_list) <= day_idx:
                    reward_list.append("money_1000")
                reward_list[day_idx] = token
            sign_cfg["reward"] = reward_list
            cur["Sign"] = sign_cfg
            self.plugin.config_manager.save_config()
            p.send_message(f"{self.info_prefix}§a第{day_idx+1}天奖励已更新")
            self._open_daily_rewards(p)

        form.on_submit = on_submit
        player.send_form(form)

    def _open_addition_settings(self, player: Player):
        additions = self.config.addition
        keys = sorted(additions.keys(), key=int)

        lines = ["§l连续签到里程碑奖励：§r"]
        for k in keys:
            reward = self.parse_reward(additions[k])
            lines.append(f"  §6第 §e{k} §6天 → §a{reward['name']}")
        if not keys:
            lines.append("  §7(暂未配置)")

        form = ActionForm(title="§b连续签到附加奖励", content="\n".join(lines))
        form.add_button("§a添加/修改里程碑")
        form.add_button("§c删除里程碑")
        form.add_button("§c返回")

        def on_submit(p, idx):
            if idx == 0:
                self._edit_addition(p)
            elif idx == 1:
                self._delete_addition(p)
            else:
                self.open_settings(p)

        form.on_submit = on_submit
        player.send_form(form)

    def _edit_addition(self, player: Player):
        form = ModalForm(
            title="添加/修改连续签到奖励",
            controls=[
                TextInput(label="连续天数(如: 7)", placeholder="7", default_value=""),
                Dropdown(label="奖励类型", options=["随机物品", "随机金币", "随机经验", "物品库#1", "物品库#2"]),
                TextInput(label="金币/经验数量", placeholder="1000", default_value="1000")
            ]
        )

        def on_submit(p, data):
            if not data:
                self._open_addition_settings(p)
                return
            try:
                day = int(data[0].strip())
                typ = int(data[1])
                amt = int(data[2]) if data[2].strip() else 1000

                if typ == 0:
                    token = "random_item"
                elif typ == 1:
                    token = "random_money"
                elif typ == 2:
                    token = "random_exp"
                elif typ == 3:
                    token = "item_1"
                elif typ == 4:
                    token = "item_2"
                else:
                    token = "money_1000"

                cur = self.plugin.config_manager.config_data
                sign_cfg = cur.get("Sign", {})
                add = dict(sign_cfg.get("addition", {}))
                add[str(day)] = token
                sign_cfg["addition"] = add
                cur["Sign"] = sign_cfg
                self.plugin.config_manager.save_config()
                p.send_message(f"{self.info_prefix}§a连续签到第{day}天奖励已设置")
                self._open_addition_settings(p)
            except Exception as e:
                p.send_message(f"{self.info_prefix}§c参数错误: {e}")

        form.on_submit = on_submit
        player.send_form(form)

    def _delete_addition(self, player: Player):
        additions = self.config.addition
        keys = sorted(additions.keys(), key=int)

        if not keys:
            player.send_message(f"{self.info_prefix}§c没有可删除的里程碑")
            self._open_addition_settings(player)
            return

        form = ActionForm(title="删除里程碑", content="选择要删除的：")
        for k in keys:
            r = self.parse_reward(additions[k])
            form.add_button(f"第{k}天: {r['name']}")
        form.add_button("§c返回")

        def on_submit(p, idx):
            if idx is None or idx == len(keys):
                self._open_addition_settings(p)
                return
            del_key = keys[idx]
            cur = self.plugin.config_manager.config_data
            sign_cfg = cur.get("Sign", {})
            add = dict(sign_cfg.get("addition", {}))
            if del_key in add:
                del add[del_key]
            sign_cfg["addition"] = add
            cur["Sign"] = sign_cfg
            self.plugin.config_manager.save_config()
            p.send_message(f"{self.info_prefix}§a已删除第{del_key}天里程碑")
            self._open_addition_settings(p)

        form.on_submit = on_submit
        player.send_form(form)

    def _open_item_lib(self, player: Player):
        items = self.get_reward_items()
        lines = [f"§7共 {len(items)} 种物品\n§e管理物品库（影响随机物品和指定物品奖励）："]
        for i, snbt in enumerate(items):
            name = self.item_zh_name(snbt)
            lines.append(f"  §f{i+1}. §a{name}")

        form = ActionForm(title="§d奖励物品库", content="\n".join(lines[:30]))
        form.add_button("§c返回")

        def on_submit(p, idx):
            self.open_settings(p)

        form.on_submit = on_submit
        player.send_form(form)

    # ── 玩家上线自动弹窗 ─────────────────────────────────

    def on_player_join(self, player: Player):
        """玩家上线时如果未签到则弹窗"""
        if not self.config.enabled:
            return
        if self._is_simulated(player):
            return
        if self.can_sign(player):
            # 延迟3秒弹窗
            def popup():
                p = self.plugin.server.get_player(player.name)
                if p:
                    self.open_sign_form(p)
            self.plugin.server.scheduler.run_task(self.plugin, popup, 60)

    def _is_simulated(self, player: Player) -> bool:
        return player.name.endswith("_sp")
