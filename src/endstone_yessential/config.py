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
            },
            "wh": {
                "EnableModule": True,
                "status": 0,
                "whmotdmsg": "服务器维护中，请勿进入！",
                "whgamemsg": "服务器正在维护中，请您稍后再来!"
            },
            "Hub": {
                "EnabledModule": True,
                "x": 0,
                "y": -60,
                "z": 0,
                "dimid": 0
            },
            "CrossServerTransfer": {
                "EnabledModule": True,
                "servers": [
                    {"server_name": "生存服", "server_ip": "127.0.0.1", "server_port": 19132}
                ]
            },
            "Motd": {
                "Enabled": True,
                "message": [
                    "§6YEssential §a服务器正在运行中！",
                    "§e欢迎来到 §bMinecraft §a服务器！"
                ],
                "interval": 5000
            },
            "Fcam": {
                "EnableModule": False,
                "CostMoney": 0,
                "TimeOut": 300
            },
            "RedPacket": {
                "EnabledModule": False,
                "minAmount": 1,
                "maxAmount": 10000,
                "maxCount": 100,
                "expireTime": 300
            },
            "Crash": {
                "EnabledModule": False,
                "LogCrashInfo": True
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        return self.config_data.get(key, default)

    def set(self, key: str, value: Any):
        self.config_data[key] = value
        self.save_config()

    def get_config(self) -> Dict[str, Any]:
        return self.config_data
