"""
YEssential MOTD System - 服务器标题轮播
"""
from .i18n import tr
from endstone.event import event_handler, EventPriority, ServerListPingEvent


class MotdSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self._index = 0
        self._paused = False
        self._task_id = None

    @property
    def config(self):
        return self.plugin.config_manager.config_data.get("Motd", {})

    @property
    def messages(self) -> list:
        return self.config.get("message", [])

    @property
    def interval_ticks(self) -> int:
        return max(20, self.config.get("interval", 5000) // 50)

    # ── 事件处理 ────────────────────────────────────────

    @event_handler(priority=EventPriority.HIGHEST)
    def on_server_list_ping(self, event: ServerListPingEvent):
        if not self.config.get("EnabledModule", True):
            return
        if self._paused:
            wh = self.plugin.config_manager.config_data.get("wh", {})
            msg = wh.get("whmotdmsg", "")
            if msg:
                event.motd = msg
            return
        msgs = self.messages
        if msgs:
            event.motd = msgs[self._index % len(msgs)]

    # ── 轮播定时器 ──────────────────────────────────────

    def start_rotation(self):
        msgs = self.messages
        if not msgs:
            return

        def rotate():
            if not self._paused:
                self._index = (self._index + 1) % len(msgs)

        task = self.plugin.server.scheduler.run_task(
            self.plugin, rotate, self.interval_ticks, self.interval_ticks
        )
        self._task_id = task.task_id if task else None

    def stop_rotation(self):
        if self._task_id is not None:
            try:
                self.plugin.server.scheduler.cancel_task(self._task_id)
            except Exception:
                pass
            self._task_id = None

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False
        if self._task_id is None:
            self.start_rotation()
