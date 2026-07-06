"""
YEssential Fcam System - 灵魂出窍
发包实现: CameraInstruction + AddPlayer + SetPlayerGameType + 拦截移动
"""
import struct
import uuid

from endstone import Player, GameMode
from endstone.level import Location
from bedrock_protocol.packets import MinecraftPackets, MinecraftPacketIds
from .i18n import tr

FAKE_PLAYER_OFFSET = 114514


class FcamSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.fcam_players: dict[str, dict] = {}
        self._address_map: dict = {}  # address -> player
        self.info_prefix = "§l§6[-YEST-] §r"

    def is_enabled(self) -> bool:
        return self.plugin.config_manager.config_data.get("Fcam", {}).get("EnableModule", False)

    def is_in_fcam(self, player: Player) -> bool:
        return player.name in self.fcam_players

    # ═══════════════════════════════════════════════════════
    # 数据包
    # ═══════════════════════════════════════════════════════

    def _pkt(self, pid, **kwargs):
        """创建并序列化数据包"""
        pkt = MinecraftPackets.create_packet(pid)
        for k, v in kwargs.items():
            setattr(pkt, k, v)
        return pkt.serialize()

    def _send_camera_set(self, p: Player):
        p.send_packet(MinecraftPacketIds.CameraInstruction, _encode_camera_set(
            p.location.x, p.location.y + 2, p.location.z, 0, p.location.yaw,
        ))

    def _send_camera_clear(self, p: Player):
        p.send_packet(MinecraftPacketIds.CameraInstruction, _encode_camera_clear())

    def _send_set_gamemode(self, p: Player, gm: GameMode):
        try:
            data = self._pkt(MinecraftPacketIds.SetPlayerGameType, gamemode=gm.value)
            p.send_packet(MinecraftPacketIds.SetPlayerGameType, data)
        except Exception:
            p.send_packet(MinecraftPacketIds.SetPlayerGameType, struct.pack('<i', gm.value))

    def _send_add_player(self, p: Player, fake_uuid: uuid.UUID, fake_eid: int):
        loc = p.location
        try:
            data = self._pkt(
                MinecraftPacketIds.AddPlayer,
                uuid=fake_uuid,
                name=p.name,
                entity_id=fake_eid,
                position=(loc.x, loc.y, loc.z),
                velocity=(0, 0, 0),
                pitch=loc.pitch,
                yaw=loc.yaw,
                gamemode=0,
            )
            p.send_packet(MinecraftPacketIds.AddPlayer, data)
        except Exception:
            # fallback: struct 编码
            self.plugin.logger.warning("[Fcam] AddPlayer fallback, 假身体可能不可见")
            p.send_packet(MinecraftPacketIds.AddPlayer, _encode_add_player(
                fake_uuid, p.name, fake_eid,
                loc.x, loc.y, loc.z, loc.pitch, loc.yaw,
            ))

    def _send_remove_actor(self, p: Player, fake_eid: int):
        try:
            data = self._pkt(MinecraftPacketIds.RemoveActor, entity_id=fake_eid)
            p.send_packet(MinecraftPacketIds.RemoveActor, data)
        except Exception:
            p.send_packet(MinecraftPacketIds.RemoveActor, struct.pack('<q', fake_eid))

    # ═══════════════════════════════════════════════════════
    # 进入 / 退出
    # ═══════════════════════════════════════════════════════

    def enter_fcam(self, player: Player) -> bool:
        if not self.is_enabled():
            player.send_message(self.info_prefix + tr("fcam.disabled"))
            return False
        if self.is_in_fcam(player):
            player.send_message(self.info_prefix + tr("fcam.already"))
            return False

        pn = player.name
        loc = player.location
        fake_uuid = uuid.uuid4()
        fake_eid = player.runtime_id + FAKE_PLAYER_OFFSET

        self.fcam_players[pn] = {
            "x": loc.x, "y": loc.y, "z": loc.z,
            "dimension": loc.dimension,
            "original_gamemode": player.game_mode,
            "fake_uuid": fake_uuid,
            "fake_eid": fake_eid,
        }

        # 1. 切旁观者
        self._send_set_gamemode(player, GameMode.SPECTATOR)
        # 2. 生成假身体
        self._send_add_player(player, fake_uuid, fake_eid)
        # 3. 自由相机
        self._send_camera_set(player)

        player.send_message(self.info_prefix + tr("fcam.entered"))
        return True

    def exit_fcam(self, player: Player) -> bool:
        pn = player.name
        if not self.is_in_fcam(player):
            return False

        data = self.fcam_players.pop(pn)

        self._send_camera_clear(player)
        self._send_set_gamemode(player, data["original_gamemode"])
        self._send_remove_actor(player, data["fake_eid"])
        player.teleport(Location(data["dimension"], data["x"], data["y"], data["z"]))

        player.send_message(self.info_prefix + tr("fcam.exited"))
        return True

    def toggle_fcam(self, player: Player) -> bool:
        if self.is_in_fcam(player):
            return self.exit_fcam(player)
        return self.enter_fcam(player)

    # ═══════════════════════════════════════════════════════
    # 事件
    # ═══════════════════════════════════════════════════════

    def on_player_join(self, player: Player):
        self._address_map[player.address] = player

    def on_player_quit(self, player: Player):
        self._address_map.pop(player.address, None)
        if player.name in self.fcam_players:
            data = self.fcam_players.pop(player.name)
            self._send_remove_actor(player, data["fake_eid"])

    def on_packet_receive(self, event):
        """拦截 PlayerAuthInputPacket → 防止服务端处理灵魂出窍玩家的移动"""
        if event.packet_id == MinecraftPacketIds.PlayerAuthInput:
            player = self._address_map.get(event.address)
            if player and player.name in self.fcam_players:
                event.cancel()

    def on_damage(self, player: Player):
        if player.name in self.fcam_players:
            self.exit_fcam(player)
            player.send_message(self.info_prefix + "§c受到伤害，已退出灵魂出窍模式")

    def on_death(self, player: Player):
        if player.name in self.fcam_players:
            self.fcam_players.pop(player.name, None)


# ═══════════════════════════════════════════════════════════
# CameraInstruction 编码 (struct 手写)
# ═══════════════════════════════════════════════════════════

def _encode_camera_set(x, y, z, pitch, yaw, preset=0, ease=0.5):
    return (
        b'\x01' + struct.pack('<I', preset)
        + b'\x01' + struct.pack('<B', 0) + struct.pack('<f', ease)
        + b'\x01' + struct.pack('<fff', x, y, z)
        + b'\x01' + struct.pack('<ff', pitch, yaw)
        + b'\x00' * 13
    )


def _encode_camera_clear():
    return b'\x00' + b'\x01' + b'\x00' * 8


def _write_varint(value: int) -> bytes:
    result = bytearray()
    value &= 0xFFFFFFFF
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            result.append(byte | 0x80)
        else:
            result.append(byte)
            break
    return bytes(result)


def _write_string(s: str) -> bytes:
    data = s.encode("utf-8")
    return _write_varint(len(data)) + data


def _encode_add_player(u, name, eid, x, y, z, pitch, yaw):
    bs = bytearray()
    bs.extend(u.bytes)
    bs.extend(_write_string(name))
    bs.extend(struct.pack('<q', eid))
    bs.extend(_write_string(""))  # platform chat id
    bs.extend(struct.pack('<fff', x, y, z))
    bs.extend(struct.pack('<fff', 0, 0, 0))  # velocity
    bs.extend(struct.pack('<f', pitch))
    bs.extend(struct.pack('<f', yaw))
    bs.extend(struct.pack('<f', yaw))  # head yaw
    bs.extend(_write_varint(0))  # held item
    bs.extend(_write_varint(0))  # gametype (survival)
    bs.extend(_write_varint(0))  # metadata count
    bs.extend(b'\x00' * 16)  # adventure settings
    bs.extend(_write_varint(0))  # links
    bs.extend(_write_string(""))  # device id
    bs.extend(struct.pack('<i', 0))  # build platform
    return bytes(bs)
