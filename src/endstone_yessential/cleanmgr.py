"""
YEssential Cleanmgr - 实体清理系统
"""
import json, os, re, time, threading
from typing import Dict
from endstone import Player
from .i18n import tr


class CleanmgrSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.config_path = "./plugins/YEssential/config/cleanmgr/config.json"
        self.player_settings_path = "./plugins/YEssential/data/CleanmgrSettingData.json"
        self._config = {}
        self.player_settings: Dict[str, bool] = {}
        self.whitelist_regex: list = []
        self.state_phase = "idle"
        self.scheduled_timeouts: list = []
        self.last_player_clean: Dict[str, float] = {}
        self.low_tps_clean_count = 0
        self.low_tps_retry_time = 0
        self.tps_before_clean = 20.0
        self.is_low_tps_trigger = False
        self.current_tps = 20.0
        self._ensure_dirs()
        self._load_config()
        self._load_player_settings()
        self._compile_whitelist()
        self._start_tps_sampler()
        self._start_timers()

    def _ensure_dirs(self):
        for p in (self.config_path, self.player_settings_path):
            os.makedirs(os.path.dirname(p), exist_ok=True)

    def _load_config(self):
        default = {
            "enable": True, "interval": 600, "debug": False,
            "whitelist": [
                "^minecraft:netherite_", "^minecraft:dragon_egg$", "^minecraft:nether_star$",
                "^minecraft:elytra$", "^minecraft:emerald$", "^minecraft:beacon$",
                "^minecraft:ender_eye$", "^minecraft:shulker_box$", "^minecraft:enchanted_book$",
                "^minecraft:diamond", "^minecraft:totem_of_undying$", "^minecraft:ender_pearl$",
                "^minecraft:ender_crystal$", "^minecraft:ender_dragon$", "^minecraft:armor_stand$",
                "^minecraft:boat$", "^minecraft:painting$"
            ],
            "notice": {"notice1": 30, "notice2": 15, "notice3": 5},
            "LowTpsClean": {"enable": True, "minimum": 15, "maxConsecutiveCleans": 2, "longCooldown": 450},
            "playerCooldown": 300
        }
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    raw = json.load(f)
                self._config = raw.get("cleanmgr", default)
            else:
                self._config = default
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump({"cleanmgr": default}, f, indent=2, ensure_ascii=False)
        except Exception:
            self._config = default

    def _load_player_settings(self):
        try:
            if os.path.exists(self.player_settings_path):
                with open(self.player_settings_path, 'r', encoding='utf-8') as f:
                    self.player_settings = json.load(f)
        except Exception:
            self.player_settings = {}

    def _save_player_settings(self):
        try:
            with open(self.player_settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.player_settings, f, indent=2)
        except Exception:
            pass

    def _compile_whitelist(self):
        self.whitelist_regex = []
        for pat in self._config.get("whitelist", []):
            try:
                self.whitelist_regex.append(re.compile(pat))
            except Exception:
                pass

    def _start_tps_sampler(self):
        def sample():
            while True:
                time.sleep(1)
                try:
                    self.current_tps = self.plugin.server.current_tps
                except Exception:
                    pass
        threading.Thread(target=sample, daemon=True).start()

    def _start_timers(self):
        interval = self._config.get("interval", 600)

        def scheduled_clean():
            while True:
                time.sleep(interval)
                if self._config.get("enable", True) and self.state_phase == "idle":
                    self.schedule_clean(False, "", False)

        threading.Thread(target=scheduled_clean, daemon=True).start()

        def tps_check():
            while True:
                time.sleep(5)
                cfg = self._config.get("LowTpsClean", {})
                if not cfg.get("enable", True):
                    continue
                if time.time() * 1000 < self.low_tps_retry_time:
                    continue
                if self.current_tps <= cfg.get("minimum", 15) and self.state_phase == "idle":
                    self.tps_before_clean = self.current_tps
                    self.plugin.server.broadcast_message(
                        tr("cleanmgr.prefix") + tr("cleanmgr.low_tps_clean", f"{self.current_tps:.2f}")
                    )
                    self.schedule_clean(False, "", True)

        threading.Thread(target=tps_check, daemon=True).start()

    def _should_keep(self, entity) -> bool:
        try:
            if entity.type == "minecraft:player":
                return True
        except Exception:
            pass
        try:
            for rgx in self.whitelist_regex:
                if rgx.search(entity.type):
                    return True
        except Exception:
            pass
        return False

    def _execute_clean(self):
        self.state_phase = "cleaning"

        def do_cleanup():
            removed = 0
            self.plugin.server.broadcast_message(
                tr("cleanmgr.prefix") + tr("cleanmgr.cleanup_start")
            )
            entities_to_remove = []
            try:
                for dim in self.plugin.server.level.dimensions:
                    for entity in dim.actors:
                        if not self._should_keep(entity):
                            entities_to_remove.append(entity)
            except Exception as e:
                self.plugin.logger.error(f"cleanmgr: {e}")

            for entity in entities_to_remove:
                try:
                    entity.remove()
                    removed += 1
                except Exception:
                    pass

            self.plugin.server.broadcast_message(
                tr("cleanmgr.prefix") + tr("cleanmgr.cleanup_complete", removed)
            )
            self._send_toast(tr("cleanmgr.toast_title"), tr("cleanmgr.cleanup_complete", removed))
            self.state_phase = "idle"

        self.plugin.server.scheduler.run_task(self.plugin, do_cleanup)

        if self.is_low_tps_trigger:
            def evaluate():
                time.sleep(5)
                improved = self.current_tps > (self.tps_before_clean + 2.0)
                cfg = self._config.get("LowTpsClean", {})
                if improved:
                    self.low_tps_clean_count = 0
                else:
                    self.low_tps_clean_count += 1
                    if self.low_tps_clean_count >= cfg.get("maxConsecutiveCleans", 2):
                        cool = round(cfg.get("longCooldown", 450) / 60)
                        self.plugin.server.broadcast_message(
                            tr("cleanmgr.prefix") + tr("cleanmgr.low_tps_ineffective", cool)
                        )
                        self.low_tps_retry_time = time.time() * 1000 + cfg.get("longCooldown", 450) * 1000
                        self.low_tps_clean_count = 0
                self.is_low_tps_trigger = False
            threading.Thread(target=evaluate, daemon=True).start()

    def schedule_clean(self, is_manual=False, player_name="", is_low_tps=False):
        if self.state_phase != "idle":
            return

        if is_manual and player_name:
            now = time.time()
            last = self.last_player_clean.get(player_name, 0)
            if (now - last) < self._config.get("playerCooldown", 300):
                p = self.plugin.server.get_player(player_name)
                if p:
                    p.send_message(tr("cleanmgr.prefix") + tr("cleanmgr.cooldown_msg"))
                return
            self.last_player_clean[player_name] = now
            self.plugin.server.broadcast_message(
                tr("cleanmgr.prefix") + tr("cleanmgr.manual_trigger")
            )

        self.state_phase = "scheduled"
        self.is_low_tps_trigger = is_low_tps
        notice = self._config.get("notice", {})
        n1, n2, n3 = notice.get("notice1", 30), notice.get("notice2", 15), notice.get("notice3", 5)

        def send1():
            self.plugin.server.broadcast_message(
                tr("cleanmgr.prefix") + tr("cleanmgr.cleanup_notice", n1)
            )
            self._send_toast(tr("cleanmgr.toast_title"), tr("cleanmgr.cleanup_notice", n1))
        self.plugin.server.scheduler.run_task(self.plugin, send1)

        if n2 > 0 and n2 < n1:
            def notice2():
                time.sleep(n1 - n2)
                if self.state_phase == "scheduled":
                    def s2():
                        self.plugin.server.broadcast_message(
                            tr("cleanmgr.prefix") + tr("cleanmgr.cleanup_notice2", n2)
                        )
                        self._send_toast(tr("cleanmgr.toast_title"), tr("cleanmgr.cleanup_notice2", n2))
                    self.plugin.server.scheduler.run_task(self.plugin, s2)
            threading.Thread(target=notice2, daemon=True).start()

        if n3 > 0 and n3 < n2:
            def notice3():
                time.sleep(n1 - n3)
                if self.state_phase == "scheduled":
                    def s3():
                        self.plugin.server.broadcast_message(
                            tr("cleanmgr.prefix") + tr("cleanmgr.cleanup_notice3", n3)
                        )
                        self._send_toast(tr("cleanmgr.toast_title"), tr("cleanmgr.cleanup_notice3", n3))
                    self.plugin.server.scheduler.run_task(self.plugin, s3)
            threading.Thread(target=notice3, daemon=True).start()

        def do_clean():
            time.sleep(n1)
            self.plugin.server.scheduler.run_task(self.plugin, self._execute_clean)
        threading.Thread(target=do_clean, daemon=True).start()

    def _send_toast(self, title: str, msg: str):
        def st():
            for p in self.plugin.server.online_players:
                if self.player_settings.get(p.xuid, True):
                    try:
                        p.send_toast(title, msg)
                    except Exception:
                        pass
        self.plugin.server.scheduler.run_task(self.plugin, st)

    def handle_command(self, player: Player, action: str = "") -> bool:
        if not action or action == "help":
            player.send_message(tr("cleanmgr.prefix") + tr("cleanmgr.help"))
            return True
        if action == "tps":
            player.send_message(tr("cleanmgr.prefix") + tr("cleanmgr.tps_info", f"{self.current_tps:.2f}"))
            return True
        if action == "status":
            s = self.state_phase
            if self.low_tps_retry_time > time.time() * 1000:
                s += " (TPS清理长冷却中)"
            player.send_message(tr("cleanmgr.prefix") + tr("cleanmgr.status", s))
            return True
        if action == "cancel":
            if self.state_phase == "scheduled":
                self.state_phase = "idle"
                self.plugin.server.broadcast_message(tr("cleanmgr.prefix") + tr("cleanmgr.cancel_success"))
            else:
                player.send_message(tr("cleanmgr.prefix") + tr("cleanmgr.no_scheduled"))
            return True
        if action == "now":
            self.schedule_clean(True, player.name)
            return True
        if action == "toast":
            xuid = player.xuid
            cur = self.player_settings.get(xuid, True)
            self.player_settings[xuid] = not cur
            self._save_player_settings()
            player.send_message(tr("cleanmgr.prefix") + tr("cleanmgr.toast_toggle", "§a已开启" if self.player_settings[xuid] else "§c已关闭"))
            return True
        return False
