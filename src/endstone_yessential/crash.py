from typing import List
from endstone import Player
from endstone.form import ActionForm

class CrashSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.info_prefix = "§l§6[-YEST-] §r"

    def is_enabled(self) -> bool:
        config = self.plugin.config_manager.get_config()
        return config.get("Crash", {}).get("EnabledModule", False)

    def should_log(self) -> bool:
        config = self.plugin.config_manager.get_config()
        return config.get("Crash", {}).get("LogCrashInfo", True)

    def show_crash_menu(self, player: Player):
        if not player.is_op:
            player.send_message(self.info_prefix + "§c你不是管理员")
            return

        if not self.is_enabled():
            player.send_message(self.info_prefix + "§c该模块未启用")
            return

        online_players = [p for p in self.plugin.server.online_players if p.name != player.name]

        if not online_players:
            player.send_message(self.info_prefix + "§c当前没有其他在线玩家")
            return

        form = ActionForm(title="§c使玩家客户端崩溃")
        form.content = "选择要崩溃的玩家:"

        for p in online_players:
            form.add_button(f"§c{p.name}")

        def on_submit(p, selected):
            if selected is None:
                return
            if 0 <= selected < len(online_players):
                target = online_players[selected]
                self.crash_player(p, target)

        form.on_submit = on_submit
        player.send_form(form)

    def crash_player(self, operator: Player, target: Player):
        try:
            target.kick("§c客户端崩溃")
            
            operator.send_message(self.info_prefix + f"§a已使 {target.name} 客户端崩溃")

            if self.should_log():
                self.plugin.logger.warning(f"[Crash] {operator.name} 对 {target.name} 执行了 crash 操作")

        except Exception as e:
            operator.send_message(self.info_prefix + "§c崩溃操作失败")
            self.plugin.logger.error(f"崩溃玩家失败: {e}")

    def on_command(self, player: Player) -> bool:
        self.show_crash_menu(player)
        return True
