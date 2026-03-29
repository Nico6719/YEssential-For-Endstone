import time
import threading
from typing import Dict, Optional
from endstone import Player
from endstone.boss import BossBar, BarColor, BarStyle

class FcamSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.fcam_boss_bars: Dict[str, Dict] = {}
        self.fcam_players: Dict[str, str] = {}  # player_name -> simulated_player_name
        self.info_prefix = "§l§6[-YEST-] §r"
        self.timeout = 300  # 默认5分钟超时
        self.cost_money = 0

    def load_config(self):
        config = self.plugin.config_manager.get_config()
        fcam_config = config.get("Fcam", {})
        self.cost_money = fcam_config.get("CostMoney", 0)
        self.timeout = fcam_config.get("TimeOut", 300)

    def is_enabled(self) -> bool:
        config = self.plugin.config_manager.get_config()
        return config.get("Fcam", {}).get("EnableModule", False)

    def is_in_fcam(self, player: Player) -> bool:
        return player.name in self.fcam_players

    def enter_fcam(self, player: Player) -> bool:
        if not self.is_enabled():
            player.send_message(self.info_prefix + "§c该模块未启用")
            return False

        player_name = player.name
        player_pos = player.location

        if self.is_in_fcam(player):
            player.send_message(self.info_prefix + "§c你已经在灵魂出窍状态")
            return False

        if self.cost_money > 0:
            if hasattr(self.plugin, 'economy') and self.plugin.economy:
                balance = self.plugin.economy.get_money(player_name)
                if balance < self.cost_money:
                    player.send_message(self.info_prefix + "§c金币不足")
                    return False
                self.plugin.economy.reduce_money(player_name, self.cost_money)
            else:
                player.send_message(self.info_prefix + "§c经济系统未初始化")
                return False

        simulated_name = player_name + "_sp"

        try:
            self.plugin.server.dispatch_command(
                self.plugin.server.command_sender,
                f"spawnsimulatedplayer {simulated_name} {player_pos.x} {player_pos.y} {player_pos.z}"
            )
        except Exception as e:
            self.plugin.logger.error(f"生成模拟玩家失败: {e}")
            player.send_message(self.info_prefix + "§c灵魂出窍失败")
            return False

        try:
            self.plugin.server.dispatch_command(
                self.plugin.server.command_sender,
                f"gamemode spectator {simulated_name}"
            )
        except:
            pass

        try:
            player.game_mode = 6  # Spectator mode
        except:
            pass

        self.fcam_players[player_name] = simulated_name
        player.send_message(self.info_prefix + f"§a已进入灵魂出窍模式，扣除 {self.cost_money} 金币")

        if self.timeout > 0:
            self.start_fcam_boss_bar(player, player_name, self.timeout)

        return True

    def exit_fcam(self, player: Player) -> bool:
        player_name = player.name

        if not self.is_in_fcam(player):
            player.send_message(self.info_prefix + "§c你不在灵魂出窍状态")
            return False

        self.cleanup_fcam_boss_bar(player_name)

        simulated_name = self.fcam_players.pop(player_name)

        try:
            player.game_mode = 0  # Survival mode
        except:
            pass

        try:
            self.plugin.server.dispatch_command(
                self.plugin.server.command_sender,
                f"tp {player_name} {simulated_name}"
            )
        except:
            pass

        try:
            self.plugin.server.dispatch_command(
                self.plugin.server.command_sender,
                f"removesimulatedplayer {simulated_name}"
            )
        except:
            pass

        player.send_message(self.info_prefix + "§a已退出灵魂出窍模式")
        return True

    def toggle_fcam(self, player: Player) -> bool:
        if self.is_in_fcam(player):
            return self.exit_fcam(player)
        else:
            return self.enter_fcam(player)

    def start_fcam_boss_bar(self, player: Player, player_name: str, timeout: int):
        remaining = timeout

        try:
            boss_bar = self.plugin.server.create_boss_bar(
                f"§e灵魂出窍剩余 §c{remaining} §e秒",
                BarColor.YELLOW,
                BarStyle.SOLID
            )
            boss_bar.add_player(player)
            boss_bar.progress = 1.0
        except Exception as e:
            self.plugin.logger.error(f"创建BossBar失败: {e}")
            boss_bar = None

        self.fcam_boss_bars[player_name] = {
            "boss_bar": boss_bar,
            "timer": None,
            "remaining": remaining,
            "total_time": timeout
        }

        def update_boss_bar():
            nonlocal remaining
            while remaining > 0 and player_name in self.fcam_players:
                time.sleep(1)
                remaining -= 1

                current_player = self.plugin.server.get_player(player_name)
                if not current_player:
                    self.cleanup_fcam_boss_bar(player_name)
                    return

                if current_player.game_mode.value != 6:
                    self.cleanup_fcam_boss_bar(player_name)
                    return

                data = self.fcam_boss_bars.get(player_name)
                if not data:
                    return

                data["remaining"] = remaining

                if remaining <= 0:
                    self.cleanup_fcam_boss_bar(player_name)
                    try:
                        current_player.game_mode = 0
                        self.plugin.server.dispatch_command(
                            self.plugin.server.command_sender,
                            f"tp {player_name} {player_name}_sp"
                        )
                        self.plugin.server.dispatch_command(
                            self.plugin.server.command_sender,
                            f"removesimulatedplayer {player_name}_sp"
                        )
                        if player_name in self.fcam_players:
                            self.fcam_players.pop(player_name)
                        current_player.send_message(self.info_prefix + "§c灵魂出窍时间已到")
                    except Exception as e:
                        self.plugin.logger.error(f"灵魂出窍超时处理失败: {e}")
                    return

                progress = remaining / data["total_time"]
                color = BarColor.YELLOW
                if remaining <= 10:
                    color = BarColor.RED
                elif remaining <= 5:
                    color = BarColor.GREEN

                if data["boss_bar"]:
                    try:
                        data["boss_bar"].title = f"§e灵魂出窍剩余 §c{remaining} §e秒"
                        data["boss_bar"].progress = progress
                        data["boss_bar"].color = color
                    except Exception as e:
                        self.plugin.logger.error(f"更新BossBar失败: {e}")

        timer_thread = threading.Thread(target=update_boss_bar, daemon=True)
        timer_thread.start()

        if player_name in self.fcam_boss_bars:
            self.fcam_boss_bars[player_name]["timer"] = timer_thread

    def cleanup_fcam_boss_bar(self, player_name: str):
        if player_name in self.fcam_boss_bars:
            data = self.fcam_boss_bars.pop(player_name)
            if data.get("boss_bar"):
                try:
                    data["boss_bar"].remove_all()
                except:
                    pass

    def on_player_quit(self, player: Player):
        player_name = player.name
        self.cleanup_fcam_boss_bar(player_name)

        if player_name in self.fcam_players:
            simulated_name = self.fcam_players.pop(player_name)
            try:
                self.plugin.server.dispatch_command(
                    self.plugin.server.command_sender,
                    f"removesimulatedplayer {simulated_name}"
                )
            except:
                pass
