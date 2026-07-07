"""
YEssential Servers System - 跨服传送
列出服务器 → 自动获取MOTD(不阻塞) → 二次确认 → 传送
"""
import struct
import socket
import time
import threading
from endstone import Player
from .i18n import tr as _tr
from endstone.form import ActionForm, MessageForm

def tr(key, *args):
    return _tr(key, *args)

# RakNet 魔数
_MAGIC = b"\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78"
_MOTD_CACHE: dict[str, tuple[str, float]] = {}
_LEVEL_CACHE: dict[str, str] = {}


def _fetch_motd_async(ip: str, port: int):
    """后台线程获取 MOTD"""
    cache_key = f"{ip}:{port}"
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.0)
        ts = int(time.time() * 1000) & 0xFFFFFFFFFFFFFFFF
        ping = b"\x01" + struct.pack(">Q", ts) + _MAGIC + struct.pack(">Q", 0)
        sock.sendto(ping, (ip, port))
        data, _ = sock.recvfrom(4096)
        sock.close()
        if len(data) >= 35 and data[0] == 0x1c:
            offset = 33
            info_len = struct.unpack(">H", data[offset:offset+2])[0]
            info = data[offset+2:offset+2+info_len].decode("utf-8", errors="ignore")
            # BDS pong: MCPE;motd;proto;ver;players;max;guid;level_name;gamemode;...
            parts = info.split(";")
            raw_motd = parts[1] if len(parts) > 1 else ""
            raw_level = parts[7] if len(parts) > 7 else ""
            # 缓存原始值，显示时再决定如何拼接
            _MOTD_CACHE[cache_key] = (
                raw_motd.replace("§", "").replace("\r", "").replace("\n", " ").strip(),
                time.time() + 2
            )
            # 额外缓存存档名
            _LEVEL_CACHE[cache_key] = raw_level.replace("§", "").replace("\r", "").replace("\n", " ").strip()
        else:
            _MOTD_CACHE[cache_key] = ("", time.time() + 2)
    except Exception:
        _MOTD_CACHE[cache_key] = ("", time.time() + 2)


def _get_motd(ip: str, port: int) -> str:
    """获取缓存的 MOTD，并触发后台更新"""
    cache_key = f"{ip}:{port}"
    now = time.time()
    entry = _MOTD_CACHE.get(cache_key)
    if not entry or now >= entry[1]:
        # 缓存过期 → 后台线程获取
        _MOTD_CACHE[cache_key] = ("", now + 1)  # 临时标记
        threading.Thread(target=_fetch_motd_async, args=(ip, port), daemon=True).start()
        # 返回旧值（如果有的话）
        return entry[0] if entry else ""
    return entry[0]


class ServersSystem:
    def __init__(self, plugin):
        self.plugin = plugin

    def start_prefetch(self):
        """插件加载时预取所有服务器 MOTD，之后定时刷新"""
        servers = self.config.get("servers", [])
        for srv in servers:
            ip = srv.get("server_ip", "0.0.0.0")
            port = srv.get("server_port", 19132)
            threading.Thread(target=_fetch_motd_async, args=(ip, port), daemon=True).start()

        # 每 60 秒刷新一次
        def refresh():
            for srv in self.config.get("servers", []):
                ip = srv.get("server_ip", "0.0.0.0")
                port = srv.get("server_port", 19132)
                threading.Thread(target=_fetch_motd_async, args=(ip, port), daemon=True).start()

        self.plugin.server.scheduler.run_task(self.plugin, refresh, 20, 20)

    @property
    def config(self):
        return self.plugin.config_manager.get("CrossServerTransfer", {
            "EnabledModule": True,
            "servers": []
        })

    def open_server_list(self, player: Player):
        if not self.config.get("EnabledModule", True):
            player.send_message(tr("servers.disabled"))
            return

        servers = self.config.get("servers", [])
        if not servers:
            player.send_message(tr("servers.empty"))
            return

        form = ActionForm(title=tr("servers.title"))

        for srv in servers:
            name = srv.get("server_name", tr("servers.unknown"))
            ip = srv.get("server_ip", "0.0.0.0")
            port = srv.get("server_port", 19132)

            motd = _get_motd(ip, port)
            line = f"§f{name}"
            if motd:
                line += f"\n§f{motd[:40]}"
            form.add_button(line)

        def on_select(p, idx):
            if idx is None:
                return
            self._confirm_transfer(p, servers[idx])

        form.on_submit = on_select
        player.send_form(form)

    def _confirm_transfer(self, player: Player, srv: dict):
        name = srv.get("server_name", tr("servers.unknown"))
        ip = srv.get("server_ip", "0.0.0.0")
        port = srv.get("server_port", 19132)
        motd = _get_motd(ip, port) or tr("servers.no_motd")
        level = _LEVEL_CACHE.get(f"{ip}:{port}", "")

        content = (
            f"§e{tr('servers.confirm_title')}\n\n"
            f"§b{tr('servers.server_name_label')}§f {name}\n"
            f"§bIP: §f{ip}:{port}"
        )
        if motd:
            content += f"\n§bMOTD: §7{motd}"
        if level:
            content += f"\n§b存档名: §7{level}"
        content += f"\n\n§c{tr('servers.confirm_warn')}"

        form = MessageForm(
            title=tr("servers.title"),
            content=content,
            button1=tr("servers.confirm_yes"),
            button2=tr("servers.confirm_no"),
        )

        def on_confirm(p, btn_id):
            if btn_id == 0:
                try:
                    p.transfer(ip, port)
                    self.plugin.server.broadcast_message(
                        tr("servers.transferred", p.name, name)
                    )
                except Exception as e:
                    p.send_message(tr("servers.fail", str(e)))

        form.on_submit = on_confirm
        player.send_form(form)
