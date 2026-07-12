"""
YEssential Suicide System - 自杀系统
"""
import json, os, time
from typing import Dict
from .i18n import tr


class SuicideSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.config_path = "./plugins/YEssential/config/suicide/config.json"
        self._config = {}
        self.last_suicide: Dict[str, float] = {}
        self._ensure_dirs()
        self._load_config()

    def _ensure_dirs(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

    def _load_config(self):
        default = {"enable": True, "cooldown": 5}
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    raw = json.load(f)
                self._config = raw.get("suicide", default)
            else:
                self._config = default
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump({"suicide": default}, f, indent=2, ensure_ascii=False)
        except Exception:
            self._config = default

    def handle_command(self, player) -> bool:
        if not self._config.get("enable", True):
            player.send_message(tr("suicide.disabled"))
            return True

        now = time.time()
        last = self.last_suicide.get(player.name, 0)
        cd = self._config.get("cooldown", 5)
        if (now - last) < cd:
            player.send_message(tr("suicide.cooldown", int(cd - (now - last))))
            return True

        def do():
            try:
                if player.health > 0:
                    if hasattr(self.plugin, 'back'):
                        self.plugin.back.record_death(player)
                    player.health = 0
                    player.send_message(tr("suicide.killed"))
                    self.last_suicide[player.name] = time.time()
                else:
                    player.send_message(tr("suicide.already_dead"))
            except Exception as e:
                self.plugin.logger.error(f"suicide: {e}")

        self.plugin.server.scheduler.run_task(self.plugin, do)
        return True
