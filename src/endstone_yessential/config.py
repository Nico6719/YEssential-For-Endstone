"""
YEssential ConfigManager - 配置管理
加载/保存/合并配置文件, 自动迁移旧版本配置(追加缺失key)
"""
import os
import json
from typing import Any, Dict

from .log import plugin_print
from .constant import plugin_version
from .i18n import tr


class ConfigManager:
    def __init__(self, plugin):
        self.plugin = plugin
        self.data_folder = str(plugin.data_folder)
        self.config_path = os.path.join(self.data_folder, "config.json")
        self.config_data: Dict[str, Any] = {}

    # ═══════════════════════════════════════════════════════════
    # 版本号比较
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def _parse_version(v: str) -> tuple:
        """'0.1.0' → (0, 1, 0), 非法则返回 (0,)"""
        try:
            return tuple(int(x) for x in str(v).split("."))
        except Exception:
            return (0,)

    # ═══════════════════════════════════════════════════════════
    # 加载 / 保存 / 迁移
    # ═══════════════════════════════════════════════════════════

    def load_config(self):
        os.makedirs(self.data_folder, exist_ok=True)

        if not os.path.exists(self.config_path):
            self.config_data = self.get_default_config()
            self.config_data["config_version"] = plugin_version
            self.save_config()
            plugin_print(tr("config.created", plugin_version))
        else:
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    raw = f.read().strip()
                    if not raw:  # 空文件 → 重建
                        raise ValueError("Empty config")
                    loaded = json.loads(raw)

                old_ver = loaded.get("config_version", "0")
                # 无论版本是否一致，始终执行迁移（默认打底 + 旧key映射 + 补齐缺失）
                self.config_data = self._migrate(loaded, old_ver)
                if self._parse_version(old_ver) < self._parse_version(plugin_version):
                    plugin_print(tr("config.migrated", old_ver, plugin_version))
                self.save_config()
            except Exception as e:
                plugin_print(tr("config.recovering", str(e)), "WARNING")
                self.config_data = self.get_default_config()
                self.config_data["config_version"] = plugin_version
                self.save_config()

    def save_config(self):
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            plugin_print(tr("config.save_failed", str(e)))

    def _migrate(self, loaded: dict, old_version: str) -> dict:
        """
        版本迁移：以默认配置为底，用户已有值覆盖。
        这样新增的 key 自动出现，用户改过的值保持不变。
        """
        defaults = self.get_default_config()
        migrated = self._deep_merge(defaults, loaded)
        migrated["config_version"] = plugin_version
        # 清理旧版可能遗留的无效字段
        migrated.pop("version", None)
        return migrated

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """深度合并：override 覆盖 base，base 中不存在的 key 保留"""
        result = base.copy()
        for key, value in override.items():
            if key == "config_version":
                continue  # 版本号由迁移逻辑控制
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    # ═══════════════════════════════════════════════════════════
    # 默认配置 (每次新增配置项后手动 +1 CONFIG_VERSION)
    # ═══════════════════════════════════════════════════════════

    def get_default_config(self) -> Dict[str, Any]:
        return {
            "config_version": plugin_version,
            "Language": "zh_CN",

            # ═══════════════════════════════════════════════════
            # Economy — 经济系统
            # ═══════════════════════════════════════════════════
            "Economy": {
                "mode": "scoreboard",          # "scoreboard" | "llmoney"
                "Scoreboard": "money",
                "CoinName": "金币",
                "RankingModel": "New",         # "New" | "Simple"
                "PayTaxRate": 0                # 0=免税, 数字=单一税率, 数组=阶梯税率
            },

            # ═══════════════════════════════════════════════════
            # RTP — 随机传送
            # ═══════════════════════════════════════════════════
            "RTP": {
                "EnabledModule": True,
                "maxRadius": 5000,
                "minRadius": 100,
                "cost": 0,
                "cooldown": 0,
                "animation": 0
            },

            # ═══════════════════════════════════════════════════
            # Home — 家园系统
            # ═══════════════════════════════════════════════════
            "Home": {
                "EnabledModule": True,
                "max_homes": 5
            },

            # ═══════════════════════════════════════════════════
            # Warp — 传送点系统
            # ═══════════════════════════════════════════════════
            "Warp": {
                "EnabledModule": True
            },

            # ═══════════════════════════════════════════════════
            # TPA — 传送请求
            # ═══════════════════════════════════════════════════
            "tpa": {
                "EnabledModule": True,
                "timeout": 60
            },

            # ═══════════════════════════════════════════════════
            # Hub — 回城系统
            # ═══════════════════════════════════════════════════
            "Hub": {
                "EnabledModule": True,
                "x": 0, "y": -60, "z": 0,
                "dimid": 0
            },

            # ═══════════════════════════════════════════════════
            # Motd — 服务器标题轮播
            # ═══════════════════════════════════════════════════
            "Motd": {
                "EnabledModule": True,
                "message": [
                    "§6YEssential §a服务器正在运行中！",
                    "§e欢迎来到 §bMinecraft §a服务器！"
                ],
                "interval": 5000
            },

            # ═══════════════════════════════════════════════════
            # PVP — PVP 防护
            # ═══════════════════════════════════════════════════
            "PVP": {
                "EnabledModule": True
            },

            # ═══════════════════════════════════════════════════
            # Fcam — 灵魂出窍
            # ═══════════════════════════════════════════════════
            "Fcam": {
                "EnableModule": False,
                "CostMoney": 0,
                "TimeOut": 300
            },

            # ═══════════════════════════════════════════════════
            # RedPacket — 红包系统
            # ═══════════════════════════════════════════════════
            "RedPacket": {
                "EnabledModule": False,
                "minAmount": 1,
                "maxAmount": 10000,
                "maxCount": 100,
                "expireTime": 300
            },

            # ═══════════════════════════════════════════════════
            # Crash — 崩溃模块
            # ═══════════════════════════════════════════════════
            "Crash": {
                "EnabledModule": False,
                "LogCrashInfo": True
            },

            # ═══════════════════════════════════════════════════
            # Sign — 每日签到
            # ═══════════════════════════════════════════════════
            "Sign": {
                "enable": True,
                "gui_arrange": 3,
                "random_money": {"min_money": 1000, "max_money": 10000},
                "random_exp": {"min_exp": 100, "max_exp": 1000},
                "reward": [
                    "item_1", "item_2", "money_1000", "money_1000", "random_money",
                    "item_1", "money_1000", "item_3", "item_4", "random_money",
                    "item_1", "item_2", "money_2000", "item_3", "random_money",
                    "item_4", "money_1000", "item_1", "random_exp", "item_2",
                    "money_1000", "item_3", "item_4", "random_money", "money_2000",
                    "item_1", "item_2", "random_exp", "money_1000", "item_3", "item_4"
                ],
                "addition": {
                    "3": "item_1", "5": "money_500", "7": "item_2",
                    "15": "item_2", "30": "money_2000"
                }
            },

            # ═══════════════════════════════════════════════════
            # Maintenance — 维护模式
            # ═══════════════════════════════════════════════════
            "wh": {
                "EnableModule": True,
                "status": 0,
                "whmotdmsg": "服务器维护中，请勿进入！",
                "whgamemsg": "服务器正在维护中，请您稍后再来!"
            },

            # ═══════════════════════════════════════════════════
            # Suicide — 自杀系统
            # ═══════════════════════════════════════════════════
            "suicide": {
                "enable": True,
                "cooldown": 5
            },

            # ═══════════════════════════════════════════════════
            # CrossServer — 跨服传送
            # ═══════════════════════════════════════════════════
            "CrossServerTransfer": {
                "EnabledModule": True,
                "servers": [
                    {"server_name": "生存服", "server_ip": "127.0.0.1", "server_port": 19132}
                ]
            },

            # ═══════════════════════════════════════════════════
            # Update — 更新检查
            # ═══════════════════════════════════════════════════
            "Update": {
                "EnableModule": True,
                "CheckInterval": 60
            },

            # ═══════════════════════════════════════════════════
            # Settings — 全局设置
            # ═══════════════════════════════════════════════════
            "KeepInventory": True,
            "BackTipAfterDeath": True,
            "CustomStopMessage": True,
            "SimpleLogOutPut": False,
        }

    # ═══════════════════════════════════════════════════════════
    # 便捷 API
    # ═══════════════════════════════════════════════════════════

    def get(self, key: str, default: Any = None) -> Any:
        return self.config_data.get(key, default)

    def set(self, key: str, value: Any):
        self.config_data[key] = value
        self.save_config()

    def get_config(self) -> Dict[str, Any]:
        return self.config_data
