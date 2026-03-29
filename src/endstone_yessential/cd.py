import json
import os
import time
from typing import Dict, List, Any, Optional
from endstone import Player
from endstone.form import ActionForm, ModalForm, CustomForm
from endstone.command import Command, CommandSender

class MenuConfigManager:
    def __init__(self, plugin):
        self.plugin = plugin
        self.config_path = "./plugins/YEssential/Config/Cd/Config.json"
        self.menus_path = "./plugins/YEssential/data/Menus/"
        self.prefix = "§e§l[菜单] §r"
        self.mobile_os = ["Android", "iOS"]
        self._config = {}
        self.ensure_directory()
        self.load()

    def ensure_directory(self):
        data_dir = "./plugins/YEssential/data/"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        if not os.path.exists(self.menus_path):
            os.makedirs(self.menus_path, exist_ok=True)

    def load(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            else:
                self._config = {}
        except Exception as e:
            self.plugin.logger.error(f"菜单配置文件加载失败: {e}")
            self._config = {}
        self.validate()

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.plugin.logger.error(f"菜单配置文件保存失败: {e}")

    def get(self) -> dict:
        return self._config

    def set(self, data: dict):
        for key, value in data.items():
            self._config[key] = value
        self.save()

    def get_money(self) -> int:
        return self._config.get("money", 0)

    def get_score(self) -> str:
        return self._config.get("score", "money")

    def get_items(self) -> List[str]:
        return self._config.get("items", ["minecraft:clock"])

    def get_main(self) -> str:
        return self._config.get("main", "main")

    def get_shield(self) -> List[str]:
        return self._config.get("shield", [])

    def get_items_trigger_mode(self) -> int:
        return self._config.get("itemsTriggerMode", 0)

    def validate(self):
        defaults = {
            "money": 0,
            "score": "money",
            "items": ["minecraft:clock"],
            "itemsTriggerMode": 0,
            "main": "main",
            "shield": []
        }
        needs_save = False
        for key, default_value in defaults.items():
            if key not in self._config:
                self._config[key] = default_value
                needs_save = True
            elif key == "money" and self._config["money"] not in [0, 1]:
                self._config["money"] = default_value
                needs_save = True
            elif key == "itemsTriggerMode" and self._config["itemsTriggerMode"] not in [0, 1, 2]:
                self._config["itemsTriggerMode"] = default_value
                needs_save = True
        if needs_save:
            self.save()


class MenuUtils:
    @staticmethod
    def is_valid_file_name(s: str) -> bool:
        import re
        return bool(re.match(r'^[A-Za-z0-9]+$', s)) and 1 <= len(s) <= 20

    @staticmethod
    def get_menu_files(exclude_main: bool = False, config_manager: MenuConfigManager = None) -> List[str]:
        menus_path = config_manager.menus_path if config_manager else "./plugins/YEssential/data/Menus/"
        if not os.path.exists(menus_path):
            return []
        files = [f for f in os.listdir(menus_path) if f.endswith('.json')]
        if exclude_main and config_manager:
            main_file = config_manager.get_main() + ".json"
            files = [f for f in files if f != main_file]
        return files


class MenuEconomyManager:
    def __init__(self, plugin, config_manager: MenuConfigManager):
        self.plugin = plugin
        self.config_manager = config_manager

    def get(self, player: Player) -> float:
        if not self.config_manager.get_money():
            score = self.config_manager.get_score()
            try:
                return float(player.scoreboard.get_objective(score).get_score(player))
            except:
                return 0.0
        else:
            if hasattr(self.plugin, 'economy') and self.plugin.economy:
                return self.plugin.economy.get_money(player.name)
            return 0.0

    def add(self, player: Player, amount: float):
        if not self.config_manager.get_money():
            score = self.config_manager.get_score()
            try:
                objective = player.scoreboard.get_objective(score)
                current = objective.get_score(player)
                objective.set_score(player, current + int(amount))
            except:
                pass
        else:
            if hasattr(self.plugin, 'economy') and self.plugin.economy:
                self.plugin.economy.add_money(player.name, amount)

    def reduce(self, player: Player, amount: float) -> bool:
        if not self.config_manager.get_money():
            score = self.config_manager.get_score()
            try:
                objective = player.scoreboard.get_objective(score)
                current = objective.get_score(player)
                if current >= amount:
                    objective.set_score(player, current - int(amount))
                    return True
            except:
                pass
            return False
        else:
            if hasattr(self.plugin, 'economy') and self.plugin.economy:
                return self.plugin.economy.reduce_money(player.name, amount)
        return False


class MenuDataManager:
    def __init__(self, plugin, config_manager: MenuConfigManager):
        self.plugin = plugin
        self.config_manager = config_manager

    @staticmethod
    def get_default_main_menu() -> dict:
        return {
            "title": "服务器菜单",
            "content": "选择:",
            "buttons": [
                {"images": True, "image": "textures/items/apple", "money": 0, "text": "获取一个苹果", "command": "give @s apple", "type": "comm"},
                {"images": False, "image": "textures/items/apple", "money": 0, "text": "发送一句你好", "command": "msg @a 你好", "type": "comm"},
                {"images": False, "image": "textures/items/apple", "money": 0, "text": "管理员菜单", "command": "admin", "type": "form", "oplist": []}
            ]
        }

    @staticmethod
    def get_default_admin_menu() -> dict:
        return {
            "title": "管理员菜单",
            "content": "选择:",
            "buttons": [
                {"images": False, "image": "textures/items/apple", "money": 0, "text": "菜单设置", "command": "cd set", "type": "comm", "oplist": []},
                {"images": False, "image": "textures/items/apple", "money": 0, "text": "返回", "command": "main", "type": "form", "oplist": []}
            ]
        }

    @staticmethod
    def get_default_sub_menu() -> dict:
        return {
            "title": "初始菜单",
            "content": "选择:",
            "buttons": [{"images": True, "image": "textures/items/apple", "money": 0, "text": "返回", "command": "main", "type": "form"}]
        }

    def get_menu(self, file_name: str) -> dict:
        if not file_name.endswith(".json"):
            file_name += ".json"
        menu_file = os.path.join(self.config_manager.menus_path, file_name)
        if not os.path.exists(menu_file):
            default = self.get_default_sub_menu()
            self.set_menu(file_name, default)
            return default
        try:
            with open(menu_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return self.get_default_sub_menu()

    def set_menu(self, file_name: str, data: dict):
        if not file_name.endswith(".json"):
            file_name += ".json"
        menu_file = os.path.join(self.config_manager.menus_path, file_name)
        try:
            os.makedirs(os.path.dirname(menu_file), exist_ok=True)
            with open(menu_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.plugin.logger.error(f"保存菜单失败: {e}")

    def delete_menu(self, file_name: str):
        if not file_name.endswith(".json"):
            file_name += ".json"
        menu_file = os.path.join(self.config_manager.menus_path, file_name)
        if os.path.exists(menu_file):
            os.remove(menu_file)

    def remove_orphan_buttons(self, deleted_file_name: str):
        target = deleted_file_name.replace(".json", "")
        if not os.path.exists(self.config_manager.menus_path):
            return
        files = [f for f in os.listdir(self.config_manager.menus_path) if f.endswith('.json')]
        for f in files:
            menu_data = self.get_menu(f)
            if not menu_data or "buttons" not in menu_data:
                continue
            before = len(menu_data["buttons"])
            menu_data["buttons"] = [
                btn for btn in menu_data["buttons"]
                if not ((btn.get("type") == "form" or btn.get("type") == "opfm") and btn.get("command") == target)
            ]
            if len(menu_data["buttons"]) != before:
                self.set_menu(f, menu_data)

    def add_button(self, file_name: str, button: dict, index: Optional[int] = None):
        if not file_name.endswith(".json"):
            file_name += ".json"
        menu_data = self.get_menu(file_name)
        if "buttons" not in menu_data:
            menu_data["buttons"] = []
        if index is None or index == "":
            menu_data["buttons"].append(button)
        else:
            try:
                idx = int(index)
                menu_data["buttons"].insert(idx, button)
            except:
                menu_data["buttons"].append(button)
        self.set_menu(file_name, menu_data)

    def delete_button(self, file_name: str, button_index: int) -> bool:
        if not file_name.endswith(".json"):
            file_name += ".json"
        menu_data = self.get_menu(file_name)
        if "buttons" not in menu_data:
            return False
        if 0 <= button_index < len(menu_data["buttons"]):
            menu_data["buttons"].pop(button_index)
            self.set_menu(file_name, menu_data)
            return True
        return False

    def update_button(self, file_name: str, button_index: int, new_button: dict) -> bool:
        if not file_name.endswith(".json"):
            file_name += ".json"
        menu_data = self.get_menu(file_name)
        if "buttons" not in menu_data:
            return False
        if 0 <= button_index < len(menu_data["buttons"]):
            menu_data["buttons"][button_index] = new_button
            self.set_menu(file_name, menu_data)
            return True
        return False

    def filter_buttons_for_player(self, player: Player, menu_data: dict) -> dict:
        if "buttons" not in menu_data:
            return menu_data
        menu_data["buttons"] = [
            btn for btn in menu_data["buttons"]
            if btn.get("type") not in ["vipfm", "vipcm"]
            and (player.is_op or btn.get("type") not in ["opfm", "opcm"])
        ]
        return menu_data

    def initialize_admin_menu(self):
        admin_file = os.path.join(self.config_manager.menus_path, "admin.json")
        if not os.path.exists(admin_file):
            self.set_menu("admin", self.get_default_admin_menu())

    def initialize_main_menu(self):
        main_file = os.path.join(self.config_manager.menus_path, "main.json")
        if not os.path.exists(main_file):
            self.set_menu("main", self.get_default_main_menu())


class MenuPlayerHandler:
    def __init__(self, plugin, config_manager: MenuConfigManager, data_manager: MenuDataManager, economy_manager: MenuEconomyManager):
        self.plugin = plugin
        self.config_manager = config_manager
        self.data_manager = data_manager
        self.economy_manager = economy_manager
        self.click_cooldown = {}

    def show_menu(self, player: Player, file_name: str):
        menu_data = self.data_manager.get_menu(file_name)
        menu_data = self.data_manager.filter_buttons_for_player(player, menu_data)

        if not menu_data.get("title") or not menu_data.get("content") or not menu_data.get("buttons"):
            player.send_message(self.config_manager.prefix + "菜单配置错误")
            return
        if len(menu_data["buttons"]) == 0:
            player.send_message(self.config_manager.prefix + "菜单按钮为空")
            return

        form = ActionForm(title=self.config_manager.prefix + menu_data["title"])
        form.content = menu_data["content"]

        for button in menu_data["buttons"]:
            if button.get("images"):
                form.add_button(button.get("text", ""), button.get("image", ""))
            else:
                form.add_button(button.get("text", ""))

        def on_submit(p, selected):
            if selected is None:
                return
            if 0 <= selected < len(menu_data["buttons"]):
                self.handle_button_click(player, menu_data["buttons"][selected], file_name)

        form.on_submit = on_submit
        player.send_form(form)

    def handle_button_click(self, player: Player, button: dict, current_menu: str):
        required_money = button.get("money", 0)
        if required_money > 0 and self.economy_manager.get(player) < required_money:
            self.show_menu(player, current_menu)
            player.send_message(self.config_manager.prefix + "金币不足")
            return

        btn_type = button.get("type", "form")
        if btn_type == "form":
            self.show_menu(player, button.get("command", "main"))
        elif btn_type == "opfm":
            self.handle_op_form(player, button, current_menu)
        elif btn_type == "comm":
            self.execute_command(player, button.get("command", ""))
        elif btn_type == "opcm":
            self.handle_op_command(player, button, current_menu)
        else:
            self.show_menu(player, current_menu)
            player.send_message(self.config_manager.prefix + "按钮类型错误")
            return

        if required_money > 0:
            self.economy_manager.reduce(player, required_money)

    def handle_op_form(self, player: Player, button: dict, current_menu: str):
        op_list = button.get("oplist", [])
        if not player.is_op and op_list and player.name not in op_list:
            self.show_menu(player, current_menu)
            player.send_message(self.config_manager.prefix + "此功能仅限管理员使用")
            return
        self.show_menu(player, button.get("command", "main"))

    def execute_command(self, player: Player, command: str):
        if "@s" in command and not player.is_op:
            command = command.replace("@s", player.name)
        player.perform_command(command)

    def handle_op_command(self, player: Player, button: dict, current_menu: str):
        op_list = button.get("oplist", [])
        if not player.is_op and op_list and player.name not in op_list:
            self.show_menu(player, current_menu)
            player.send_message(self.config_manager.prefix + "此功能仅限管理员使用")
            return
        self.execute_command(player, button.get("command", ""))


class MenuAdminHandler:
    def __init__(self, plugin, config_manager: MenuConfigManager, data_manager: MenuDataManager, player_handler: MenuPlayerHandler):
        self.plugin = plugin
        self.config_manager = config_manager
        self.data_manager = data_manager
        self.player_handler = player_handler

    def show_main_settings(self, player: Player):
        form = ActionForm(title=self.config_manager.prefix + "菜单设置")
        form.content = "选择:"
        form.add_button("经济设置")
        form.add_button("添加菜单")
        form.add_button("删除菜单")
        form.add_button("修改菜单")
        form.add_button("修改其他")

        def on_submit(p, selected):
            if selected == 0:
                self.show_money_settings(player)
            elif selected == 1:
                self.show_add_menu(player)
            elif selected == 2:
                self.show_delete_menu(player)
            elif selected == 3:
                self.show_edit_menu(player)
            elif selected == 4:
                self.show_other_settings(player)

        form.on_submit = on_submit
        player.send_form(form)

    def show_money_settings(self, player: Player, error: str = None, money_type: int = None, score_name: str = None):
        current_money_type = self.config_manager.get_money()
        current_score = self.config_manager.get_score()

        form = CustomForm(title="设置经济参数")
        form.add_dropdown("选择经济模式", ["计分板", "LLMoney"], money_type if money_type is not None else current_money_type)
        form.add_input("输入计分板项", f"当前: {current_score}", score_name if score_name else "")

        if error:
            form.add_label(error)

        def on_submit(p, data):
            if not data:
                self.show_main_settings(player)
                return
            selected_money_type = data[0]
            input_score = data[1].strip() if data[1] else ""

            if selected_money_type == current_money_type and input_score == "":
                self.show_money_settings(player, "§l§c你好像什么都没有操作", selected_money_type, input_score)
                return

            self.config_manager.set({"money": selected_money_type})
            if input_score:
                self.config_manager.set({"score": input_score})

            player.send_message(self.config_manager.prefix + "§2修改成功")
            self.show_main_settings(player)

        form.on_submit = on_submit
        player.send_form(form)

    def show_add_menu(self, player: Player, menu_type: str = None):
        if menu_type is None:
            form = ActionForm(title="添加菜单")
            form.content = "选择操作:"
            form.add_button("添加二级菜单")
            form.add_button("添加菜单按钮")
            form.add_button("返回上级")

            def on_submit(p, selected):
                if selected == 0:
                    self.show_add_sub_menu(player)
                elif selected == 1:
                    self.show_add_button(player)
                elif selected == 2:
                    self.show_main_settings(player)

            form.on_submit = on_submit
            player.send_form(form)
            return

        if menu_type == "add_menu":
            self.show_add_sub_menu(player)
        elif menu_type == "add_button":
            self.show_add_button(player)

    def show_add_sub_menu(self, player: Player, error: str = None, form_data: dict = None):
        form_data = form_data or {}
        menu_files = MenuUtils.get_menu_files(config_manager=self.config_manager)
        file_options = [MenuDataManager.get_default_sub_menu().get("title", "菜单") + " | " + f for f in menu_files]

        if not file_options:
            player.send_message(self.config_manager.prefix + "§c没有可用的菜单文件")
            self.show_add_menu(player)
            return

        form = CustomForm(title="添加二级菜单")
        form.add_dropdown("选择上级菜单", file_options, form_data.get("parentIndex", 0))
        form.add_input("二级菜单文件名称", "例如: aaa", form_data.get("fileName", ""))
        form.add_input("二级菜单标题", "例如: 二级菜单", form_data.get("title", ""))
        form.add_input("二级菜单提示", "例如: 选择:", form_data.get("content", ""))

        if error:
            form.add_label(error)

        def on_submit(p, data):
            if not data:
                self.show_add_menu(player)
                return
            parent_index = data[0]
            file_name = data[1].strip()
            title = data[2].strip()
            content = data[3].strip()

            if not MenuUtils.is_valid_file_name(file_name):
                self.show_add_sub_menu(player, "§l§c文件名称不合法", form_data)
                return

            if os.path.exists(os.path.join(self.config_manager.menus_path, file_name + ".json")):
                self.show_add_sub_menu(player, "§l§c文件已存在", form_data)
                return

            MenuDataManager.add_button(self.config_manager, menu_files[parent_index], {
                "images": True,
                "image": "textures/items/apple",
                "money": 0,
                "text": title,
                "command": file_name,
                "type": "form"
            })
            MenuDataManager.set_menu(self.config_manager, file_name, {
                "title": title,
                "content": content or "选择:",
                "buttons": MenuDataManager.get_default_sub_menu()["buttons"]
            })
            player.send_message(self.config_manager.prefix + "§2添加成功")
            self.show_add_menu(player, "add_menu")

        form.on_submit = on_submit
        player.send_form(form)

    def show_add_button(self, player: Player, error: str = None, form_data: dict = None):
        form_data = form_data or {}
        menu_files = MenuUtils.get_menu_files(config_manager=self.config_manager)
        if not menu_files:
            player.send_message(self.config_manager.prefix + "§c没有可用的菜单文件")
            self.show_add_menu(player)
            return

        file_options = [MenuDataManager.get_default_sub_menu().get("title", "菜单") + " | " + f for f in menu_files]
        button_types = ["玩家二级菜单", "管理员二级菜单", "玩家执行指令", "管理员执行指令"]

        form = CustomForm(title="添加菜单按钮")
        form.add_dropdown("选择菜单文件", file_options, form_data.get("fileIndex", 0))
        form.add_dropdown("选择按钮类型", button_types, form_data.get("buttonType", 0))
        form.add_input("按钮标题", "例如: 说你好", form_data.get("buttonText", ""))
        form.add_input("按钮执行指令", "例如: say @a 你好", form_data.get("command", ""))
        form.add_input("按钮所需金币", "例如: 999", str(form_data.get("money", "")))
        form.add_input("按钮位置(0为首)", "例如: 0", str(form_data.get("position", "")))

        if error:
            form.add_label(error)

        def on_submit(p, data):
            if not data:
                self.show_add_menu(player)
                return
            file_index = data[0]
            type_index = data[1]
            button_text = data[2].strip()
            command = data[3].strip()
            money = data[4].strip()
            position = data[5].strip()

            if not button_text or not command:
                self.show_add_button(player, "§c标题和指令必填", form_data)
                return

            type_map = ["form", "opfm", "comm", "opcm"]
            new_button = {
                "images": False,
                "image": "",
                "money": int(money) if money.isdigit() else 0,
                "text": button_text,
                "command": command,
                "type": type_map[type_index]
            }
            if "op" in type_map[type_index]:
                new_button["oplist"] = []

            MenuDataManager.add_button(self.config_manager, menu_files[file_index], new_button, int(position) if position.isdigit() else None)
            player.send_message(self.config_manager.prefix + "§2添加成功")
            self.show_add_menu(player, "add_button")

        form.on_submit = on_submit
        player.send_form(form)

    def show_delete_menu(self, player: Player, delete_type: str = None):
        if delete_type is None:
            form = ActionForm(title="删除菜单")
            form.content = "选择操作:"
            form.add_button("删除二级菜单")
            form.add_button("删除菜单按钮")
            form.add_button("返回上级")

            def on_submit(p, selected):
                if selected == 0:
                    self.show_delete_menu(player, "del_menu")
                elif selected == 1:
                    self.show_delete_menu(player, "del_button")
                elif selected == 2:
                    self.show_main_settings(player)

            form.on_submit = on_submit
            player.send_form(form)
            return

        if delete_type == "del_menu":
            files = MenuUtils.get_menu_files(True, self.config_manager)
            if not files:
                player.send_message(self.config_manager.prefix + "§c无可删除的菜单")
                self.show_delete_menu(player)
                return

            form = ActionForm(title="删除二级菜单")
            form.content = "选择要删除的菜单:"
            for f in files:
                menu_data = self.data_manager.get_menu(f)
                form.add_button((menu_data.get("title", "") or "菜单") + " | " + f)
            form.add_button("§c返回上级")

            def on_submit(p, selected):
                if selected is None or selected == len(files):
                    self.show_delete_menu(player)
                    return
                if 0 <= selected < len(files):
                    deleted = files[selected]
                    MenuDataManager.delete_menu(self.config_manager, deleted)
                    MenuDataManager.remove_orphan_buttons(self.config_manager, deleted)
                    player.send_message(self.config_manager.prefix + "§2删除成功: " + deleted)
                    self.show_delete_menu(player, delete_type)

            form.on_submit = on_submit
            player.send_form(form)

        elif delete_type == "del_button":
            files = MenuUtils.get_menu_files(config_manager=self.config_manager)
            if not files:
                player.send_message(self.config_manager.prefix + "§c无可用的菜单")
                self.show_delete_menu(player)
                return

            form = ActionForm(title="删除菜单按钮")
            form.content = "选择菜单:"
            for f in files:
                menu_data = self.data_manager.get_menu(f)
                form.add_button((menu_data.get("title", "") or "菜单") + " | " + f)
            form.add_button("§c返回上级")

            def on_submit(p, selected):
                if selected is None or selected == len(files):
                    self.show_delete_menu(player)
                    return
                if 0 <= selected < len(files):
                    self.show_delete_button_list(player, files[selected])

            form.on_submit = on_submit
            player.send_form(form)

    def show_delete_button_list(self, player: Player, file_name: str):
        menu_data = self.data_manager.get_menu(file_name)
        if not menu_data.get("buttons") or len(menu_data["buttons"]) == 0:
            player.send_message(self.config_manager.prefix + "§c该菜单没有按钮")
            self.show_delete_menu(player, "del_button")
            return

        form = ActionForm(title="删除按钮 - " + menu_data.get("title", "菜单"))
        form.content = "选择要删除的按钮:"
        for btn in menu_data["buttons"]:
            t = btn.get("text", "") + " [" + btn.get("type", "") + "]"
            if btn.get("money", 0) > 0:
                t += f" (需{btn['money']}金币)"
            form.add_button(t)
        form.add_button("§c返回上级")

        def on_submit(p, selected):
            if selected is None or selected == len(menu_data["buttons"]):
                self.show_delete_menu(player, "del_button")
                return
            if 0 <= selected < len(menu_data["buttons"]):
                deleted_btn = menu_data["buttons"][selected]
                if MenuDataManager.delete_button(self.config_manager, file_name, selected):
                    player.send_message(self.config_manager.prefix + "§2删除成功: " + deleted_btn.get("text", ""))
                else:
                    player.send_message(self.config_manager.prefix + "§c删除失败")
                self.show_delete_button_list(player, file_name)

        form.on_submit = on_submit
        player.send_form(form)

    def show_edit_menu(self, player: Player, edit_type: str = None):
        if edit_type is None:
            form = ActionForm(title="修改菜单")
            form.content = "选择操作:"
            form.add_button("修改菜单信息")
            form.add_button("修改菜单按钮")
            form.add_button("返回上级")

            def on_submit(p, selected):
                if selected == 0:
                    self.show_edit_menu_info(player)
                elif selected == 1:
                    self.show_edit_button_select(player)
                elif selected == 2:
                    self.show_main_settings(player)

            form.on_submit = on_submit
            player.send_form(form)
            return

        if edit_type == "edit_menu":
            self.show_edit_menu_info(player)
        elif edit_type == "edit_button":
            self.show_edit_button_select(player)

    def show_edit_menu_info(self, player: Player):
        files = MenuUtils.get_menu_files(config_manager=self.config_manager)
        if not files:
            player.send_message(self.config_manager.prefix + "§c无可用的菜单")
            self.show_edit_menu(player)
            return

        form = ActionForm(title="修改菜单信息")
        form.content = "选择要修改的菜单:"
        for f in files:
            menu_data = self.data_manager.get_menu(f)
            form.add_button((menu_data.get("title", "") or "菜单") + " | " + f)
        form.add_button("§c返回上级")

        def on_submit(p, selected):
            if selected is None or selected == len(files):
                self.show_edit_menu(player)
                return
            if 0 <= selected < len(files):
                self.show_edit_menu_info_form(player, files[selected])

        form.on_submit = on_submit
        player.send_form(form)

    def show_edit_menu_info_form(self, player: Player, file_name: str, error: str = None):
        menu_data = self.data_manager.get_menu(file_name)

        form = CustomForm(title="修改菜单: " + file_name)
        form.add_input("菜单标题", f"当前: {menu_data.get('title', '')}", menu_data.get('title', ''))
        form.add_input("菜单内容", f"当前: {menu_data.get('content', '')}", menu_data.get('content', ''))

        if error:
            form.add_label(error)

        def on_submit(p, data):
            if not data:
                self.show_edit_menu_info(player)
                return
            new_title = data[0].strip()
            new_content = data[1].strip()
            if not new_title or not new_content:
                self.show_edit_menu_info_form(player, file_name, "§c标题和内容不能为空")
                return
            menu_data["title"] = new_title
            menu_data["content"] = new_content
            MenuDataManager.set_menu(self.config_manager, file_name, menu_data)
            player.send_message(self.config_manager.prefix + "§2修改成功")
            self.show_edit_menu_info(player)

        form.on_submit = on_submit
        player.send_form(form)

    def show_edit_button_select(self, player: Player):
        files = MenuUtils.get_menu_files(config_manager=self.config_manager)
        if not files:
            player.send_message(self.config_manager.prefix + "§c无可用的菜单")
            self.show_edit_menu(player)
            return

        form = ActionForm(title="修改菜单按钮")
        form.content = "选择菜单:"
        for f in files:
            menu_data = self.data_manager.get_menu(f)
            form.add_button((menu_data.get("title", "") or "菜单") + " | " + f)
        form.add_button("§c返回上级")

        def on_submit(p, selected):
            if selected is None or selected == len(files):
                self.show_edit_menu(player)
                return
            if 0 <= selected < len(files):
                self.show_edit_button_list(player, files[selected])

        form.on_submit = on_submit
        player.send_form(form)

    def show_edit_button_list(self, player: Player, file_name: str):
        menu_data = self.data_manager.get_menu(file_name)
        if not menu_data.get("buttons") or len(menu_data["buttons"]) == 0:
            player.send_message(self.config_manager.prefix + "§c该菜单没有按钮")
            self.show_edit_button_select(player)
            return

        form = ActionForm(title="修改按钮 - " + menu_data.get("title", "菜单"))
        form.content = "选择要修改的按钮:"
        for btn in menu_data["buttons"]:
            form.add_button(btn.get("text", "") + " [" + btn.get("type", "") + "]")
        form.add_button("§c返回上级")

        def on_submit(p, selected):
            if selected is None or selected == len(menu_data["buttons"]):
                self.show_edit_button_select(player)
                return
            if 0 <= selected < len(menu_data["buttons"]):
                self.show_edit_button_form(player, file_name, selected)

        form.on_submit = on_submit
        player.send_form(form)

    def show_edit_button_form(self, player: Player, file_name: str, button_index: int, error: str = None):
        menu_data = self.data_manager.get_menu(file_name)
        button = menu_data["buttons"][button_index]

        type_map = ["form", "opfm", "comm", "opcm"]
        button_types = ["玩家二级菜单", "管理员二级菜单", "玩家执行指令", "管理员执行指令"]

        raw_type = button.get("type", "form")
        if raw_type == "vipfm":
            raw_type = "form"
        if raw_type == "vipcm":
            raw_type = "comm"
        current_type_index = type_map.index(raw_type) if raw_type in type_map else 0

        form = CustomForm(title="修改按钮: " + button.get("text", ""))
        form.add_dropdown("按钮类型", button_types, current_type_index)
        form.add_input("按钮标题", "例如: 说你好", button.get("text", ""))
        form.add_input("按钮执行指令", "例如: say @a 你好", button.get("command", ""))
        form.add_input("按钮所需金币", "例如: 999", str(button.get("money", 0)))

        if error:
            form.add_label(error)

        def on_submit(p, data):
            if not data:
                self.show_edit_button_list(player, file_name)
                return
            type_index = data[0]
            button_text = data[1].strip()
            command = data[2].strip()
            money = data[3].strip()

            if not button_text or not command:
                self.show_edit_button_form(player, file_name, button_index, "§c标题和指令不能为空")
                return

            new_button = {
                "images": button.get("images", False),
                "image": button.get("image", ""),
                "money": int(money) if money.isdigit() else 0,
                "text": button_text,
                "command": command,
                "type": type_map[type_index]
            }
            if "op" in type_map[type_index]:
                new_button["oplist"] = button.get("oplist", [])

            if MenuDataManager.update_button(self.config_manager, file_name, button_index, new_button):
                player.send_message(self.config_manager.prefix + "§2修改成功")
            else:
                player.send_message(self.config_manager.prefix + "§c修改失败")
            self.show_edit_button_list(player, file_name)

        form.on_submit = on_submit
        player.send_form(form)

    def show_other_settings(self, player: Player, error: str = None):
        files = MenuUtils.get_menu_files(config_manager=self.config_manager)
        main_file = self.config_manager.get_main()

        form = CustomForm(title="其他设置")
        options = ["不修改"] + [f.replace(".json", "") for f in files]
        default_index = 0
        for i, f in enumerate(files):
            if f.replace(".json", "") == main_file:
                default_index = i + 1
                break
        form.add_dropdown(f"主菜单文件（当前: {main_file}）", options, default_index)

        if error:
            form.add_label(error)

        def on_submit(p, data):
            if not data:
                self.show_main_settings(player)
                return
            if data[0] > 0:
                self.config_manager.set({"main": files[data[0] - 1].replace(".json", "")})
                self.show_other_settings(player, "§2修改成功")
            else:
                self.show_other_settings(player, "§e未做任何修改")

        form.on_submit = on_submit
        player.send_form(form)


class GetClockCommandHandler:
    def __init__(self, plugin):
        self.plugin = plugin
        self.data_path = "./plugins/YEssential/data/getclock_claimed.json"
        self.ensure_file()

    def ensure_file(self):
        if not os.path.exists(self.data_path):
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def load_claimed(self) -> List[str]:
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except:
            return []

    def save_claimed(self, data: List[str]):
        try:
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except:
            pass

    def has_claimed(self, xuid: str) -> bool:
        return xuid in self.load_claimed()

    def mark_claimed(self, xuid: str):
        data = self.load_claimed()
        if xuid not in data:
            data.append(xuid)
            self.save_claimed(data)

    def execute(self, player: Player) -> bool:
        if self.has_claimed(player.xuid):
            player.send_message("§6[YEssential] §c你已经领取过钟表了")
            return False

        item = self.plugin.server.item_factory.get_item("minecraft:clock", 1)
        if not item:
            player.send_message("§6[YEssential] §c获取钟表失败")
            return False

        if not player.inventory.can_hold_item(item):
            player.send_message("§6[YEssential] §c背包已满，请清理背包后重试")
            return False

        player.inventory.add_item(item)
        self.mark_claimed(player.xuid)
        player.send_message("§6[YEssential] §a已获得钟表，此物品每人仅限领取一次")
        return True


class CdSystem:
    def __init__(self, plugin):
        self.plugin = plugin
        self.config_manager = MenuConfigManager(plugin)
        self.data_manager = MenuDataManager(plugin, self.config_manager)
        self.economy_manager = MenuEconomyManager(plugin, self.config_manager)
        self.player_handler = MenuPlayerHandler(plugin, self.config_manager, self.data_manager, self.economy_manager)
        self.admin_handler = MenuAdminHandler(plugin, self.config_manager, self.data_manager, self.player_handler)
        self.getclock_handler = GetClockCommandHandler(plugin)

        self.data_manager.initialize_admin_menu()
        self.data_manager.initialize_main_menu()

    def open_menu(self, player: Player):
        self.player_handler.show_menu(player, self.config_manager.get_main())

    def open_settings(self, player: Player):
        if player.is_op:
            self.admin_handler.show_main_settings(player)
        else:
            player.send_message("§6[YEssential] §c你不是管理员!")

    def getclock(self, player: Player):
        self.getclock_handler.execute(player)
