import json
import os
import re
import time
import threading
from typing import List, Dict, Optional
from endstone import Player
from endstone.level import Level
from endstone.actor import Actor

class CleanmgrConfig:
    def __init__(self, plugin):
        self.plugin = plugin
        self.config_path = "./plugins/YEssential/config/cleanmgr/config.json"
        self.lang_path = "./plugins/YEssential/lang/cleanmgr/lang.json"
        self.player_settings_path = "./plugins/YEssential/data/CleanmgrSettingData.json"
        self._config = {}
        self._lang = {}
        self.player_settings: Dict[str, bool] = {}
        self.whitelist_regex: List[re.Pattern] = []
        self.ensure_directories()
        self.load()

    def ensure_directories(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.lang_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.player_settings_path), exist_ok=True)

    def load(self):
        self._config = self.load_config()
        self._lang = self.load_lang()
        self.load_player_settings()
        self.compile_whitelist()

    def load_lang(self) -> dict:
        default = {
            "prefix": "§l§6[-YEST-] §l§e[清理系统] §r",
            "messages": {
                "system_starting": "§a清理系统正在启动...",
                "system_started": "§a清理系统已启动",
                "cleanup_start": "§a开始清理实体...",
                "cleanup_complete": "§a已清理 {0} 个实体",
                "low_tps_clean": "§cTPS 过低({0})，已自动清理",
                "manual_trigger": "§6玩家触发了手动清理",
                "cancel_success": "§c已取消计划清理",
                "status_idle": "§a当前没有清理任务在进行",
                "status_scheduled": "§a计划清理将在 {0} 秒后执行",
                "status_cleaning": "§c正在清理实体...",
                "tps_info": "§a当前TPS: §e{0}§a / 20.00",
                "help_message": "§e用法:\n§a/clean §7- 触发清理\n§a/clean status §7- 查询状态\n§a/clean cancel §7- 取消清理\n§a/clean tps §7- 查询TPS\n§a/clean toast §7- 开关顶部弹窗"
            }
        }

        if not os.path.exists(self.lang_path):
            try:
                with open(self.lang_path, 'w', encoding='utf-8') as f:
                    json.dump(default, f, indent=2, ensure_ascii=False)
            except:
                pass
            return default

        try:
            with open(self.lang_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                return self.merge(default, loaded)
        except:
            return default

    def load_config(self) -> dict:
        default = {
            "cleanmgr": {
                "enable": True,
                "interval": 600,
                "debug": False,
                "whitelist": [
                    "^minecraft:netherite_", "^minecraft:ancient_debris$", "^minecraft:dragon_egg$",
                    "^minecraft:nether_star$", "^minecraft:elytra$", "^minecraft:emerald$",
                    "^minecraft:beacon$", "^minecraft:ender_eye$", "^minecraft:shulker_box$",
                    "^minecraft:sea_lantern$", "^minecraft:enchanted_book$", "^minecraft:diamond",
                    "^minecraft:totem_of_undying$", "^minecraft:ender_pearl$", "^minecraft:villager_v2$",
                    "^minecraft:ender_crystal$", "^minecraft:ender_dragon$", "^minecraft:parrot$",
                    "^minecraft:chest_minecart$", "^minecraft:minecart$", "^minecraft:hopper_minecart$",
                    "^minecraft:armor_stand$", "^minecraft:boat$", "^minecraft:sheep$", "^minecraft:leash_knot$",
                    "^minecraft:cow$", "^minecraft:pig$", "^minecraft:painting$"
                ],
                "notice": {"notice1": 30, "notice2": 15, "notice3": 5},
                "LowTpsClean": {
                    "enable": True,
                    "minimum": 15,
                    "maxConsecutiveCleans": 2,
                    "longCooldown": 450
                },
                "playerCooldown": 300
            }
        }

        if not os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(default, f, indent=2, ensure_ascii=False)
            except:
                pass
            return default.get("cleanmgr", {})

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                raw = json.load(f)
                return raw.get("cleanmgr", {})
        except:
            return default.get("cleanmgr", {})

    def load_player_settings(self):
        if os.path.exists(self.player_settings_path):
            try:
                with open(self.player_settings_path, 'r', encoding='utf-8') as f:
                    self.player_settings = json.load(f)
            except:
                self.player_settings = {}
        else:
            self.player_settings = {}

    def save_player_settings(self):
        try:
            with open(self.player_settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.player_settings, f, indent=2)
        except:
            pass

    def compile_whitelist(self):
        self.whitelist_regex = []
        whitelist = self._config.get("whitelist", [])
        for pattern in whitelist:
            try:
                self.whitelist_regex.append(re.compile(pattern))
            except:
                pass

    def merge(self, default: dict, loaded: dict) -> dict:
        result = default.copy()
        for key, value in loaded.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                result[key] = self.merge(result[key], value)
            else:
                result[key] = value
        return result

    def t(self, key: str, *args) -> str:
        keys = key.split(".")
        obj = self._lang
        for k in keys:
            if isinstance(obj, dict):
                obj = obj.get(k, key)
            else:
                return key
        if not isinstance(obj, str):
            return key
        for i, arg in enumerate(args):
            obj = obj.replace(f"{{{i}}}", str(arg))
        return obj

    def get(self, key: str, default=None):
        return self._config.get(key, default)

    def get_message(self, key: str, *args) -> str:
        msg = self._lang.get("messages", {}).get(key, key)
        for i, arg in enumerate(args):
            msg = msg.replace(f"{{{i}}}", str(arg))
        return msg


class CleanmgrState:
    def __init__(self):
        self.phase = "idle"
        self.scheduled_timeouts: list = []
        self.last_player_clean: Dict[str, float] = {}
        self.low_tps_clean_count = 0
        self.low_tps_retry_time = 0
        self.tps_before_clean = 20.0
        self.is_low_tps_trigger = False


class CleanmgrSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.config = CleanmgrConfig(plugin)
        self.state = CleanmgrState()
        self.current_tps = 20.0
        self.timers: list = []

        self.start_tps_sampler()
        self.start_timers()

    def start_tps_sampler(self):
        def sample():
            while True:
                time.sleep(1)
                try:
                    self.current_tps = self.plugin.server.current_tps
                except:
                    pass

        thread = threading.Thread(target=sample, daemon=True)
        thread.start()

    def start_tps_cleanup_checker(self):
        def check():
            while True:
                time.sleep(5)
                if not self.config.get("LowTpsClean", {}).get("enable", True):
                    continue

                now = time.time() * 1000
                if now < self.state.low_tps_retry_time:
                    continue

                if self.current_tps <= self.config.get("LowTpsClean", {}).get("minimum", 15):
                    if self.state.phase == "idle":
                        self.state.tps_before_clean = self.current_tps
                        self.plugin.server.broadcast_message(
                            self.config.t("prefix", "") + 
                            self.config.get_message("low_tps_clean", f"{self.current_tps:.2f}")
                        )
                        self.schedule_clean(is_manual=False, player_name="", is_low_tps=True)

        thread = threading.Thread(target=check, daemon=True)
        thread.start()

    def start_timers(self):
        interval = self.config.get("interval", 600)

        def scheduled_clean():
            while True:
                time.sleep(interval)
                if self.config.get("enable", True) and self.state.phase == "idle":
                    self.schedule_clean(is_manual=False, player_name="", is_low_tps=False)

        thread = threading.Thread(target=scheduled_clean, daemon=True)
        thread.start()

        self.start_tps_cleanup_checker()

    def should_keep(self, entity: Actor) -> bool:
        try:
            if entity.type == "minecraft:player":
                return True
        except:
            pass

        try:
            entity_type = entity.type
            for regex in self.config.whitelist_regex:
                if regex.search(entity_type):
                    return True
        except:
            pass

        return False

    def execute_clean(self):
        self.state.phase = "cleaning"
        removed = 0
        kept = 0

        self.plugin.server.broadcast_message(
            self.config.t("prefix", "") + self.config.get_message("cleanup_start")
        )

        try:
            level = self.plugin.server.level
            for dimension in level.dimensions:
                for entity in dimension.actors:
                    if self.should_keep(entity):
                        kept += 1
                    else:
                        try:
                            entity.remove()
                            removed += 1
                        except:
                            pass
        except Exception as e:
            self.plugin.logger.error(f"清理实体失败: {e}")

        self.plugin.server.broadcast_message(
            self.config.t("prefix", "") + self.config.get_message("cleanup_complete", removed)
        )

        self.send_toast_to_all(
            "清理系统",
            self.config.get_message("cleanup_complete", removed)
        )

        if self.state.is_low_tps_trigger:
            def evaluate():
                time.sleep(5)
                improved = self.current_tps > (self.state.tps_before_clean + 2.0)

                if improved:
                    self.state.low_tps_clean_count = 0
                else:
                    self.state.low_tps_clean_count += 1
                    if self.state.low_tps_clean_count >= self.config.get("LowTpsClean", {}).get("maxConsecutiveCleans", 2):
                        cool_min = round(self.config.get("LowTpsClean", {}).get("longCooldown", 450) / 60)
                        self.plugin.server.broadcast_message(
                            self.config.t("prefix", "") + 
                            self.config.get_message("low_tps_ineffective", cool_min)
                        )
                        self.state.low_tps_retry_time = (time.time() * 1000) + (self.config.get("LowTpsClean", {}).get("longCooldown", 450) * 1000)
                        self.state.low_tps_clean_count = 0

                self.state.is_low_tps_trigger = False

            thread = threading.Thread(target=evaluate, daemon=True)
            thread.start()

        self.state.phase = "idle"
        self.state.scheduled_timeouts = []

    def schedule_clean(self, is_manual: bool = False, player_name: str = "", is_low_tps: bool = False):
        if self.state.phase != "idle":
            return

        if is_manual and player_name:
            now = time.time()
            last = self.state.last_player_clean.get(player_name, 0)
            cooldown = self.config.get("playerCooldown", 300)
            if (now - last) < cooldown:
                player = self.plugin.server.get_player(player_name)
                if player:
                    player.send_message(
                        self.config.t("prefix", "") + "§c触发清理冷却中，请稍后再试"
                    )
                return

            self.state.last_player_clean[player_name] = now
            self.plugin.server.broadcast_message(
                self.config.t("prefix", "") + self.config.get_message("manual_trigger")
            )

        self.state.phase = "scheduled"
        self.state.is_low_tps_trigger = is_low_tps

        notice = self.config.get("notice", {})
        n1 = notice.get("notice1", 30)
        n2 = notice.get("notice2", 15)
        n3 = notice.get("notice3", 5)

        self.plugin.server.broadcast_message(
            self.config.t("prefix", "") + self.config.get_message("cleanup_notice", n1)
        )
        self.send_toast_to_all("清理系统", self.config.get_message("cleanup_notice", n1))

        if n2 > 0 and n2 < n1:
            def notice2():
                time.sleep((n1 - n2))
                if self.state.phase == "scheduled":
                    self.plugin.server.broadcast_message(
                        self.config.t("prefix", "") + self.config.get_message("cleanup_notice2", n2)
                    )
                    self.send_toast_to_all("清理系统", self.config.get_message("cleanup_notice2", n2))
            t = threading.Thread(target=notice2, daemon=True)
            t.start()

        if n3 > 0 and n3 < n2:
            def notice3():
                time.sleep((n1 - n3))
                if self.state.phase == "scheduled":
                    self.plugin.server.broadcast_message(
                        self.config.t("prefix", "") + self.config.get_message("cleanup_notice3", n3)
                    )
                    self.send_toast_to_all("清理系统", self.config.get_message("cleanup_notice3", n3))
            t = threading.Thread(target=notice3, daemon=True)
            t.start()

        def do_clean():
            time.sleep(n1)
            self.execute_clean()

        t = threading.Thread(target=do_clean, daemon=True)
        t.start()

    def send_toast_to_all(self, title: str, message: str):
        for player in self.plugin.server.online_players:
            xuid = player.xuid
            if self.config.player_settings.get(xuid, True):
                try:
                    player.send_toast(title, message)
                except:
                    pass

    def handle_command(self, player: Player, action: str = "") -> bool:
        if not action or action == "help":
            player.send_message(self.config.t("prefix", "") + self.config.get_message("help_message"))
            return True

        if action == "tps":
            player.send_message(
                self.config.t("prefix", "") + self.config.get_message("tps_info", f"{self.current_tps:.2f}")
            )
            return True

        if action == "status":
            status = self.state.phase
            if self.state.low_tps_retry_time > time.time() * 1000:
                status += " (TPS清理长冷却中)"
            player.send_message(self.config.t("prefix", "") + "状态: " + status)
            return True

        if action == "cancel":
            if self.state.phase == "scheduled":
                self.state.phase = "idle"
                self.plugin.server.broadcast_message(
                    self.config.t("prefix", "") + self.config.get_message("cancel_success")
                )
            else:
                player.send_message(
                    self.config.t("prefix", "") + "§c当前没有计划清理可取消"
                )
            return True

        if action == "now":
            self.schedule_clean(is_manual=True, player_name=player.name, is_low_tps=False)
            return True

        if action == "toast":
            xuid = player.xuid
            current = self.config.player_settings.get(xuid, True)
            self.config.player_settings[xuid] = not current
            self.config.save_player_settings()

            if self.config.player_settings[xuid]:
                player.send_message(
                    self.config.t("prefix", "") + self.config.get_message("toast_enabled", "§a您已开启清理系统的顶部弹窗通知")
                )
            else:
                player.send_message(
                    self.config.t("prefix", "") + self.config.get_message("toast_disabled", "§c您已关闭清理系统的顶部弹窗通知")
                )
            return True

        return False
