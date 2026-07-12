"""
YEssential Servers System - 跨服传送
"""
import struct, socket, time, threading
from endstone import Player
from .i18n import tr as _tr
from endstone.form import ActionForm, MessageForm
from .log import debug

def tr(key, *args):
    return _tr(key, *args)

_MAGIC = b"\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78"
# cache: key → {motd, level, online, max, proto, latency, expire}
_DATA: dict[str, dict] = {}


def _fetch_async(ip: str, port: int):
    key = f"{ip}:{port}"
    t0 = time.time()
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.0)
        ts = int(t0 * 1000) & 0xFFFFFFFFFFFFFFFF
        sock.sendto(b"\x01" + struct.pack(">Q", ts) + _MAGIC + struct.pack(">Q", 0), (ip, port))
        data, _ = sock.recvfrom(4096)
        lat = int((time.time() - t0) * 1000)
        if len(data) >= 35 and data[0] == 0x1c:
            offset = 33
            ilen = struct.unpack(">H", data[offset:offset+2])[0]
            info = data[offset+2:offset+2+ilen].decode("utf-8", errors="ignore")
            # MCPE;motd;proto;ver;online;max;guid;level;gamemode;...
            p = info.split(";")
            _DATA[key] = {
                "motd":     (p[1] if len(p)>1 else "").replace("§","").replace("\r","").replace("\n"," ").strip(),
                "level":    (p[7] if len(p)>7 else "").replace("§","").replace("\r","").replace("\n"," ").strip(),
                "online":   int(p[4]) if len(p)>4 and p[4].isdigit() else 0,
                "max":      int(p[5]) if len(p)>5 and p[5].isdigit() else 0,
                "proto":    int(p[2]) if len(p)>2 and p[2].isdigit() else 0,
                "version":  (p[3] if len(p)>3 else "").strip(),
                "latency":  lat,
                "expire":   time.time() + 2,
            }
        else:
            _DATA[key] = {"motd":"","level":"","online":0,"max":0,"proto":0,"version":"","latency":-1,"expire":time.time()+2}
    except Exception:
        _DATA[key] = {"motd":"","level":"","online":0,"max":0,"proto":0,"version":"","latency":-1,"expire":time.time()+2}
    finally:
        if sock:
            try: sock.close()
            except: pass


def _get(key: str) -> dict:
    now = time.time()
    d = _DATA.get(key, {})
    if not d or now >= d.get("expire", 0):
        _DATA[key] = {"motd":"","level":"","online":0,"max":0,"proto":0,"version":"","latency":-1,"expire":now+1}
        ip, port_str = key.split(":")
        threading.Thread(target=_fetch_async, args=(ip, int(port_str)), daemon=True).start()
        return d if d else _DATA[key]
    return d


class ServersSystem:
    def __init__(self, plugin):
        self.plugin = plugin

    def start_prefetch(self):
        debug(f"Servers: prefetching {len(self.config.get('servers',[]))} servers")
        for srv in self.config.get("servers", []):
            threading.Thread(target=_fetch_async, args=(
                srv.get("server_ip","0.0.0.0"), srv.get("server_port",19132)), daemon=True).start()
        def refresh():
            for srv in self.config.get("servers", []):
                threading.Thread(target=_fetch_async, args=(
                    srv.get("server_ip","0.0.0.0"), srv.get("server_port",19132)), daemon=True).start()
        self.plugin.server.scheduler.run_task(self.plugin, refresh, 20, 20)

    @property
    def config(self):
        return self.plugin.config_manager.get("CrossServerTransfer", {"EnabledModule":True,"servers":[]})

    def open_server_list(self, player: Player):
        if not self.config.get("EnabledModule", True):
            player.send_message(tr("servers.disabled")); return
        servers = self.config.get("servers", [])
        if not servers:
            player.send_message(tr("servers.empty")); return

        form = ActionForm(title=tr("servers.title"))
        for srv in servers:
            name = srv.get("server_name", tr("servers.unknown"))
            ip, port = srv.get("server_ip","0.0.0.0"), srv.get("server_port",19132)
            d = _get(f"{ip}:{port}")
            motd = d.get("motd","")
            online, mx = d.get("online",0), d.get("max",0)
            lat = d.get("latency",-1)
            if lat<0: clr="§7"
            elif lat<50: clr="§a"
            elif lat<100: clr="§e"
            elif lat<200: clr="§6"
            else: clr="§c"
            lat_str = f"{clr}{lat}ms" if lat>=0 else "§7..."

            line = f"{name}\n§7{motd[:30]}\n§8{online}/{mx}  {lat_str}" if motd else f"{name}\n§8{online}/{mx}  {lat_str}"
            form.add_button(line)

        def on_select(p, idx):
            if idx is None: return
            self._confirm(p, servers[idx])
        form.on_submit = on_select
        player.send_form(form)

    def _confirm(self, player: Player, srv: dict):
        name = srv.get("server_name", tr("servers.unknown"))
        ip, port = srv.get("server_ip","0.0.0.0"), srv.get("server_port",19132)
        d = _get(f"{ip}:{port}")
        motd, level = d.get("motd",""), d.get("level","")
        online, mx = d.get("online",0), d.get("max",0)
        proto, ver = d.get("proto",0), d.get("version","")
        lat = d.get("latency",-1)
        if lat<0: lc="§7"; lt="?"
        elif lat<50: lc="§a"; lt=f"{lat}ms"
        elif lat<100: lc="§e"; lt=f"{lat}ms"
        elif lat<200: lc="§6"; lt=f"{lat}ms"
        else: lc="§c"; lt=f"{lat}ms"
        lat_str = lc+lt

        content = (
            f"§e{tr('servers.confirm_title')}\n\n"
            f"§b{tr('servers.server_name_label')}§f {name}\n"
            f"§bIP: §f{ip}:{port}"
        )
        if motd:  content += f"\n§bMOTD: §7{motd}"
        if level: content += f"\n§b存档: §7{level}"
        if ver:   content += f"\n§b版本: §7{ver} (§7{proto})"
        content += f"\n§b在线: §7{online}/{mx}  §b延迟: §7{lat_str}"
        content += f"\n\n§c{tr('servers.confirm_warn')}"

        form = MessageForm(
            title=tr("servers.title"), content=content,
            button1=tr("servers.confirm_yes"), button2=tr("servers.confirm_no"),
        )
        def cb(p, btn):
            if btn == 0:
                try:
                    p.transfer(ip, port)
                    self.plugin.server.broadcast_message(tr("servers.transferred", p.name, name))
                except Exception as e:
                    p.send_message(tr("servers.fail", str(e)))
        form.on_submit = cb
        player.send_form(form)
