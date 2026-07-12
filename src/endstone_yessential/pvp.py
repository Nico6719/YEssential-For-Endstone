"""
YEssential PVP System - PVP 设置与伤害防护
支持玩家独立开关 PVP 并拦截非 PVP 玩家的伤害事件
"""
import os
import json
from typing import Dict
from endstone import Player
from endstone.event import event_handler, ActorDamageEvent
from endstone.form import ActionForm

from .log import plugin_print
from .i18n import tr


class PVPSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.data_folder = plugin.data_folder
        self.pvp_path = os.path.join(self.data_folder, "pvp_settings.json")
        self.pvp_settings: Dict[str, bool] = {}
        self.load_pvp_settings()

    def load_pvp_settings(self):
        if not os.path.exists(self.pvp_path):
            self.pvp_settings = {}
            self.save_pvp_settings()
        else:
            try:
                with open(self.pvp_path, "r", encoding="utf-8") as f:
                    self.pvp_settings = json.load(f)
            except Exception as e:
                plugin_print(f"Failed to load PVP settings: {e}")
                self.pvp_settings = {}

    def save_pvp_settings(self):
        try:
            with open(self.pvp_path, "w", encoding="utf-8") as f:
                json.dump(self.pvp_settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            plugin_print(f"Failed to save PVP settings: {e}")

    def is_pvp_enabled(self, player_name: str) -> bool:
        """检查玩家是否开启 PVP (默认开启)"""
        return self.pvp_settings.get(player_name, True)

    def set_pvp(self, player: Player, enabled: bool):
        """设置玩家 PVP 状态"""
        self.pvp_settings[player.name] = enabled
        self.save_pvp_settings()
        player.send_message(tr("pvp.set_on") if enabled else tr("pvp.set_off"))

    def init_player_default(self, player: Player):
        """初始化玩家默认PVP设置 (join时调用)"""
        if player.name not in self.pvp_settings:
            self.pvp_settings[player.name] = True  # 默认开启PVP

    # ── 伤害事件监听 (在主插件中注册) ──────────────────────

    def on_actor_damage(self, event: ActorDamageEvent):
        """
        拦截 PVP 伤害事件
        需要在主插件中注册: @event_handler

        Endstone 的 DamageSource 可能通过以下方式访问攻击者:
        - source.damaging_entity / source.entity
        - source.attacker (自定义实现)
        我们通过 hasattr 防御性检查所有可能的属性名
        """
        try:
            victim = event.actor
            source = event.damage_source

            # 尝试多种可能的属性名获取攻击者
            attacker = None
            for attr in ("damaging_entity", "entity", "attacker", "damaging_actor",
                         "source_entity", "get_damaging_entity"):
                try:
                    val = getattr(source, attr, None)
                    if val is not None:
                        # 如果是方法则调用
                        if callable(val):
                            val = val()
                        if val is not None:
                            attacker = val
                            break
                except Exception:
                    continue

            if attacker is None:
                return  # 无法识别攻击者，不拦截

            # 检查双方是否都是 Player 实例
            from endstone import Player as P
            if not isinstance(victim, P) or not isinstance(attacker, P):
                return

            # 排除模拟玩家
            if victim.name.endswith("_sp") or attacker.name.endswith("_sp"):
                return

            # 任一方关闭PVP则取消伤害
            if not self.is_pvp_enabled(victim.name) or not self.is_pvp_enabled(attacker.name):
                event.is_cancelled = True
        except Exception:
            # 静默处理，PVP 拦截失败不应影响正常游戏
            pass

    # ── GUI ────────────────────────────────────────────────

    def open_pvp_gui(self, player: Player):
        current_status = self.is_pvp_enabled(player.name)
        form = ActionForm(
            title=tr("pvp.title"),
            content=tr("pvp.status", tr("pvp.enabled") if current_status else tr("pvp.disabled"))
        )
        form.add_button(tr("pvp.on_btn"), on_click=lambda p: self.set_pvp(p, True))
        form.add_button(tr("pvp.off_btn"), on_click=lambda p: self.set_pvp(p, False))
        form.add_button(tr("pvp.close"))
        player.send_form(form)
