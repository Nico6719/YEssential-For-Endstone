import time
from typing import Dict, List, Optional
from endstone import Player, Location

class BackSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.server = plugin.server
        self.death_locations = {}  # 玩家死亡位置记录
    
    def record_death_location(self, player: Player):
        """记录玩家死亡位置"""
        if not self.plugin.is_module_enabled("Back"):
            return
        
        location = player.location
        death_record = {
            "x": location.x,
            "y": location.y,
            "z": location.z,
            "dimension": location.dimension,
            "world": location.world.name if location.world else "overworld",
            "timestamp": time.time(),
            "time_str": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if player.name not in self.death_locations:
            self.death_locations[player.name] = []
        
        # 添加到记录列表
        self.death_locations[player.name].append(death_record)
        
        # 限制记录数量
        max_history = self.plugin.config_manager.get("Back.max_history", 3)
        if len(self.death_locations[player.name]) > max_history:
            self.death_locations[player.name] = self.death_locations[player.name][-max_history:]
        
        # 发送提示消息
        player.send_message(self.plugin.get_text("back.recorded"))
    
    def teleport_to_death_location(self, player: Player, death_index: int = -1) -> bool:
        """传送到死亡位置"""
        if not self.plugin.is_module_enabled("Back"):
            player.send_message(self.plugin.get_text("module.no.enabled"))
            return False
        
        if player.name not in self.death_locations or not self.death_locations[player.name]:
            player.send_message(self.plugin.get_text("back.empty"))
            return False
        
        # 检查费用
        cost = self.plugin.config_manager.get("Back.cost", 0)
        if cost > 0 and not self.plugin.economy.reduce_balance(player, cost):
            player.send_message(self.plugin.get_text("economy.no.enough"))
            return False
        
        # 获取死亡记录
        death_records = self.death_locations[player.name]
        if death_index < 0:
            death_index = len(death_records) + death_index
        
        if death_index < 0 or death_index >= len(death_records):
            player.send_message(self.plugin.get_text("back.invalid_index"))
            return False
        
        death_record = death_records[death_index]
        
        try:
            # 创建位置对象
            world = self.server.get_world(death_record.get("world", "overworld"))
            location = Location(
                x=death_record["x"],
                y=death_record["y"],
                z=death_record["z"],
                world=world,
                dimension=death_record.get("dimension", 0)
            )
            
            # 执行传送
            player.teleport(location)
            player.send_message(self.plugin.get_text("back.success"))
            
            # 添加保护效果
            player.add_effect("resistance", 15, 255, True)
            
            return True
            
        except Exception as e:
            self.plugin.logger.error(f"死亡回溯传送失败: {e}")
            player.send_message(self.plugin.get_text("back.failed"))
            return False
    
    def get_death_history(self, player: Player) -> List[Dict]:
        """获取玩家死亡历史"""
        return self.death_locations.get(player.name, [])
    
    def show_death_tip(self, player: Player):
        """显示死亡回溯提示"""
        if not self.plugin.config_manager.get("Back.tip_after_death", True):
            return
        
        if player.name in self.death_locations and self.death_locations[player.name]:
            player.send_message(self.plugin.get_text("back.tip"))
    
    def open_back_gui(self, player: Player):
        """打开死亡回溯GUI"""
        death_history = self.get_death_history(player)
        
        if not death_history:
            player.send_message(self.plugin.get_text("back.empty"))
            return
        
        from endstone import SimpleForm
        form = SimpleForm()
        form.title = self.plugin.get_text("back.gui.title")
        form.content = self.plugin.get_text("back.gui.select")
        
        for i, record in enumerate(death_history):
            time_str = record.get("time_str", "未知时间")
            form.add_button(
                f"死亡点 {i+1}\n{time_str}\n({record['x']:.1f}, {record['y']:.1f}, {record['z']:.1f})",
                callback=lambda p, data, idx=i: self._confirm_teleport_back(p, idx)
            )
        
        player.send_form(form)
    
    def _confirm_teleport_back(self, player: Player, death_index: int):
        """确认传送到死亡点"""
        death_history = self.get_death_history(player)
        if death_index >= len(death_history):
            return
        
        record = death_history[death_index]
        cost = self.plugin.config_manager.get("Back.cost", 0)
        
        from endstone import CustomForm
        form = CustomForm()
        form.title = self.plugin.get_text("back.gui.confirm.title")
        
        form.add_label(self.plugin.get_text("back.gui.confirm.death_point", index=death_index+1))
        form.add_label(self.plugin.get_text("back.gui.confirm.position", 
                                           x=record["x"], 
                                           y=record["y"], 
                                           z=record["z"]))
        form.add_label(self.plugin.get_text("back.gui.confirm.time", time=record.get("time_str", "未知")))
        form.add_label(self.plugin.get_text("back.gui.confirm.cost", cost=cost))
        form.add_label(self.plugin.get_text("economy.balance", balance=self.plugin.economy.get_balance(player)))
        
        def callback(p, data):
            if data is not None:
                self.teleport_to_death_location(p, death_index)
        
        player.send_form(form, callback)
