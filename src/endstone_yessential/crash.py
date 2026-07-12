from typing import List
from endstone import Player
from .i18n import tr
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
            player.send_message(self.info_prefix + tr("crash.no_perm"))
            return

        if not self.is_enabled():
            player.send_message(self.info_prefix + tr("crash.disabled"))
            return

        online_players = [p for p in self.plugin.server.online_players if p.name != player.name]

        if not online_players:
            player.send_message(self.info_prefix + tr("crash.no_players"))
            return

        form = ActionForm(title=tr("crash.title"))
        form.content = tr("crash.select")

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
            target.kick(tr("crash.kick_msg"))
            
            operator.send_message(self.info_prefix + tr("crash.crashed", target.name))

            if self.should_log():
                self.plugin.logger.warning(f"Crash: {operator.name} -> {target.name}")

        except Exception as e:
            operator.send_message(self.info_prefix + tr("crash.fail"))
            self.plugin.logger.error(f"Crash player failed: {e}")

    def on_command(self, player: Player) -> bool:
        self.show_crash_menu(player)
        return True
