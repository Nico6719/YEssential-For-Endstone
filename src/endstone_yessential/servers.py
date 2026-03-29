from endstone import Player
from endstone.form import ActionForm

class ServersSystem:
    def __init__(self, plugin):
        self.plugin = plugin
    
    @property
    def config(self):
        return self.plugin.config_manager.get("CrossServerTransfer", {
            "EnabledModule": True,
            "servers": []
        })
    
    def open_server_list(self, player: Player):
        if not self.config.get("EnabledModule", True):
            player.send_message("§6[YEssential] §c该模块未启用。")
            return
        
        servers = self.config.get("servers", [])
        if not servers:
            player.send_message("§6[YEssential] §c服务器列表为空。")
            return
        
        form = ActionForm(title="§6跨服传送")
        
        for server in servers:
            name = server.get("server_name", "未知服务器")
            ip = server.get("server_ip", "0.0.0.0")
            port = server.get("server_port", 19132)
            form.add_button(f"§b{name}\n§7IP: {ip}:{port}")
        
        def on_select(selected_player, selected_id):
            if selected_id is None:
                return
            target_server = servers[selected_id]
            server_name = target_server.get("server_name", "未知")
            server_ip = target_server.get("server_ip", "0.0.0.0")
            server_port = target_server.get("server_port", 19132)
            
            try:
                selected_player.transfer_server(server_ip, server_port)
                self.plugin.server.broadcast_message(f"§6[YEssential] §a{selected_player.name} 前往了 {server_name}")
            except Exception as e:
                selected_player.send_message(f"§6[YEssential] §c传送失败: {str(e)}")
        
        form.on_submit = on_select
        player.send_form(form)
