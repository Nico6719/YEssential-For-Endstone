import json
import os
from typing import Any, Dict

class ConfigManager:
    def __init__(self, plugin):
        self.plugin = plugin
        self.config = {}
        self.default_config = {
            "version": "2.5.4",
            "AutoUpdate": True,
            "Language": "zh_cn",
            
            # 经济系统
            "Economy": {
                "enabled": True,
                "system": "scoreboard",  # scoreboard 或 llmoney
                "scoreboard_name": "money",
                "PayTaxRate": 0,
                "ranking_enabled": True,
                "ranking_model": 1
            },
            
            # 家园系统
            "Home": {
                "enabled": True,
                "max_homes": 10,
                "add_cost": 0,
                "del_cost": 0,
                "tp_cost": 0
            },
            
            # 传送点系统
            "Warp": {
                "enabled": True,
                "cost": 0
            },
            
            # 随机传送
            "RTP": {
                "enabled": True,
                "cost": 50,
                "cooldown": 300,
                "min_radius": 100,
                "max_radius": 5000,
                "animation": False,
                "allowed_dimensions": [0]  # 0=主世界
            },
            
            # 玩家传送
            "TPA": {
                "enabled": True,
                "delay_enabled": True,
                "max_delay": 20,
                "request_timeout": 60,
                "prompt_type": "form"  # form 或 bossbar
            },
            
            # 红包系统
            "RedPacket": {
                "enabled": True,
                "expire_time": 300,
                "max_amount": 10000,
                "max_count": 50,
                "min_amount": 1
            },
            
            # PVP系统
            "PVP": {
                "enabled": True,
                "default_enabled": False
            },
            
            # 死亡回溯
            "Back": {
                "enabled": True,
                "cost": 0,
                "tip_after_death": True,
                "max_history": 3
            },
            
            # 公告系统
            "Notice": {
                "enabled": True,
                "show_on_join": True,
                "force_show_on_update": True
            },
            
            # 中心传送
            "Hub": {
                "enabled": True,
                "x": 0,
                "y": 100,
                "z": 0,
                "dimension": 0,
                "is_set": False
            },
            
            # 自杀系统
            "Suicide": {
                "enabled": True,
                "cost": 0
            },
            
            # 自动清理
            "AutoClean": {
                "enabled": True,
                "interval": 60,
                "batch_size": 200,
                "warn_times": [30, 15, 10, 5, 3, 2, 1],
                "trigger_amount": 2000
            },
            
            # 其他设置
            "KeepInventory": False,
            "OptimizeXporb": False,
            "join_notice": True,
            "Motd": {
                "enabled": False,
                "messages": ["Bedrock_Server", "Geyser"],
                "interval": 5
            }
        }
    
    def load_config(self):
        """加载配置"""
        config_path = os.path.join(self.plugin.data_folder, "config.json")
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config = self._merge_configs(self.default_config, loaded_config)
            else:
                self.config = self.default_config.copy()
                self.save_config()
            
            self.plugin.logger.info("配置文件加载完成")
            
        except Exception as e:
            self.plugin.logger.error(f"加载配置文件失败: {e}")
            self.config = self.default_config.copy()
    
    def save_config(self):
        """保存配置"""
        config_path = os.path.join(self.plugin.data_folder, "config.json")
        
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            self.plugin.logger.info("配置文件保存完成")
            
        except Exception as e:
            self.plugin.logger.error(f"保存配置文件失败: {e}")
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """合并配置（深度合并）"""
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result:
                if isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._merge_configs(result[key], value)
                else:
                    result[key] = value
            else:
                result[key] = value
        
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        
        # 导航到父级
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
        self.save_config()
    
    def reload(self):
        """重新加载配置"""
        self.load_config()
