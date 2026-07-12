import json
import os
import time
from typing import Dict, List, Any, Optional
from endstone import Player
from endstone.form import ActionForm, ModalForm, Dropdown, TextInput, Label
from endstone.event import event_handler, PlayerInteractEvent
from .i18n import tr

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
            self.plugin.logger.error(f"CD config load fail: {e}")
            self._config = {}
        self.validate()

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.plugin.logger.error(f"CD config save fail: {e}")

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
            "title": tr("cd.server_menu"),
            "content": tr("cd.select"),
            "buttons": [
                {"images": True, "image": "textures/items/apple", "money": 0, "text": "获取一个苹果", "command": "give @s apple", "type": "comm"},
                {"images": False, "image": "textures/items/apple", "money": 0, "text": "发送一句你好", "command": "msg @a 你好", "type": "comm"},
                {"images": False, "image": "textures/items/apple", "money": 0, "text": tr("cd.admin_menu"), "command": "admin", "type": "form", "oplist": []}
            ]
        }

    @staticmethod
    def get_default_admin_menu() -> dict:
        return {
            "title": tr("cd.admin_menu"),
            "content": tr("cd.select"),
            "buttons": [
                {"images": False, "image": "textures/items/apple", "money": 0, "text": tr("cd.menu_settings"), "command": "cd set", "type": "comm", "oplist": []},
                {"images": False, "image": "textures/items/apple", "money": 0, "text": "返回", "command": "main", "type": "form", "oplist": []}
            ]
        }

    @staticmethod
    def get_default_sub_menu() -> dict:
        return {
            "title": tr("cd.default_menu"),
            "content": tr("cd.select"),
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
            self.plugin.logger.error(f"CD menu save fail: {e}")

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
            player.send_message(self.config_manager.prefix + tr("cd.config_error"))
            return
        if len(menu_data["buttons"]) == 0:
            player.send_message(self.config_manager.prefix + tr("cd.empty_buttons"))
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
            player.send_message(self.config_manager.prefix + tr("economy.not_enough"))
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
            player.send_message(self.config_manager.prefix + tr("cd.button_type_error"))
            return

        if required_money > 0:
            self.economy_manager.reduce(player, required_money)

    def handle_op_form(self, player: Player, button: dict, current_menu: str):
        op_list = button.get("oplist", [])
        if not player.is_op and op_list and player.name not in op_list:
            self.show_menu(player, current_menu)
            player.send_message(self.config_manager.prefix + tr("cd.op_only"))
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
            player.send_message(self.config_manager.prefix + tr("cd.op_only"))
            return
        self.execute_command(player, button.get("command", ""))


class MenuAdminHandler:
    def __init__(self, plugin, config_manager: MenuConfigManager, data_manager: MenuDataManager, player_handler: MenuPlayerHandler):
        self.plugin = plugin
        self.config_manager = config_manager
        self.data_manager = data_manager
        self.player_handler = player_handler

    def show_main_settings(self, player: Player):
        form = ActionForm(title=self.config_manager.prefix + tr("cd.menu_settings"))
        form.content = tr("cd.select")
        form.add_button(tr("cd.economy_settings"))
        form.add_button(tr("cd.add_menu"))
        form.add_button(tr("cd.delete_menu"))
        form.add_button(tr("cd.modify_menu"))
        form.add_button(tr("cd.modify_other"))

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

        controls = [
            Dropdown(label=tr("cd.select_economy_mode"), options=[tr("cd.scoreboard"), "LLMoney"], default_index=money_type if money_type is not None else current_money_type),
            TextInput(label=tr("cd.input_scoreboard"), placeholder=f"当前: {current_score}", default_value=score_name if score_name else "")
        ]
        if error:
            controls.append(Label(text=error))

        form = ModalForm(title=tr("cd.set_economy_params"), controls=controls)

        def on_submit(p, data):
            if not data:
                self.show_main_settings(player)
                return
            data = json.loads(data) if isinstance(data, str) else data
            selected_money_type = int(data[0])
            input_score = data[1].strip() if data[1] else ""

            if selected_money_type == current_money_type and input_score == "":
                self.show_money_settings(player, tr("cd.no_operation"), selected_money_type, input_score)
                return

            self.config_manager.set({"money": selected_money_type})
            if input_score:
                self.config_manager.set({"score": input_score})

            player.send_message(self.config_manager.prefix + tr("cd.edit_success"))
            self.show_main_settings(player)

        form.on_submit = on_submit
        player.send_form(form)

    def show_add_menu(self, player: Player, menu_type: str = None):
        if menu_type is None:
            form = ActionForm(title=tr("cd.add_menu"))
            form.content = tr("cd.select_action")
            form.add_button(tr("cd.add_submenu"))
            form.add_button(tr("cd.add_button"))
            form.add_button(tr("cd.back"))

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
            player.send_message(self.config_manager.prefix + tr("cd.no_menu_files"))
            self.show_add_menu(player)
            return

        controls = [
            Dropdown(label=tr("cd.select_parent_menu"), options=file_options, default_index=form_data.get("parentIndex", 0)),
            TextInput(label=tr("cd.submenu_filename"), placeholder="例如: aaa", default_value=form_data.get("fileName", "")),
            TextInput(label=tr("cd.submenu_title"), placeholder="例如: 二级菜单", default_value=form_data.get("title", "")),
            TextInput(label=tr("cd.submenu_content"), placeholder="例如: 选择:", default_value=form_data.get("content", ""))
        ]
        if error:
            controls.append(Label(text=error))

        form = ModalForm(title=tr("cd.add_submenu"), controls=controls)

        def on_submit(p, data):
            if not data:
                self.show_add_menu(player)
                return
            data = json.loads(data) if isinstance(data, str) else data
            parent_index = int(data[0])
            file_name = data[1].strip()
            title = data[2].strip()
            content = data[3].strip()

            if not MenuUtils.is_valid_file_name(file_name):
                self.show_add_sub_menu(player, tr("cd.invalid_filename"), form_data)
                return

            if os.path.exists(os.path.join(self.config_manager.menus_path, file_name + ".json")):
                self.show_add_sub_menu(player, tr("cd.file_exists"), form_data)
                return

            self.data_manager.add_button( menu_files[parent_index], {
                "images": True,
                "image": "textures/items/apple",
                "money": 0,
                "text": title,
                "command": file_name,
                "type": "form"
            })
            self.data_manager.set_menu( file_name, {
                "title": title,
                "content": content or tr("cd.select"),
                "buttons": MenuDataManager.get_default_sub_menu()["buttons"]
            })
            player.send_message(self.config_manager.prefix + tr("cd.add_success"))
            self.show_add_menu(player, "add_menu")

        form.on_submit = on_submit
        player.send_form(form)

    def show_add_button(self, player: Player, error: str = None, form_data: dict = None):
        form_data = form_data or {}
        menu_files = MenuUtils.get_menu_files(config_manager=self.config_manager)
        if not menu_files:
            player.send_message(self.config_manager.prefix + tr("cd.no_menu_files"))
            self.show_add_menu(player)
            return

        file_options = [MenuDataManager.get_default_sub_menu().get("title", "菜单") + " | " + f for f in menu_files]
        button_types = [tr("cd.player_submenu"), tr("cd.admin_submenu"), tr("cd.player_command"), tr("cd.admin_command")]

        controls = [
            Dropdown(label=tr("cd.select_menu_file"), options=file_options, default_index=form_data.get("fileIndex", 0)),
            Dropdown(label=tr("cd.select_button_type"), options=button_types, default_index=form_data.get("buttonType", 0)),
            TextInput(label=tr("cd.button_text"), placeholder="例如: 说你好", default_value=form_data.get("buttonText", "")),
            TextInput(label=tr("cd.button_command"), placeholder="例如: say @a 你好", default_value=form_data.get("command", "")),
            TextInput(label=tr("cd.button_money"), placeholder="例如: 999", default_value=str(form_data.get("money", ""))),
            TextInput(label=tr("cd.button_position"), placeholder="例如: 0", default_value=str(form_data.get("position", "")))
        ]
        if error:
            controls.append(Label(text=error))

        form = ModalForm(title=tr("cd.add_button"), controls=controls)

        def on_submit(p, data):
            if not data:
                self.show_add_menu(player)
                return
            data = json.loads(data) if isinstance(data, str) else data
            file_index = int(data[0])
            type_index = int(data[1])
            button_text = data[2].strip()
            command = data[3].strip()
            money = data[4].strip()
            position = data[5].strip()

            if not button_text or not command:
                self.show_add_button(player, tr("cd.title_command_required"), form_data)
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

            self.data_manager.add_button( menu_files[file_index], new_button, int(position) if position.isdigit() else None)
            player.send_message(self.config_manager.prefix + tr("cd.add_success"))
            self.show_add_menu(player, "add_button")

        form.on_submit = on_submit
        player.send_form(form)

    def show_delete_menu(self, player: Player, delete_type: str = None):
        if delete_type is None:
            form = ActionForm(title=tr("cd.delete_menu"))
            form.content = tr("cd.select_action")
            form.add_button(tr("cd.delete_submenu"))
            form.add_button(tr("cd.delete_button"))
            form.add_button(tr("cd.back"))

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
                player.send_message(self.config_manager.prefix + tr("cd.no_menu_to_delete"))
                self.show_delete_menu(player)
                return

            form = ActionForm(title=tr("cd.delete_submenu"))
            form.content = tr("cd.select_menu_delete")
            for f in files:
                menu_data = self.data_manager.get_menu(f)
                form.add_button((menu_data.get("title", "") or "菜单") + " | " + f)
            form.add_button(tr("cd.back"))

            def on_submit(p, selected):
                if selected is None or selected == len(files):
                    self.show_delete_menu(player)
                    return
                if 0 <= selected < len(files):
                    deleted = files[selected]
                    self.data_manager.delete_menu( deleted)
                    self.data_manager.remove_orphan_buttons( deleted)
                    player.send_message(self.config_manager.prefix + tr("cd.delete_success") + ": " + deleted)
                    self.show_delete_menu(player, delete_type)

            form.on_submit = on_submit
            player.send_form(form)

        elif delete_type == "del_button":
            files = MenuUtils.get_menu_files(config_manager=self.config_manager)
            if not files:
                player.send_message(self.config_manager.prefix + tr("cd.no_menu_available"))
                self.show_delete_menu(player)
                return

            form = ActionForm(title=tr("cd.delete_button"))
            form.content = tr("cd.select_menu")
            for f in files:
                menu_data = self.data_manager.get_menu(f)
                form.add_button((menu_data.get("title", "") or "菜单") + " | " + f)
            form.add_button(tr("cd.back"))

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
            player.send_message(self.config_manager.prefix + tr("cd.menu_no_buttons"))
            self.show_delete_menu(player, "del_button")
            return

        form = ActionForm(title=tr("cd.delete_button_title") + " - " + menu_data.get("title", tr("cd.menu")))
        form.content = tr("cd.select_button_delete")
        for btn in menu_data["buttons"]:
            t = btn.get("text", "") + " [" + btn.get("type", "") + "]"
            if btn.get("money", 0) > 0:
                t += f" (" + tr("cd.need_money", btn["money"]) + ")"
            form.add_button(t)
        form.add_button(tr("cd.back"))

        def on_submit(p, selected):
            if selected is None or selected == len(menu_data["buttons"]):
                self.show_delete_menu(player, "del_button")
                return
            if 0 <= selected < len(menu_data["buttons"]):
                deleted_btn = menu_data["buttons"][selected]
                if self.data_manager.delete_button( file_name, selected):
                    player.send_message(self.config_manager.prefix + tr("cd.delete_success") + ": " + deleted_btn.get("text", ""))
                else:
                    player.send_message(self.config_manager.prefix + tr("cd.delete_fail"))
                self.show_delete_button_list(player, file_name)

        form.on_submit = on_submit
        player.send_form(form)

    def show_edit_menu(self, player: Player, edit_type: str = None):
        if edit_type is None:
            form = ActionForm(title=tr("cd.modify_menu"))
            form.content = tr("cd.select_action")
            form.add_button(tr("cd.edit_menu_info"))
            form.add_button(tr("cd.edit_button"))
            form.add_button(tr("cd.back"))

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
            player.send_message(self.config_manager.prefix + tr("cd.no_menu_available"))
            self.show_edit_menu(player)
            return

        form = ActionForm(title=tr("cd.edit_menu_info"))
        form.content = tr("cd.select_menu_edit")
        for f in files:
            menu_data = self.data_manager.get_menu(f)
            form.add_button((menu_data.get("title", "") or "菜单") + " | " + f)
        form.add_button(tr("cd.back"))

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

        controls = [
            TextInput(label=tr("cd.menu_title"), placeholder=f"当前: {menu_data.get('title', '')}", default_value=menu_data.get('title', '')),
            TextInput(label=tr("cd.menu_content"), placeholder=f"当前: {menu_data.get('content', '')}", default_value=menu_data.get('content', ''))
        ]
        if error:
            controls.append(Label(text=error))

        form = ModalForm(title=tr("cd.edit_menu_title") + ": " + file_name, controls=controls)

        def on_submit(p, data):
            if not data:
                self.show_edit_menu_info(player)
                return
            data = json.loads(data) if isinstance(data, str) else data
            new_title = data[0].strip()
            new_content = data[1].strip()
            if not new_title or not new_content:
                self.show_edit_menu_info_form(player, file_name, tr("cd.title_content_required"))
                return
            menu_data["title"] = new_title
            menu_data["content"] = new_content
            self.data_manager.set_menu( file_name, menu_data)
            player.send_message(self.config_manager.prefix + tr("cd.edit_success"))
            self.show_edit_menu_info(player)

        form.on_submit = on_submit
        player.send_form(form)

    def show_edit_button_select(self, player: Player):
        files = MenuUtils.get_menu_files(config_manager=self.config_manager)
        if not files:
            player.send_message(self.config_manager.prefix + tr("cd.no_menu_available"))
            self.show_edit_menu(player)
            return

        form = ActionForm(title=tr("cd.edit_button"))
        form.content = tr("cd.select_menu")
        for f in files:
            menu_data = self.data_manager.get_menu(f)
            form.add_button((menu_data.get("title", "") or "菜单") + " | " + f)
        form.add_button(tr("cd.back"))

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
            player.send_message(self.config_manager.prefix + tr("cd.menu_no_buttons"))
            self.show_edit_button_select(player)
            return

        form = ActionForm(title=tr("cd.edit_button_title") + " - " + menu_data.get("title", tr("cd.menu")))
        form.content = tr("cd.select_button_edit")
        for btn in menu_data["buttons"]:
            form.add_button(btn.get("text", "") + " [" + btn.get("type", "") + "]")
        form.add_button(tr("cd.back"))

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
        button_types = [tr("cd.player_submenu"), tr("cd.admin_submenu"), tr("cd.player_command"), tr("cd.admin_command")]

        raw_type = button.get("type", "form")
        if raw_type == "vipfm":
            raw_type = "form"
        if raw_type == "vipcm":
            raw_type = "comm"
        current_type_index = type_map.index(raw_type) if raw_type in type_map else 0

        controls = [
            Dropdown(label=tr("cd.select_button_type"), options=button_types, default_index=current_type_index),
            TextInput(label=tr("cd.button_text"), placeholder="例如: 说你好", default_value=button.get("text", "")),
            TextInput(label=tr("cd.button_command"), placeholder="例如: say @a 你好", default_value=button.get("command", "")),
            TextInput(label=tr("cd.button_money"), placeholder="例如: 999", default_value=str(button.get("money", 0)))
        ]
        if error:
            controls.append(Label(text=error))

        form = ModalForm(title=tr("cd.edit_button_title") + ": " + button.get("text", ""), controls=controls)

        def on_submit(p, data):
            if not data:
                self.show_edit_button_list(player, file_name)
                return
            data = json.loads(data) if isinstance(data, str) else data
            type_index = data[0]
            button_text = data[1].strip()
            command = data[2].strip()
            money = data[3].strip()

            if not button_text or not command:
                self.show_edit_button_form(player, file_name, button_index, tr("cd.title_command_required"))
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

            if self.data_manager.update_button( file_name, button_index, new_button):
                player.send_message(self.config_manager.prefix + tr("cd.edit_success"))
            else:
                player.send_message(self.config_manager.prefix + tr("cd.edit_fail"))
            self.show_edit_button_list(player, file_name)

        form.on_submit = on_submit
        player.send_form(form)

    def show_other_settings(self, player: Player, error: str = None):
        files = MenuUtils.get_menu_files(config_manager=self.config_manager)
        main_file = self.config_manager.get_main()

        options = [tr("cd.no_change")] + [f.replace(".json", "") for f in files]
        default_index = 0
        for i, f in enumerate(files):
            if f.replace(".json", "") == main_file:
                default_index = i + 1
                break

        controls = [Dropdown(label=tr("cd.main_menu_file", main_file), options=options, default_index=default_index)]
        if error:
            controls.append(Label(text=error))

        form = ModalForm(title=tr("cd.modify_other"), controls=controls)

        def on_submit(p, data):
            if not data:
                self.show_main_settings(player)
                return
            data = json.loads(data) if isinstance(data, str) else data
            if int(data[0]) > 0:
                self.config_manager.set({"main": files[int(data[0]) - 1].replace(".json", "")})
                self.show_other_settings(player, "§2修改成功")
            else:
                self.show_other_settings(player, tr("cd.no_change"))

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
            player.send_message(tr("cd.clock_claimed"))
            return False

        item = self.plugin.server.item_factory.get_item("minecraft:clock", 1)
        if not item:
            player.send_message(tr("cd.clock_fail"))
            return False

        if not player.inventory.can_hold_item(item):
            player.send_message(tr("cd.inventory_full"))
            return False

        player.inventory.add_item(item)
        self.mark_claimed(player.xuid)
        player.send_message(tr("cd.clock_success"))
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
            player.send_message(tr("cd.not_op"))

    def getclock(self, player: Player):
        self.getclock_handler.execute(player)


class MenuTriggerListener:
    """菜单触发监听器 — 严格按照 JS 版 registerEvents 逻辑
    onUseItemOn(方块) => mode 0/2
    onUseItem(空气)   => mode 1/2
    menuPendingThisTick 防同 tick 双击
    """

    def __init__(self, cd_system: CdSystem):
        self._cd = cd_system
        self._pending = set()

    @event_handler
    def on_player_interact(self, event: PlayerInteractEvent):
        player = event.player
        xuid = player.xuid

        # 同 tick 已触发过，跳过（menuPendingThisTick）
        if xuid in self._pending:
            return

        action = event.action
        trigger_mode = self._cd.config_manager.get_items_trigger_mode()

        # onUseItemOn: mode 0 或 2
        if action == PlayerInteractEvent.RIGHT_CLICK_BLOCK:
            if trigger_mode not in (0, 2):
                return
        # onUseItem: mode 1 或 2
        elif action == PlayerInteractEvent.RIGHT_CLICK_AIR:
            if trigger_mode not in (1, 2):
                return
        else:
            return

        # 检查手持物品是否在触发列表中
        item = player.inventory.item_in_main_hand
        if item is None:
            return

        items = self._cd.config_manager.get_items()
        if item.type not in items:
            return

        # 标记已触发
        self._pending.add(xuid)

        # 打开菜单（JS 版直接调用 showMenu，无延迟）
        self._cd.open_menu(player)

        # 50ms 后清除标记（JS 版 setTimeout）
        def _clear():
            self._pending.discard(xuid)

        self._cd.plugin.server.scheduler.run_task(self._cd.plugin, _clear, 1)
