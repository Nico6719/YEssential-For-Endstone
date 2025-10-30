import os
import json
from typing import Dict, List, Optional
from endstone import Player, Location

class HomeSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.server = plugin.server
        self.player_homes = {}
    
    def set_home(self, player: Player, home_name: str) -> bool:
        """设置家"""
        if not self.plugin.is_module_enabled("Home"):
            player.send_message(self.plugin.get_text("module.no.enabled"))
            return False
        
        # 检查费用
        cost = self.plugin.config_manager.get("Home.add_cost", 0)
        if cost > 0 and not self.plugin.economy.reduce_balance(player, cost):
            player.send_message(self.plugin.get_text("economy.no.enough"))
            return False
        
        # 检查数量限制
        max_homes = self.plugin.config_manager.get("Home.max_homes", 10)
        homes = self.get_player_homes(player)
        if len(homes) >= max_homes:
            player.send_message(self.plugin.get_text("home.set.max", max=max_homes))
            return False
        
        # 检查名称是否存在
        if home_name in homes:
            player.send_message(self.plugin.get_text("home.set.exists"))
            return False
        
        # 记录家的位置
        location = player.location
        homes[home_name] = {
            "x": location.x,
            "y": location.y,
            "z": location.z,
            "dimension": location.dimension,
            "world": location.world.name if location.world else "overworld",
            "timestamp": self.plugin.server.get_tick()
        }
        
        self.player_homes[player.name] = homes
        player.send_message(self.plugin.get_text("home.set.success", name=home_name))
        
        # 保存数据
        self._save_player_homes(player)
        return True
    
    def delete_home(self, player: Player, home_name: str) -> bool:
        """删除家"""
        if not self.plugin.is_module_enabled("Home"):
            player.send_message(self.plugin.get_text("module.no.enabled"))
            return False
        
        # 检查费用
        cost = self.plugin.config_manager.get("Home.del_cost", 0)
        if cost > 0 and not self.plugin.economy.reduce_balance(player, cost):
            player.send_message(self.plugin.get_text("economy.no.enough"))
            return False
        
        homes = self.get_player_homes(player)
        if home_name not in homes:
            player.send_message(self.plugin.get_text("home.del.failed"))
            return False
        
        del homes[home_name]
        self.player_homes[player.name] = homes
        player.send_message(self.plugin.get_text("home.del.success", name=home_name))
        
        # 保存数据
        self._save_player_homes(player)
        return True
    
    def teleport_home(self, player: Player, home_name: str) -> bool:
        """传送回家"""
        if not self.plugin.is_module_enabled("Home"):
            player.send_message(self.plugin.get_text("module.no.enabled"))
            return False
        
        # 检查费用
        cost = self.plugin.config_manager.get("Home.tp_cost", 0)
        if cost > 0 and not self.plugin.economy.reduce_balance(player, cost):
            player.send_message(self.plugin.get_text("economy.no.enough"))
            return False
        
        homes = self.get_player_homes(player)
        if home_name not in homes:
            player.send_message(self.plugin.get_text("home.tp.failed"))
            return False
        
        home_data = homes[home_name]
        
        try:
            # 创建位置对象
            world = self.server.get_world(home_data.get("world", "overworld"))
            location = Location(
                x=home_data["x"],
                y=home_data["y"],
                z=home_data["z"],
                world=world,
                dimension=home_data.get("dimension", 0)
            )
            
            # 执行传送
            player.teleport(location)
            player.send_message(self.plugin.get_text("home.tp.success", name=home_name))
            return True
            
        except Exception as e:
            self.plugin.logger.error(f"传送回家失败: {e}")
            player.send_message(self.plugin.get_text("home.tp.failed"))
            return False
    
    def get_player_homes(self, player: Player) -> Dict:
        """获取玩家的所有家"""
        if player.name not in self.player_homes:
            # 尝试从文件加载
            self._load_player_homes(player)
        
        return self.player_homes.get(player.name, {})
    
    def list_homes(self, player: Player) -> List[str]:
        """列出玩家的所有家名称"""
        homes = self.get_player_homes(player)
        return list(homes.keys())
    
    def open_home_gui(self, player: Player):
        """打开家园系统GUI"""
        from endstone import SimpleForm
        
        form = SimpleForm()
        form.title = self.plugin.get_text("home.gui.title")
        
        form.add_button(self.plugin.get_text("home.gui.tp"), callback=lambda p, _: self._open_tp_home_gui(p))
        form.add_button(self.plugin.get_text("home.gui.add"), callback=lambda p, _: self._open_add_home_gui(p))
        form.add_button(self.plugin.get_text("home.gui.del"), callback=lambda p, _: self._open_del_home_gui(p))
        form.add_button(self.plugin.get_text("home.gui.list"), callback=lambda p, _: self._show_home_list(p))
        
        player.send_form(form)
    
    def _open_tp_home_gui(self, player: Player):
        """打开传送回家GUI"""
        from endstone import SimpleForm
        
        homes = self.get_player_homes(player)
        if not homes:
            player.send_message(self.plugin.get_text("home.list.empty"))
            return
        
        form = SimpleForm()
        form.title = self.plugin.get_text("home.gui.tp.title")
        form.content = self.plugin.get_text("home.gui.tp.select")
        
        for home_name in homes:
            home_data = homes[home_name]
            form.add_button(
                f"{home_name}\n({home_data['x']:.1f}, {home_data['y']:.1f}, {home_data['z']:.1f})",
                callback=lambda p, data, name=home_name: self.teleport_home(p, name)
            )
        
        player.send_form(form)
    
    def _open_add_home_gui(self, player: Player):
        """打开添加家GUI"""
        from endstone import CustomForm
        
        form = CustomForm()
        form.title = self.plugin.get_text("home.gui.add.title")
        
        form.add_label(self.plugin.get_text("home.gui.add.current_pos", 
                                           x=player.location.x, 
                                           y=player.location.y, 
                                           z=player.location.z))
        form.add_label(self.plugin.get_text("home.gui.add.cost", 
                                           cost=self.plugin.config_manager.get("Home.add_cost", 0)))
        form.add_label(self.plugin.get_text("economy.balance", 
                                           balance=self.plugin.economy.get_balance(player)))
        form.add_input(self.plugin.get_text("home.gui.add.name"), "my_home")
        
        def callback(p, data):
            if not data or not data[3]:
                return
            
            home_name = data[3].strip()
            if not home_name:
                p.send_message(self.plugin.get_text("home.gui.add.invalid_name"))
                return
            
            self.set_home(p, home_name)
        
        player.send_form(form, callback)
    
    def _open_del_home_gui(self, player: Player):
        """打开删除家GUI"""
        from endstone import SimpleForm
        
        homes = self.get_player_homes(player)
        if not homes:
            player.send_message(self.plugin.get_text("home.list.empty"))
            return
        
        form = SimpleForm()
        form.title = self.plugin.get_text("home.gui.del.title")
        form.content = self.plugin.get_text("home.gui.del.select")
        
        for home_name in homes:
            home_data = homes[home_name]
            form.add_button(
                f"{home_name}\n({home_data['x']:.1f}, {home_data['y']:.1f}, {home_data['z']:.1f})",
                callback=lambda p, data, name=home_name: self._confirm_delete_home(p, name)
            )
        
        player.send_form(form)
    
    def _confirm_delete_home(self, player: Player, home_name: str):
        """确认删除家"""
        from endstone import CustomForm
        
        form = CustomForm()
        form.title = self.plugin.get_text("home.gui.del.confirm.title")
        
        form.add_label(self.plugin.get_text("home.gui.del.confirm.warning", name=home_name))
        form.add_label(self.plugin.get_text("home.gui.del.cost", 
                                           cost=self.plugin.config_manager.get("Home.del_cost", 0)))
        form.add_label(self.plugin.get_text("economy.balance", 
                                           balance=self.plugin.economy.get_balance(player)))
        
        def callback(p, data):
            if data is not None:
                self.delete_home(p, home_name)
        
        player.send_form(form, callback)
    
    def _show_home_list(self, player: Player):
        """显示家列表"""
        homes = self.get_player_homes(player)
        
        if not homes:
            player.send_message(self.plugin.get_text("home.list.empty"))
            return
        
        from endstone import SimpleForm
        form = SimpleForm()
        form.title = self.plugin.get_text("home.gui.list.title")
        
        content = self.plugin.get_text("home.list.title") + "\n\n"
        for home_name, home_data in homes.items():
            content += f"§e{home_name}: §f({home_data['x']:.1f}, {home_data['y']:.1f}, {home_data['z']:.1f})\n"
        
        form.content = content
        player.send_form(form)
    
    def _load_player_homes(self, player: Player):
        """从文件加载玩家家数据"""
        try:
            player_file = os.path.join(self.plugin.data_folder, "players", f"{player.name}.json")
            if os.path.exists(player_file):
                with open(player_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.player_homes[player.name] = data.get("homes", {})
        except Exception as e:
            self.plugin.logger.error(f"加载玩家家数据失败 {player.name}: {e}")
            self.player_homes[player.name] = {}
    
    def _save_player_homes(self, player: Player):
        """保存玩家家数据到文件"""
        try:
            player_file = os.path.join(self.plugin.data_folder, "players", f"{player.name}.json")
            os.makedirs(os.path.dirname(player_file), exist_ok=True)
            
            # 读取现有数据
            data = {}
            if os.path.exists(player_file):
                with open(player_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            # 更新家数据
            data["homes"] = self.player_homes.get(player.name, {})
            
            # 保存数据
            with open(player_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.plugin.logger.error(f"保存玩家家数据失败 {player.name}: {e}")
