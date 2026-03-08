from pathlib import Path

# 插件全局常量
plugin_name = "YEssential"
plugin_name_smallest = "yessential"
plugin_description = "基于 Endstone 的 YEssential"
plugin_version = "0.1.0"
plugin_author = ["Nico6719", "梦涵LOVE"]
plugin_license = "AGPL-3.0"
plugin_github_link = "https://github.com/MengHanLOVE1027/endstone-yessential"
plugin_minebbs_link = "https://www.minebbs.com/resources/yessential-elp-endstone.15496/"
plugin_website = "https://www.minebbs.com/resources/yessential-elp-endstone.15496/"
plugin_update_url = "https://raw.githubusercontent.com/MengHanLOVE1027/endstone-yessential/refs/heads/main/update_versions.json"

plugin_path = Path(f"./plugins/{plugin_name}")
plugin_config_path = plugin_path / "config" / f"{plugin_name}.json"