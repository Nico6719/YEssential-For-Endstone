class MotdSystem:
    def __init__(self, plugin):
        self.plugin = plugin
    
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
        pass
    
    def stop_rotation(self):
        pass
    
    def set_motd(self, message: str):
        pass
