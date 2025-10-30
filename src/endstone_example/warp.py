import os
import json
from typing import Dict, List
from endstone import Player, Location

class WarpSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.server = plugin.server
        self.warps = {}
        self._load_warps()
    
    def create_warp(self, player: Player, warp_name: str) -> bool:
        """创建传送点"""
        if not self.plugin.is_module_enabled("Warp"):
            player.send_message(self.plugin.get_text("module.no.enabled"))
            return False
        
        if not player.has_permission("yessential.warp.create"):
            player.send_message(self.plugin.get_text("player.not.op"))
            return False
        
        if warp_name in self.warps:
            player.send_message(self.plugin.get_text("warp.exists"))
            return False
        
        location = player.location
        self.warps[warp_name] = {
            "x": location.x,
            "y": location.y,
            "z": location.z,
            "dimension": location.dimension,
            "world": location.world.name if location.world else "overworld",
            "creator": player.name,
            "created": self.plugin.server.get_tick()
        }
        
        self._save_warps()
        player.send_message(self.plugin.get_text("warp.create.success", name=warp_name))
        return True
    
    def delete_warp(self, player: Player, warp_name: str) -> bool:
        """删除传送点"""
        if not self.plugin.is_module_enabled("Warp"):
            player.send_message(self.plugin.get_text("module.no.enabled"))
            return False
        
        if not player.has_permission("yessential.warp.delete"):
            player.send_message(self.plugin.get_text("player.not.op"))
            return False
        
        if warp_name not in self.warps:
            player.send_message(self.plugin.get_text("warp.not_exists"))
            return False
        
        del self.warps[warp_name]
        self._save_warps()
        player.send_message(self.plugin.get_text("warp.delete.success", name=warp_name))
        return True
    
    def teleport_to_warp(self, player: Player, warp_name: str) -> bool:
        """传送到传送点"""
        if not self.plugin.is_module_enabled("Warp"):
            player.send_message(self.plugin.get_text("module.no.enabled"))
            return False
        
        if warp_name not in self.warps:
            player.send_message(self.plugin.get_text("warp.not_exists"))
            return False
        
        # 检查费用
        cost = self.plugin.config_manager.get("Warp.cost", 0)
        if cost > 0 and not self.plugin.economy.reduce_balance(player, cost):
            player.send_message(self.plugin.get_text("economy.no.enough"))
            return False
        
        warp_data = self.warps[warp_name]
        
        try:
            world = self.server.get_world(warp_data.get("world", "overworld"))
            location = Location(
                x=warp_data["x"],
                y=warp_data["y"],
                z=warp_data["z"],
                world=world,
                dimension=warp_data.get("dimension", 0)
            )
            
            player.teleport(location)
            player.send_message(self.plugin.get_text("warp.teleport.success", name=warp_name))
            return True
            
        except Exception as e:
            self.plugin.logger.error(f"传送到传送点失败: {e}")
            player.send_message(self.plugin.get_text("warp.teleport.failed"))
            return False
    
    def list_warps(self) -> List[str]:
        """获取所有传送点名称"""
        return list(self.warps.keys())
    
    def open_warp_gui(self, player: Player):
        """打开传送点GUI"""
        from endstone import SimpleForm
        
        form = SimpleForm()
        form.title = self.plugin.get_text("warp.gui.title")
        
        if player.has_permission("yessential.warp.manage"):
            # OP玩家显示管理选项
            form.add_button(self.plugin.get_text("warp.gui.add"), callback=lambda p, _: self._open_add_warp_gui(p))
            form.add_button(self.plugin.get_text("warp.gui.del"), callback=lambda p, _: self._open_del_warp_gui(p))
            form.add_button(self.plugin.get_text("warp.gui.list"), callback=lambda p, _: self._open_warp_list_gui(p))
        else:
            # 普通玩家只显示传送列表
            self._open_warp_list_gui(player)
    
    def _open_add_warp_gui(self, player: Player):
        """打开添加传送点GUI"""
        from endstone import CustomForm
        
        form = CustomForm()
        form.title = self.plugin.get_text("warp.gui.add.title")
        
        form.add_label(self.plugin.get_text("warp.gui.add.current_pos", 
                                           x=player.location.x, 
                                           y=player.location.y, 
                                           z=player.location.z))
        form.add_input(self.plugin.get_text("warp.gui.add.name"), "warp_name")
        
        def callback(p, data):
            if not data or not data[1]:
                return
            
            warp_name = data[1].strip()
            if not warp_name:
                p.send_message(self.plugin.get_text("warp.gui.add.invalid_name"))
                return
            
            self.create_warp(p, warp_name)
        
        player.send_form(form, callback)
    
    def _open_del_warp_gui(self, player: Player):
        """打开删除传送点GUI"""
        from endstone import SimpleForm
        
        warps = self.list_warps()
        if not warps:
            player.send_message(self.plugin.get_text("warp.list.empty"))
            return
        
        form = SimpleForm()
        form.title = self.plugin.get_text("warp.gui.del.title")
        form.content = self.plugin.get_text("warp.gui.del.select")
        
        for warp_name in warps:
            warp_data = self.warps[warp_name]
            form.add_button(
                f"{warp_name}\n({warp_data['x']:.1f}, {warp_data['y']:.1f}, {warp_data['z']:.1f})",
                callback=lambda p, data, name=warp_name: self._confirm_delete_warp(p, name)
            )
        
        player.send_form(form)
    
    def _confirm_delete_warp(self, player: Player, warp_name: str):
        """确认删除传送点"""
        from endstone import CustomForm
        
        form = CustomForm()
        form.title = self.plugin.get_text("warp.gui.del.confirm.title")
        
        warp_data = self.warps[warp_name]
        form.add_label(self.plugin.get_text("warp.gui.del.confirm.warning", name=warp_name))
        form.add_label(self.plugin.get_text("warp.gui.del.confirm.position", 
                                           x=warp_data["x"], 
                                           y=warp_data["y"], 
                                           z=warp_data["z"]))
        form.add_label(self.plugin.get_text("warp.gui.del.confirm.creator", creator=warp_data.get("creator", "未知")))
        
        def callback(p, data):
            if data is not None:
                self.delete_warp(p, warp_name)
        
        player.send_form(form, callback)
    
    def _open_warp_list_gui(self, player: Player):
        """打开传送点列表GUI"""
        warps = self.list_warps()
        if not warps:
            player.send_message(self.plugin.get_text("warp.list.empty"))
            return
        
        from endstone import SimpleForm
        form = SimpleForm()
        form.title = self.plugin.get_text("warp.gui.list.title")
        form.content = self.plugin.get_text("warp.gui.list.select")
        
        for warp_name in warps:
            warp_data = self.warps[warp_name]
            
            # 显示传送费用
            cost = self.plugin.config_manager.get("Warp.cost", 0)
            cost_text = f" §c{cost}金币" if cost > 0 else " §a免费"
            
            form.add_button(
                f"{warp_name}{cost_text}\n({warp_data['x']:.1f}, {warp_data['y']:.1f}, {warp_data['z']:.1f})",
                callback=lambda p, data, name=warp_name: self._confirm_teleport_warp(p, name)
            )
        
        player.send_form(form)
    
    def _confirm_teleport_warp(self, player: Player, warp_name: str):
        """确认传送到传送点"""
        from endstone import CustomForm
        
        warp_data = self.warps[warp_name]
        cost = self.plugin.config_manager.get("Warp.cost", 0)
        
        form = CustomForm()
        form.title = self.plugin.get_text("warp.gui.teleport.title")
        
        form.add_label(self.plugin.get_text("warp.gui.teleport.name", name=warp_name))
        form.add_label(self.plugin.get_text("warp.gui.teleport.position", 
                                           x=warp_data["x"], 
                                           y=warp_data["y"], 
                                           z=warp_data["z"]))
        form.add_label(self.plugin.get_text("warp.gui.teleport.cost", cost=cost))
        form.add_label(self.plugin.get_text("economy.balance", balance=self.plugin.economy.get_balance(player)))
        
        def callback(p, data):
            if data is not None:
                self.teleport_to_warp(p, warp_name)
        
        player.send_form(form, callback)
    
    def _load_warps(self):
        """加载传送点数据"""
        try:
            warps_path = os.path.join(self.plugin.data_folder, "warps.json")
            if os.path.exists(warps_path):
                with open(warps_path, 'r', encoding='utf-8') as f:
                    self.warps = json.load(f)
        except Exception as e:
            self.plugin.logger.error(f"加载传送点数据失败: {e}")
            self.warps = {}
    
    def _save_warps(self):
        """保存传送点数据"""
        try:
            warps_path = os.path.join(self.plugin.data_folder, "warps.json")
            os.makedirs(os.path.dirname(warps_path), exist_ok=True)
            
            with open(warps_path, 'w', encoding='utf-8') as f:
                json.dump(self.warps, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.plugin.logger.error(f"保存传送点数据失败: {e}")
