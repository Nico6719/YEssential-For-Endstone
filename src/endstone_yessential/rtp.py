import random
import math
from typing import Dict
from endstone import Player
from endstone.level import Location
from endstone.command import CommandSenderWrapper

from .log import plugin_print


class RTPSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.cooltime: Dict[str, int] = {}
        # 静默命令发送器：抑制所有命令输出到控制台
        self._silent = CommandSenderWrapper(plugin.server.command_sender)

    def _dispatch(self, command: str) -> bool:
        try:
            return self.plugin.server.dispatch_command(self._silent, command)
        except Exception as e:
            plugin_print(f"[RTP] cmd失败: {e} | {command[:80]}")
            return False

    def get_config(self):
        c = self.plugin.config_manager.config_data.get("RTP", {})
        if not c:
            c = {"maxRadius": 5000, "minRadius": 100, "cost": 0, "cooldown": 0, "animation": 0}
            self.plugin.config_manager.config_data["RTP"] = c
            self.plugin.config_manager.save_config()
        return c

    def _random_xy(self):
        c = self.get_config()
        a = random.random() * 2 * math.pi
        r = math.sqrt(c["minRadius"]**2 + random.random() * (c["maxRadius"]**2 - c["minRadius"]**2))
        return math.floor(r * math.cos(a)), math.floor(r * math.sin(a))

    # ─── /spreadplayers 方案（MC 引擎内部处理安全地表）─────────

    def _spread(self, player: Player, x: int, z: int, max_range: int = 50) -> bool:
        """用 /spreadplayers 传送到安全地表"""
        return self._dispatch(f'spreadplayers {x} {z} 1 {max_range} {player.name}')

    def _rtp(self, player: Player, anim: bool):
        x, z = self._random_xy()
        dist = math.floor(math.sqrt(x * x + z * z))
        player.send_message(f"§6[YEssential] §7随机传送 X:{x}, Z:{z} (距离:{dist}格)")

        if anim:
            self._rtp_anim(player, x, z)
        else:
            self._rtp_plain(player, x, z)

    def _rtp_plain(self, player, x, z):
        """无动画：直接 spreadplayers"""
        player.send_message("§6[YEssential] §7正在搜索安全位置...")
        if self._spread(player, x, z):
            l = player.location
            player.send_message(f"§6[YEssential] §a传送成功！位置: {int(l.x)}, {int(l.y)}, {int(l.z)}")
            player.send_message(f"§6[YEssential] §e距离出生点: §f{math.floor(math.sqrt(l.x**2+l.z**2))} 格")
        else:
            player.send_message("§6[YEssential] §c/spreadplayers 失败，使用备用方案...")
            self._fallback(player)

    def _rtp_anim(self, player, x, z):
        """动画模式：镜头上升 → spreadplayers → 镜头过渡"""
        pn = player.name
        op = player.location

        self._dispatch(f'camera {pn} set minecraft:free ease 3 in_out_sine pos {op.x:.1f} {op.y+75:.1f} {op.z:.1f} rot 90 {op.yaw:.1f}')
        self._dispatch(f'hud {pn} hide all')
        self._dispatch(f'effect "{pn}" resistance 30 255 true')
        player.send_message("§6[YEssential] §7正在搜索安全位置...")

        def do():
            if self._spread(player, x, z):
                l = player.location
                # 镜头 → 天空
                self._dispatch(f'camera "{pn}" set minecraft:free ease 3 in_out_sine pos {l.x:.1f} {l.y+100:.1f} {l.z:.1f} rot 90 ~')
                def bh():
                    self._dispatch(f'camera "{pn}" set minecraft:free ease 3 in_out_sine pos {l.x:.1f} {l.y+1.65:.1f} {l.z-3:.1f} rot 0 0')
                self.plugin.server.scheduler.run_task(self.plugin, bh, 60)
                def fp():
                    self._dispatch(f'camera "{pn}" set minecraft:free ease 1 in_sine pos {l.x-0.21:.1f} {l.y+1.65:.1f} {l.z:.1f} rot 0 0')
                self.plugin.server.scheduler.run_task(self.plugin, fp, 120)
                def cl():
                    self._dispatch(f'camera "{pn}" clear')
                    self._dispatch(f'hud {pn} reset all')
                    self._dispatch(f'playsound random.levelup "{pn}"')
                    d = math.floor(math.sqrt(l.x**2+l.z**2))
                    player.send_message(f"§6[YEssential] §a传送成功！位置: {int(l.x)}, {int(l.y)}, {int(l.z)}")
                    player.send_message(f"§6[YEssential] §e距离出生点: §f{d} 格")
                    player.send_message("§6[YEssential] §b传送完成！")
                self.plugin.server.scheduler.run_task(self.plugin, cl, 140)
            else:
                self._dispatch(f'camera "{pn}" clear')
                self._dispatch(f'hud {pn} reset all')
                self._fallback(player)

        self.plugin.server.scheduler.run_task(self.plugin, do, 60)  # 3 秒后

    # ─── 主入口 ────────────────────────────────────────────

    def perform_rtp(self, player):
        c = self.get_config()
        cost, cd = c.get("cost", 0), c.get("cooldown", 0)
        pn = player.name
        try:
            if pn in self.cooltime and self.cooltime[pn] > 0:
                return player.send_message(f"§6[YEssential] §c传送冷却中，剩余时间：{self.cooltime[pn]}秒")
            if cost > 0 and self.plugin.economy.get_money(pn) < cost:
                return player.send_message(f"§6[YEssential] §c您需要 {cost} 金币")
            if cd > 0:
                self.cooltime[pn] = cd
            if cost > 0:
                self.plugin.economy.reduce_money(pn, cost)
                player.send_message(f"§6[YEssential] §e花费 {cost} 金币")
            self._rtp(player, c.get("animation", 0))
        except Exception as e:
            plugin_print(f"[RTP] 失败: {e}")
            player.send_message("§6[YEssential] §c传送错误")
            self._refund(player, cost, cd)

    def _fallback(self, player):
        try:
            x, z = self._random_xy()
            self._dispatch(f'effect "{player.name}" slow_falling 30 1 true')
            player.teleport(Location(player.location.dimension, x, 320, z))
            player.send_message(f"§6[YEssential] §a备用传送 X:{x} Y:320 Z:{z}")
        except Exception as e:
            plugin_print(f"[RTP] 备用失败: {e}")

    def _refund(self, player, cost, cd):
        if cost > 0:
            try:
                self.plugin.economy.add_money(player.name, cost)
                player.send_message(f"§6[YEssential] §a已退还 {cost} 金币")
            except Exception as e:
                plugin_print(f"退款失败: {e}")
        if cd > 0 and player.name in self.cooltime:
            del self.cooltime[player.name]

    def start_cooltime_task(self):
        def tick():
            for k in list(self.cooltime.keys()):
                if self.cooltime[k] > 0:
                    self.cooltime[k] -= 1
                else:
                    del self.cooltime[k]
        self.plugin.server.scheduler.run_task(self.plugin, tick, 0, 20)
