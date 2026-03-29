import asyncio
from typing import Optional

class MotdSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self._task: Optional[asyncio.Task] = None
        self._index: int = 0
        self._running: bool = False
    
    @property
    def config(self):
        return self.plugin.config_manager.get("Motd", {
            "Enabled": True,
            "message": [
                "§6YEssential §a服务器正在运行中！",
                "§e欢迎来到 §bMinecraft §a服务器！"
            ],
            "interval": 5000
        })
    
    def start_rotation(self):
        if self._task:
            self._task.cancel()
        
        motd_config = self.config
        if not motd_config.get("Enabled", True):
            return
        
        messages = motd_config.get("message", [])
        if not messages:
            return
        
        interval = motd_config.get("interval", 5000) / 1000.0
        self._running = True
        self._task = asyncio.create_task(self._rotate_loop(messages, interval))
    
    def stop_rotation(self):
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
    
    async def _rotate_loop(self, messages: list, interval: float):
        while self._running:
            if messages:
                motd = messages[self._index % len(messages)]
                self.plugin.server.set_motd(motd)
                self._index += 1
            await asyncio.sleep(interval)
    
    def set_motd(self, message: str):
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
        self.plugin.server.set_motd(message)
