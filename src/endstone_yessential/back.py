from typing import Dict, List
from endstone import Player, ColorFormat
from endstone.level import Location
from endstone.form import ActionForm
from .i18n import tr
import time

class BackSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        # 使用unique_id作为键来存储死亡点
        self.death_points: Dict[str, List[Dict]] = {}
        # 每个玩家最多记录的死亡点数量
        self.max_death_points = 5

    def record_death(self, player: Player):
        """记录玩家死亡点"""
        self.plugin.logger.info(f"[DEBUG] record_death 被调用，玩家: {player.name}, unique_id: {player.unique_id}")
        # 初始化玩家的死亡点列表
        if player.unique_id not in self.death_points:
            self.death_points[player.unique_id] = []

        # 记录新的死亡点，包含位置和时间
        death_point = {
            "location": player.location,
            "time": time.time()
        }

        self.plugin.logger.info(f"[DEBUG] 死亡点位置: ({death_point['location'].x}, {death_point['location'].y}, {death_point['location'].z})")

        # 添加到列表开头
        self.death_points[player.unique_id].insert(0, death_point)

        # 限制死亡点数量
        if len(self.death_points[player.unique_id]) > self.max_death_points:
            self.death_points[player.unique_id] = self.death_points[player.unique_id][:self.max_death_points]

        self.plugin.logger.info(f"[DEBUG] 当前记录的死亡点数量: {len(self.death_points[player.unique_id])}")
        player.send_message(f"§6[YEssential] §c死亡点已记录，输入 /back 返回。当前记录了 {len(self.death_points[player.unique_id])} 个死亡点。")

    def teleport_back(self, player: Player, index: int = 0):
        """传送到指定索引的死亡点"""
        if player.unique_id not in self.death_points or not self.death_points[player.unique_id]:
            player.send_message(ColorFormat.DARK_RED + "It seems you haven't died yet.")
            return

        if index < 0 or index >= len(self.death_points[player.unique_id]):
            player.send_message(tr("back.invalid_index"))
            return

        death_point = self.death_points[player.unique_id][index]
        player.teleport(death_point["location"])
        player.send_message(ColorFormat.GREEN + "You have been teleported to the last place of death")
        # 传送后移除该死亡点
        del self.death_points[player.unique_id][index]

    def open_back_gui(self, player: Player):
        """打开返回死亡点 GUI"""
        form = ActionForm(title=tr("back.title"))

        if player.unique_id in self.death_points and self.death_points[player.unique_id]:
            # 显示所有记录的死亡点
            for i, death_point in enumerate(self.death_points[player.unique_id]):
                loc = death_point["location"]
                death_time = time.time() - death_point["time"]

                # 格式化时间
                if death_time < 60:
                    time_str = f"{int(death_time)}秒前"
                elif death_time < 3600:
                    time_str = f"{int(death_time / 60)}分钟前"
                elif death_time < 86400:
                    time_str = f"{int(death_time / 3600)}小时前"
                else:
                    time_str = f"{int(death_time / 86400)}天前"

                button_text = f"§a死亡点 {i + 1}: §e({int(loc.x)}, {int(loc.y)}, {int(loc.z)}) §7- {time_str}"
                form.add_button(button_text, on_click=lambda p, idx=i: self.teleport_back(p, idx))

            form.content = f"§7您共有 {len(self.death_points[player.unique_id])} 个记录的死亡点。"
        else:
            form.content = "§c当前没有记录的死亡点。"

        form.add_button("§c关闭")
        player.send_form(form)
