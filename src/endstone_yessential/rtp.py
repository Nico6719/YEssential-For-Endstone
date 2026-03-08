import random
import math
from typing import Dict, Optional, Tuple
from endstone import Player
from endstone.level import Location
from endstone.command import CommandSender

from .log import plugin_print

class RTPSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.cooltime: Dict[str, int] = {}  # 冷却时间 Map，key: playerName, value: 剩余秒数

    def get_config(self):
        """获取RTP配置"""        
        config = self.plugin.config_manager.config_data.get("RTP", {})
        if not config:
            # 使用默认配置
            config = {
                "maxRadius": 5000,
                "minRadius": 100,
                "cost": 0,
                "cooldown": 0,
                "animation": 0
            }
            self.plugin.config_manager.config_data["RTP"] = config
            self.plugin.config_manager.save_config()
        return config

    def generate_random_coordinate(self) -> Tuple[int, int]:
        """生成随机坐标（在最小和最大半径之间）"""
        config = self.get_config()
        max_radius = config.get("maxRadius", 5000)
        min_radius = config.get("minRadius", 100)

        angle = random.random() * 2 * math.pi
        min_radius_squared = min_radius * min_radius
        max_radius_squared = max_radius * max_radius
        radius_squared = min_radius_squared + random.random() * (max_radius_squared - min_radius_squared)
        radius = math.sqrt(radius_squared)

        x = math.floor(radius * math.cos(angle))
        z = math.floor(radius * math.sin(angle))

        return x, z

    def is_coordinate_valid(self, x: int, z: int) -> bool:
        """验证坐标是否在有效范围内"""
        config = self.get_config()
        max_radius = config.get("maxRadius", 5000)
        min_radius = config.get("minRadius", 100)

        distance = math.sqrt(x * x + z * z)
        return min_radius <= distance <= max_radius

    def preload_chunks(self, x: int, z: int, dimension: str, player: Player) -> bool:
        """预加载区块"""
        try:
            # 传送到地图顶端确保不会卡进地形，同时给予缓降效果防止摔落
            # Endstone 中维度ID可能不同，这里使用 dimension 参数
            preload_y = 320  # 默认高度
            if dimension == "minecraft:nether":  # 下界
                preload_y = 130
            elif dimension == "minecraft:the_end":  # 末地
                preload_y = 125

            # 给予缓降效果
            player.send_message("§6[YEssential] §7正在加载区块...")
            # Endstone 可能没有直接的命令执行方式，这里使用 teleport
            player.teleport(Location(dimension, x, preload_y, z))

            # 使用调度器延迟执行后续操作，模拟异步加载
            def on_chunk_loaded():
                player.send_message("§6[YEssential] §a区块加载完成，正在搜索安全位置...")
            
            self.plugin.server.scheduler.run_task(self.plugin, on_chunk_loaded, 60)  # 3秒后执行 (60 ticks)
            return True
        except Exception as error:
            plugin_print(f"[RTP] 预加载区块失败: {error}")
            return False

    def get_surface_height(self, x: int, z: int, dimension: str) -> Optional[int]:
        """获取地表高度"""
        # 主世界支持 1.18+ 新地形（-64~320），下界扫 5~120，末地扫 0~128
        start_y = 320
        end_y = -62

        if dimension == "minecraft:nether":  # 下界
            start_y = 120
            end_y = 5
        elif dimension == "minecraft:the_end":  # 末地
            start_y = 128
            end_y = 0

        air_blocks = {"minecraft:air", "minecraft:cave_air", "minecraft:void_air"}
        liquid_blocks = {"minecraft:water", "minecraft:lava", "minecraft:flowing_water", "minecraft:flowing_lava"}

        hit_liquid = False

        for y in range(start_y, end_y - 1, -1):
            try:
                # 获取方块类型
                block = self.plugin.server.get_block(Location(dimension, x, y, z))
                if not block:
                    continue

                block_type = block.type

                if block_type in air_blocks:
                    continue

                # 记录遇到液体，之后的固体因为上方是液体，所以不安全
                if block_type in liquid_blocks:
                    hit_liquid = True
                    continue

                # 找到固体块，如果上方曾经是液体则这里是水下，不安全
                if hit_liquid:
                    # 重置，继续向下找可能存在的洞穴出口
                    hit_liquid = False
                    continue

                # 检查上方两个方块是否是空气
                up1 = self.plugin.server.get_block(Location(dimension, x, y + 1, z))
                up2 = self.plugin.server.get_block(Location(dimension, x, y + 2, z))

                if up1 and up2:
                    up1_type = up1.type
                    up2_type = up2.type

                    if up1_type in air_blocks and up2_type in air_blocks:
                        return y + 1  # 站立点
            except Exception:
                continue

        return None

    def is_location_safe(self, x: int, y: int, z: int, dimension: str) -> bool:
        """检查位置是否安全"""
        try:
            feet_block = self.plugin.server.get_block(Location(dimension, x, y, z))
            head_block = self.plugin.server.get_block(Location(dimension, x, y + 1, z))
            ground_block = self.plugin.server.get_block(Location(dimension, x, y - 1, z))

            if not feet_block or not head_block or not ground_block:
                return False

            feet_type = feet_block.type
            head_type = head_block.type
            ground_type = ground_block.type

            if feet_type not in {"minecraft:air", "minecraft:cave_air"}:
                return False

            if head_type not in {"minecraft:air", "minecraft:cave_air"}:
                return False

            very_dangerous_blocks = [
                "minecraft:air",
                "minecraft:cave_air",
                "minecraft:void_air",
                "minecraft:lava",
                "minecraft:flowing_lava"
            ]

            if ground_type in very_dangerous_blocks:
                return False

            return True
        except Exception:
            return False

    def find_safe_location(self, center_x: int, center_z: int, dimension: str, player: Player) -> Optional[Location]:
        """查找安全位置"""
        # 预加载中心区块
        self.preload_chunks(center_x, center_z, dimension, player)

        # 检查中心点
        y = self.get_surface_height(center_x, center_z, dimension)
        if y is not None and self.is_location_safe(center_x, y, center_z, dimension):
            return Location(dimension, center_x, y, center_z)

        # 螺旋搜索（增大范围和次数以应对海洋/山地等复杂地形）
        max_attempts = 120
        max_radius = 300

        for attempt in range(1, max_attempts + 1):
            angle = attempt * 0.618 * math.pi * 2  # 黄金角，均匀覆盖
            distance = min(attempt * 3, max_radius)

            offset_x = math.floor(distance * math.cos(angle))
            offset_z = math.floor(distance * math.sin(angle))

            x = center_x + offset_x
            z = center_z + offset_z

            try:
                y = self.get_surface_height(x, z, dimension)

                if y is not None and self.is_location_safe(x, y, z, dimension):
                    return Location(dimension, x, y, z)
            except Exception:
                continue

        return None

    def perform_rtp(self, player: Player) -> bool:
        """主要的RTP执行方法"""
        config = self.get_config()
        cost = config.get("cost", 0)
        cooldown = config.get("cooldown", 0)
        player_name = player.name

        try:
            # 1. 冷却检查
            if player_name in self.cooltime:
                remaining_time = self.cooltime[player_name]
                if remaining_time > 0:
                    player.send_message(f"§6[YEssential] §c传送冷却中，剩余时间：{remaining_time}秒")
                    return False

            # 2. 金币检查
            if cost > 0:
                balance = self.plugin.economy.get_money(player_name)

                if balance < cost:
                    player.send_message(f"§6[YEssential] §c您需要 {cost} 金币才能使用随机传送！")
                    return False

            # 3. 显示传送信息
            player.send_message("§6[YEssential] §7正在搜索安全位置...")

            # 4. 设置冷却
            if cooldown > 0:
                self.cooltime[player_name] = cooldown

            # 5. 扣除费用
            if cost > 0:
                self.plugin.economy.reduce_money(player_name, cost)
                player.send_message(f"§6[YEssential] §e花费 {cost} 金币")

            # 6. 尝试找到合适的坐标并执行传送
            safe_location = None
            max_coordinate_attempts = 8  # 增加外层重试次数

            for attempt in range(1, max_coordinate_attempts + 1):
                x, z = self.generate_random_coordinate()

                if not self.is_coordinate_valid(x, z):
                    continue

                distance = math.floor(math.sqrt(x * x + z * z))
                player.send_message(f"§6[YEssential] §7尝试第 {attempt} 次：坐标 X:{x}, Z:{z} (距离: {distance}格)")

                # 查找安全位置
                safe_location = self.find_safe_location(x, z, player.location.dimension, player)

                if safe_location:
                    break

            # 7. 处理传送结果
            if safe_location:
                final_distance = math.floor(math.sqrt(
                    safe_location.x * safe_location.x +
                    safe_location.z * safe_location.z
                ))
                
                # 检查是否启用动画
                animation_enabled = config.get("animation", 0)
                
                if animation_enabled == 1:
                    # GTA5 风格的传送动画
                    self.perform_gta5_animation(player, safe_location, final_distance)
                else:
                    # 直接传送
                    player.teleport(safe_location)
                    player.send_message(f"§6[YEssential] §a传送成功！位置: {safe_location.x}, {safe_location.y}, {safe_location.z}")
                    player.send_message(f"§6[YEssential] §e距离出生点: §f{final_distance} 格")

                return True
            else:
                # 所有尝试都失败，使用备用方案
                player.send_message("§6[YEssential] §c无法找到安全位置，使用备用传送方案...")
                fallback_result = self.fallback_teleport(player)

                if not fallback_result:
                    self.refund_player(player, cost, cooldown)
                    return False

                return True

        except Exception as error:
            plugin_print(f"[RTP] RTP传送失败: {error}")
            player.send_message("§6[YEssential] §c传送过程中出现错误")

            self.refund_player(player, cost, cooldown)

            return False

    def fallback_teleport(self, player: Player) -> bool:
        """备用传送方案"""
        try:
            x, z = self.generate_random_coordinate()
            y = 150

            player.teleport(Location(player.location.dimension, x, y, z))

            player.send_message("§6[YEssential] §a已使用备用方案传送到安全高度")
            player.send_message(f"§6[YEssential] §7坐标: X:{x}, Y:{y}, Z:{z}")

            return True
        except Exception as error:
            plugin_print(f"[RTP] 备用传送失败: {error}")
            return False

    def refund_player(self, player: Player, cost: float, cooldown: int):
        """退还费用和重置冷却"""
        if cost > 0:
            try:
                self.plugin.economy.add_money(player.name, cost)
                player.send_message(f"§6[YEssential] §a已退还 {cost} 金币")
            except Exception as e:
                plugin_print(f"退还费用失败: {e}")

        if cooldown > 0 and player.name in self.cooltime:
            del self.cooltime[player.name]

    def perform_gta5_animation(self, player: Player, safe_location: Location, final_distance: int):
        """执行GTA5风格的传送动画"""
        try:
            player_name = player.name
            player_pos = player.location
            
            # 阶段1：镜头上升75格 (2秒)
            self.plugin.server.dispatch_command(f'effect "{player_name}" resistance 30 255 true')
            self.plugin.server.dispatch_command(f'camera {player_name} set minecraft:free ease 3 in_out_sine pos {player_pos.x} {player_pos.y + 75} {player_pos.z} rot 90 ~')
            self.plugin.server.dispatch_command(f'hud {player_name} hide all')
            
            # 2秒后开始查找安全位置
            def stage2():
                player.send_message("§6[YEssential] §7正在查找安全位置...")
                player.send_message("§6[YEssential] §7正在加载区块...")
            
            self.plugin.server.scheduler.run_task(self.plugin, stage2, 40)  # 2秒后执行
            
            # 3秒后显示加载进度
            def stage3():
                player.send_message("§6[YEssential] §7正在搜索安全位置...")
            
            self.plugin.server.scheduler.run_task(self.plugin, stage3, 60)  # 3秒后执行
            
            # 4秒后显示加载进度
            def stage4():
                player.send_message("§6[YEssential] §7正在加载区块...")
            
            self.plugin.server.scheduler.run_task(self.plugin, stage4, 80)  # 4秒后执行
            
            # 5秒后显示找到安全位置
            def stage5():
                player.send_message("§6[YEssential] §a找到安全位置！")
                sky_y = safe_location.y + 100
                self.plugin.server.dispatch_command(f'camera "{player_name}" set minecraft:free ease 3 in_out_sine pos {safe_location.x} {sky_y} {safe_location.z} rot 90 ~')
            
            self.plugin.server.scheduler.run_task(self.plugin, stage5, 100)  # 5秒后执行
            
            # 6.5秒时传送玩家
            def stage6():
                player.send_message("§6[YEssential] §e正在传送...")
                player.teleport(safe_location)
            
            self.plugin.server.scheduler.run_task(self.plugin, stage6, 130)  # 6.5秒后执行
            
            # 7.5秒后镜头移动到玩家后方
            def stage7():
                behind_z = safe_location.z - 3
                self.plugin.server.dispatch_command(f'camera "{player_name}" set minecraft:free ease 3 in_out_sine pos {safe_location.x} {safe_location.y + 1.65} {behind_z} rot 0 0')
            
            self.plugin.server.scheduler.run_task(self.plugin, stage7, 150)  # 7.5秒后执行
            
            # 8.5秒后镜头快速移动到第一人称
            def stage8():
                self.plugin.server.dispatch_command(f'camera "{player_name}" set minecraft:free ease 1 in_sine pos {safe_location.x - 0.21} {safe_location.y + 1.65} {safe_location.z} rot 0 0')
            
            self.plugin.server.scheduler.run_task(self.plugin, stage8, 170)  # 8.5秒后执行
            
            # 9.5秒后清除镜头
            def stage9():
                self.plugin.server.dispatch_command(f'camera "{player_name}" clear')
                self.plugin.server.dispatch_command(f'hud {player_name} reset all')
                try:
                    self.plugin.server.dispatch_command(f'playsound random.levelup "{player_name}"')
                except:
                    # 忽略音效错误
                    pass
                player.send_message(f"§6[YEssential] §a传送成功！位置: {safe_location.x}, {safe_location.y}, {safe_location.z}")
                player.send_message(f"§6[YEssential] §e距离出生点: §f{final_distance} 格")
                player.send_message("§6[YEssential] §b传送完成！")
            
            self.plugin.server.scheduler.run_task(self.plugin, stage9, 190)  # 9.5秒后执行
            
        except Exception as error:
            plugin_print(f"[RTP] 动画执行失败: {error}")
            # 清除镜头效果
            try:
                self.plugin.server.dispatch_command(f'camera "{player.name}" clear')
                self.plugin.server.dispatch_command(f'hud {player.name} reset all')
            except:
                pass
            # 如果动画失败，直接传送
            player.teleport(safe_location)
            player.send_message(f"§6[YEssential] §a传送成功！位置: {safe_location.x}, {safe_location.y}, {safe_location.z}")
            player.send_message(f"§6[YEssential] §e距离出生点: §f{final_distance} 格")

    def start_cooltime_task(self):
        """启动冷却时间倒计时任务"""
        # 使用 Endstone 的调度器来处理冷却时间
        def update_cooltime():
            for player_name in list(self.cooltime.keys()):
                if self.cooltime[player_name] > 0:
                    self.cooltime[player_name] -= 1
                else:
                    del self.cooltime[player_name]

        # 每秒更新一次冷却时间
        self.plugin.server.scheduler.run_task(self.plugin, update_cooltime, 0, 20)  # 20 ticks = 1 second

    def teleport_random(self, player: Player):
        """执行随机传送"""
        config = self.get_config()
        cost = config.get("cost", 0)
        cooldown = config.get("cooldown", 0)
        player_name = player.name
        
        try:
            # 1. 冷却检查
            if player_name in self.cooltime:
                remaining_time = self.cooltime[player_name]
                if remaining_time > 0:
                    player.send_message(f"§6[YEssential] §c传送冷却中，剩余时间：{remaining_time}秒")
                    return False
            
            # 2. 金币检查
            if cost > 0:
                balance = self.plugin.economy.get_money(player_name)
                
                if balance < cost:
                    player.send_message(f"§6[YEssential] §c您需要 {cost} 金币才能使用随机传送！")
                    return False
            
            # 3. 显示传送信息
            player.send_message("§6[YEssential] §7正在搜索安全位置...")
            
            # 4. 设置冷却
            if cooldown > 0:
                self.cooltime[player_name] = cooldown
            
            # 5. 扣除费用
            if cost > 0:
                self.plugin.economy.reduce_money(player_name, cost)
                player.send_message(f"§6[YEssential] §e花费 {cost} 金币")
            
            # 6. 尝试找到合适的坐标并执行传送
            safe_location = None
            max_coordinate_attempts = 8  # 增加外层重试次数
            
            for attempt in range(1, max_coordinate_attempts + 1):
                x, z = self.generate_random_coordinate()
                
                if not self.is_coordinate_valid(x, z):
                    continue
                
                distance = math.floor(math.sqrt(x * x + z * z))
                player.send_message(f"§6[YEssential] §7尝试第 {attempt} 次：坐标 X:{x}, Z:{z} (距离: {distance}格)")
                
                # 查找安全位置
                safe_location = self.find_safe_location(x, z, player.location.dimension, player)
                
                if safe_location:
                    break
            
            # 7. 处理传送结果
            if safe_location:
                final_distance = math.floor(math.sqrt(
                    safe_location.x * safe_location.x +
                    safe_location.z * safe_location.z
                ))
                
                player.teleport(safe_location)
                player.send_message(f"§6[YEssential] §a传送成功！位置: {safe_location.x}, {safe_location.y}, {safe_location.z}")
                player.send_message(f"§6[YEssential] §e距离出生点: §f{final_distance} 格")
                
                return True
            else:
                # 所有尝试都失败，使用备用方案
                player.send_message("§6[YEssential] §c无法找到安全位置，使用备用传送方案...")
                fallback_result = self.fallback_teleport(player)
                
                if not fallback_result:
                    self.refund_player(player, cost, cooldown)
                    return False
                
                return True
            
        except Exception as error:
            plugin_print(f"[RTP] RTP传送失败: {error}")
            player.send_message("§6[YEssential] §c传送过程中出现错误")
            
            self.refund_player(player, cost, cooldown)
            
            return False
