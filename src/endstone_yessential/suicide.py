import json
import os
import time
from typing import Dict

class SuicideConfig:
    def __init__(self, plugin):
        self.plugin = plugin
        self.config_path = "./plugins/YEssential/config/suicide/config.json"
        self.lang_path = "./plugins/YEssential/lang/suicide/lang.json"
        self._config = {}
        self._lang = {}
        self.ensure_directories()
        self.load()

    def ensure_directories(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.lang_path), exist_ok=True)

    def load(self):
        self._config = self.load_config()
        self._lang = self.load_lang()

    def load_lang(self) -> dict:
        default = {
            "prefix": "§l§6[-YEST-] §l§e[自杀系统] §r",
            "messages": {
                "kill_success": "§c你选择了结束自己的生命",
                "kill_fail": "§c自杀失败，你已死亡",
                "help_message": "§e用法:\n§a/suicide §7- 自杀"
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
            "suicide": {
                "enable": True,
                "cooldown": 5
            }
        }

        if not os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(default, f, indent=2, ensure_ascii=False)
            except:
                pass
            return default.get("suicide", {})

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                raw = json.load(f)
                return raw.get("suicide", {})
        except:
            return default.get("suicide", {})

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


class SuicideSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.config = SuicideConfig(plugin)
        self.last_suicide_time: Dict[str, float] = {}

    def handle_command(self, player):
        if not self.config.get("enable", True):
            player.send_message(
                self.config.t("prefix", "") + "§c自杀功能已禁用"
            )
            return True

        # 检查冷却时间
        now = time.time()
        last = self.last_suicide_time.get(player.name, 0)
        cooldown = self.config.get("cooldown", 5)
        if (now - last) < cooldown:
            remaining = int(cooldown - (now - last))
            player.send_message(
                self.config.t("prefix", "") + f"§c请等待 {remaining} 秒后再试"
            )
            return True

        # 在主线程上执行自杀操作
        def do_suicide():
            try:
                # 检查玩家是否存活（生命值大于0）
                if player.health > 0:
                    # 记录死亡位置，以便玩家可以使用/back命令返回
                    if hasattr(self.plugin, 'back'):
                        self.plugin.back.record_death(player)

                    # 将玩家生命值设置为0来实现自杀
                    player.health = 0
                    player.send_message(
                        self.config.t("prefix", "") + self.config.get_message("kill_success")
                    )
                    self.last_suicide_time[player.name] = time.time()
                else:
                    player.send_message(
                        self.config.t("prefix", "") + self.config.get_message("kill_fail")
                    )
            except Exception as e:
                self.plugin.logger.error(f"自杀操作失败: {e}")

        self.plugin.server.scheduler.run_task(self.plugin, do_suicide)
        return True
