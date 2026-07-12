"""
YEssential Update Checker - 更新检查
从 GitHub Releases API 检查新版本并通知
"""
import json
import threading
import time
from urllib.request import urlopen, Request
from urllib.error import URLError

from .constant import plugin_version
from .log import plugin_print


class UpdateChecker:
    """GitHub 更新检查器"""

    # GitHub API URL
    UPDATE_URL = "https://api.github.com/repos/Nico6719/YEssential-For-Endstone/releases/latest"

    def __init__(self, plugin):
        self.plugin = plugin
        self._check_interval = 0  # 分钟

    @property
    def config(self):
        return self.plugin.config_manager.config_data.get("Update", {
            "EnableModule": True,
            "CheckInterval": 60
        })

    @property
    def is_enabled(self) -> bool:
        return self.config.get("EnableModule", True)

    def check(self, silent: bool = False):
        """执行一次更新检查 (异步)"""
        if not self.is_enabled:
            return

        def _do_check():
            try:
                req = Request(
                    self.UPDATE_URL,
                    headers={
                        "User-Agent": "YEssential-Endstone-Plugin",
                        "Accept": "application/vnd.github.v3+json"
                    }
                )
                with urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    latest_version = data.get("tag_name", "").lstrip("v")

                    if not latest_version:
                        return

                    # 比较版本号
                    current = [int(x) for x in plugin_version.split(".")]
                    try:
                        latest = [int(x) for x in latest_version.split(".")]
                    except ValueError:
                        return

                    if latest > current:
                        msg = (
                            f"\n{'='*50}\n"
                            f"  §6[YEssential] §a发现新版本！\n"
                            f"  §7当前版本: §c{plugin_version}\n"
                            f"  §7最新版本: §a{latest_version}\n"
                            f"  §7下载地址: §bhttps://github.com/Nico6719/YEssential-For-Endstone/releases/latest\n"
                            f"  §7更新日志: §f{data.get('name', latest_version)}\n"
                            f"{'='*50}"
                        )
                        plugin_print(msg.replace("§", ""))
                        self._notify_ops(msg)
                    elif not silent:
                        plugin_print(f"[UpdateChecker] 已是最新版本 ({plugin_version})")

            except URLError as e:
                if not silent:
                    plugin_print(f"[UpdateChecker] 网络错误: {e}")
            except Exception as e:
                if not silent:
                    plugin_print(f"[UpdateChecker] 检查失败: {e}")

        thread = threading.Thread(target=_do_check, daemon=True)
        thread.start()

    def _notify_ops(self, msg: str):
        """通知所有 OP 玩家"""
        try:
            for player in self.plugin.server.online_players:
                if player.is_op and not player.name.endswith("_sp"):
                    player.send_message(msg)
        except:
            pass

    def start_periodic(self):
        """启动定时检查"""
        self.check(silent=True)  # 启动时静默检查一次

        interval = self.config.get("CheckInterval", 60)
        if interval <= 0:
            return

        self._check_interval = interval

        def periodic():
            while True:
                time.sleep(interval * 60)
                self.check(silent=True)

        thread = threading.Thread(target=periodic, daemon=True)
        thread.start()

    def check_now(self) -> str:
        """同步检查并返回结果字符串"""
        try:
            req = Request(
                self.UPDATE_URL,
                headers={
                    "User-Agent": "YEssential-Endstone-Plugin",
                    "Accept": "application/vnd.github.v3+json"
                }
            )
            with urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                latest_version = data.get("tag_name", "").lstrip("v")

                current = [int(x) for x in plugin_version.split(".")]
                latest = [int(x) for x in latest_version.split(".")]

                if latest > current:
                    return f"§a新版本可用: {latest_version} (当前: {plugin_version})"
                return f"§7已是最新版本 ({plugin_version})"
        except Exception as e:
            return f"§c检查失败: {e}"
