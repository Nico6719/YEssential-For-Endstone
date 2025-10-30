import math
import random
import time
from typing import Optional
from endstone import Player, Location

class RTPSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.server = plugin.server
    
    def teleport_random(self, player: Player) -> bool:
        """执行随机传送"""
        if not self.plugin.is_module_enabled("RTP"):
            player.send_message(self.plugin.get_text("module.no.enabled"))
            return False
        
        # 检查维度限制
        dimension = player.location.dimension
        allowed_dimensions = self.plugin.config_manager.get("RTP.allowed_dimensions", [0])
        if dimension not in allowed_dimensions:
            player.send_message(self.plugin.get_text("rtp.wrong_dimension"))
            return False
        
        # 检查冷却时间
        has_cooldown, remaining = self.plugin.has_cooldown(player, "rtp")
        if has_cooldown:
            player.send_message(self.plugin.get_text("rtp.cooldown", time=remaining))
            return False
        
        # 检查费用
        cost = self.plugin.config_manager.get("RTP.cost", 0)
        if cost > 0 and not self.plugin.economy.reduce_balance(player, cost):
            player.send_message(self.plugin.get_text("economy.no.enough"))
            return False
        
        # 设置冷却
        cooldown = self.plugin.config_manager.get("RTP.cooldown", 300)
        if cooldown > 0:
            self.plugin.set_cooldown(player, "rtp", cooldown)
        
        # 显示搜索信息
        min_radius = self.plugin.config_manager.get("RTP.min_radius", 100)
        max_radius = self.plugin.config_manager.get("RTP.max_radius", 5000)
        player.send_message(self.plugin.get_text("rtp.searching"))
        player.send_message(self.plugin.get_text("rtp.range", min=min_radius, max=max_radius))
        
        # 生成安全位置
        safe_location = self._find_safe_location(player)
        if not safe_location:
            player.send_message(self.plugin.get_text("rtp.failed"))
            # 退还费用
            if cost > 0:
                self.plugin.economy.add_balance(player, cost)
            return False
        
        # 执行传送
        try:
            if self.plugin.config_manager.get("RTP.animation", False):
                self._perform_animated_teleport(player, safe_location)
            else:
                player.teleport(safe_location)
                player.send_message(self.plugin.get_text("rtp.success"))
            
            # 计算距离
            distance = math.sqrt(
                (safe_location.x - player.location.x) ** 2 +
                (safe_location.z - player.location.z) ** 2
            )
            player.send_message(self.plugin.get_text("rtp.distance", distance=int(distance)))
            
            return True
            
        except Exception as e:
            self.plugin.logger.error(f"随机传送失败: {e}")
            player.send_message(self.plugin.get_text("rtp.failed"))
            # 退还费用
            if cost > 0:
                self.plugin.economy.add_balance(player, cost)
            return False
    
    def _find_safe_location(self, player: Player, max_attempts: int = 50) -> Optional[Location]:
        """寻找安全位置"""
        min_radius = self.plugin.config_manager.get("RTP.min_radius", 100)
        max_radius = self.plugin.config_manager.get("RTP.max_radius", 5000)
        
        for attempt in range(max_attempts):
            # 生成随机坐标
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(min_radius, max_radius)
            
            x = player.location.x + int(distance * math.cos(angle))
            z = player.location.z + int(distance * math.sin(angle))
            
            # 寻找安全高度
            y = self._find_safe_height(x, z, player.location.dimension)
            if y is not None:
                return Location(
                    x=x,
                    y=y,
                    z=z,
                    dimension=player.location.dimension,
                    world=player.location.world
                )
        
        return None
    
    def _find_safe_height(self, x: int, z: int, dimension: int) -> Optional[float]:
        """寻找安全高度"""
        # 简化版本：从最高点开始向下寻找安全位置
        # 在实际实现中，需要根据地形生成算法来寻找
        
        # 模拟寻找安全高度
        for test_y in range(120, 0, -1):
            # 检查这个位置是否安全（脚部、头部、地面）
            # 这里需要实际的方块检查逻辑
            if self._is_position_safe(x, test_y, z, dimension):
                return test_y + 1  # 返回脚部位置
        
        return None
    
    def _is_position_safe(self, x: int, y: int, z: int, dimension: int) -> bool:
        """检查位置是否安全"""
        # 简化版本：总是返回True
        # 在实际实现中，需要检查：
        # 1. 脚部位置是否安全（不是岩浆、水等）
        # 2. 头部位置是否安全（有足够空间）
        # 3. 地面位置是否坚固
        
        # 这里应该使用Endstone的方块检查API
        # 例如：world.get_block(x, y, z, dimension)
        
        return True
    
    def _perform_animated_teleport(self, player: Player, location: Location):
        """执行动画传送"""
        # 显示传送动画信息
        player.send_message("§7正在加载区块...")
        
        # 模拟传送动画
        # 在实际实现中，可以使用粒子效果、相机动画等
        
        # 延迟传送以创建动画效果
        def do_teleport():
            try:
                player.teleport(location)
                player.send_message(self.plugin.get_text("rtp.success"))
                
                # 添加效果
                player.add_effect("resistance", 30, 255, True)
                
            except Exception as e:
                self.plugin.logger.error(f"动画传送失败: {e}")
                player.send_message(self.plugin.get_text("rtp.failed"))
        
        # 延迟执行传送
        self.server.get_scheduler().call_later(3.0, do_teleport)
