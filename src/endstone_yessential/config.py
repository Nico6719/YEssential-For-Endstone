import os
import json
from typing import Any, Dict

from .log import plugin_print

class ConfigManager:
    def __init__(self, plugin):
        self.plugin = plugin
        self.data_folder = plugin.data_folder
        self.config_path = os.path.join(self.data_folder, "config.json")
        self.config_data: Dict[str, Any] = {}

    def load_config(self):
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        
        if not os.path.exists(self.config_path):
            self.config_data = self.get_default_config()
            self.save_config()
        else:
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config_data = json.load(f)
            except Exception as e:
                self.plugin.logger.error(f"Failed to load config: {e}")
                self.config_data = self.get_default_config()

    def save_config(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            plugin_print(f"Failed to save config: {e}")

    def get_default_config(self) -> Dict[str, Any]:
        return {
            "version": "2.10.0",
            "language": "zh_cn",
            "modules": {
                "tpa": True,
                "home": True,
                "warp": True,
                "economy": True,
                "pvp": True,
                "notice": True
            },
            "settings": {
                "tpa_timeout": 60,
                "max_homes": 5,
                "rtp_range": 5000
            },
            "RTP": {
                "maxRadius": 5000,
                "minRadius": 100,
                "cost": 0,
                "cooldown": 0,
                "animation": 0
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        return self.config_data.get(key, default)

    def set(self, key: str, value: Any):
        self.config_data[key] = value
        self.save_config()
