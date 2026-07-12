## [v0.1.0-beta.1] - 2026-07-12

### ♻️ 重构

- 重写 RTP 系统，用 /spreadplayers 替代手动方块扫描
- Remove permissions related to test
- Clean up examples
- Use hatchling as the build backend instead of setuptools
- Datetime import in example_listener.py
- Logging messages in player join/quit events due to api change
- Update imports due to upstream API change
- Update to new plugin api
- Rename project
- Rename project and simplify pyproject.toml
- Use new command registration api
- Remove parentheses
- Plugin structure
### 🐛 修复

- 更新星标历史图表链接以指向正确的仓库
- 修正README中的图像链接和用户统计信息
- 修复发送版本信息时使用翻译函数
- 修复清理实体失败问题，改用 level.dimensions 遍历 actors
- 修复清理实体失败问题，改用 level.dimensions 遍历 actors
- Remove incompatible APIs (set_motd, transfer_server) and simplify code
- Remove non-existent PlayerHurtEvent import, use ActorDamageEvent
- 改善文件目录
- Avoid imports from endstone._internal
- Project name in pyproject.toml
### 📚 文档

- Update README.md
- Update README.md
- Update README.md
- Update README.md
- Update README.md
### 📝 其他

- Delete YEssential-main directory
- Merge branch 'dev' of https://github.com/Nico6719/YEssential-For-Endstone into dev
- 上传测试
- Replace CustomForm with ModalForm (not available in Endstone)
- Migrate 5 new modules from LSE: cd, fcam, redpacket, crash, cleanmgr
- Fix API compatibility issues

- Fix self.plugin.server to self.server in main.py tpa command
- Fix player.location.world to player.location.dimension in hub.py
- Replace get_world()/worlds with server.level in hub.py
- Test
- 删除不再使用的工作流文件和许可证
- 意义不明的commit
- Rename mian.py to main.py
- Create 2234
- Refactor plugin initialization and update exports
- Create plugin.yml for YEssential plugin

Added plugin.yml for YEssential with permissions and commands.
- Create clean.py
- Implement suicide system for players
- Implement HubSystem for player teleportation and GUI
- Add notice system for player notifications

Implement a notice system for players with options to show or hide notices, and an editor for OPs to set notice content.
- Add back system for death location tracking

Implement a back system to record and teleport to player death locations.
- Add PVP system with state management and GUI

Implement a PVP system allowing players to toggle their PVP state, handle entity damage events, and open a PVP settings GUI.
- Add Red Packet system for player interactions

Implement a Red Packet system allowing players to send and receive virtual red packets with configurable amounts and counts. Includes GUI for sending, opening, and viewing red packets.
- Create tpa.py
- Add RTP system for random teleportation

Implement a random teleportation system with cooldown, cost, and safety checks.
- Add warp system for player teleportation

Implement a warp system allowing players to create, delete, and teleport to warps. Includes GUI for managing warps and saving/loading warp data.
- Add home system with GUI for player management

Implement home system for players including setting, deleting, and teleporting to homes. Also includes GUI for managing homes.
- Create economy.py
- Create language.py
- Add ConfigManager class for configuration handling
- Update and rename YEssential.py to mian.py
- Rename example_plugin.py to YEssential.py
- Merge pull request #2 from umarurize/feat/update-api-version
- Merge pull request #1 from smartcmd/feat/update-api-version
- Add sample plugin
- Initial commit
### 🔧 杂项

- V0.1.0-beta.1
- V0.1.0-beta1
- Bump api version
- Bump plugin version to v0.4.0
- Update api version
### 🚀 新功能

- 添加死亡记录查看功能和TPA设置管理，优化相关国际化支持
- 添加菜单触发监听器，优化菜单交互逻辑
- Feat(i18n): 添加菜单相关的多语言支持和翻译字符串
feat(cd): 优化菜单功能，添加右键钟表打开菜单的事件处理
fix(fcam): 修复 PlayerAuthInputPacket 的处理逻辑
- 添加调试日志功能并改进国际化
- Refactor code structure for improved readability and maintainability
- 引入国际化支持，更新多个模块以使用翻译函数
- 添加多语言支持，更新配置管理器的日志信息
- Add YEssential Sign-In System and Update Checker
- Add missing features from original YEssential
- Nico不会写Endstone的插件UwU
- 删除似人README内容
- 简单一点的更新，后续继续写
- Update api version to 0.6
- Update api version to 0.5
- Add an example of Server.dispatch_command
- Add example of explicitly removing one's permission of using a given command
- Add `/kickme` command
- Send current time to all online players
- Add example for scheduler
- Update player join/quit log messages
- Add examples of PlayerJoinEvent and PlayerQuitEvent
- Add an event handler for ServerListPingEvent to customise server info displayed to players
- Add an example of setting event handling priority
- Update ExamplePlugin to use @event_handler decorator
- Add ServerLoadEvent handling in example plugin
- Add api_version to ExamplePlugin class
- Add more usages to the test command
- Use pattern matching to handle different command cases
- Add example commands
## [v0.1.0-beta.1] - 2026-07-12

### ♻️ 重构

- 重写 RTP 系统，用 /spreadplayers 替代手动方块扫描
- Remove permissions related to test
- Clean up examples
- Use hatchling as the build backend instead of setuptools
- Datetime import in example_listener.py
- Logging messages in player join/quit events due to api change
- Update imports due to upstream API change
- Update to new plugin api
- Rename project
- Rename project and simplify pyproject.toml
- Use new command registration api
- Remove parentheses
- Plugin structure
### 🐛 修复

- 更新星标历史图表链接以指向正确的仓库
- 修正README中的图像链接和用户统计信息
- 修复发送版本信息时使用翻译函数
- 修复清理实体失败问题，改用 level.dimensions 遍历 actors
- 修复清理实体失败问题，改用 level.dimensions 遍历 actors
- Remove incompatible APIs (set_motd, transfer_server) and simplify code
- Remove non-existent PlayerHurtEvent import, use ActorDamageEvent
- 改善文件目录
- Avoid imports from endstone._internal
- Project name in pyproject.toml
### 📚 文档

- Update README.md
- Update README.md
- Update README.md
- Update README.md
- Update README.md
### 📝 其他

- Delete YEssential-main directory
- Merge branch 'dev' of https://github.com/Nico6719/YEssential-For-Endstone into dev
- 上传测试
- Replace CustomForm with ModalForm (not available in Endstone)
- Migrate 5 new modules from LSE: cd, fcam, redpacket, crash, cleanmgr
- Fix API compatibility issues

- Fix self.plugin.server to self.server in main.py tpa command
- Fix player.location.world to player.location.dimension in hub.py
- Replace get_world()/worlds with server.level in hub.py
- Test
- 删除不再使用的工作流文件和许可证
- 意义不明的commit
- Rename mian.py to main.py
- Create 2234
- Refactor plugin initialization and update exports
- Create plugin.yml for YEssential plugin

Added plugin.yml for YEssential with permissions and commands.
- Create clean.py
- Implement suicide system for players
- Implement HubSystem for player teleportation and GUI
- Add notice system for player notifications

Implement a notice system for players with options to show or hide notices, and an editor for OPs to set notice content.
- Add back system for death location tracking

Implement a back system to record and teleport to player death locations.
- Add PVP system with state management and GUI

Implement a PVP system allowing players to toggle their PVP state, handle entity damage events, and open a PVP settings GUI.
- Add Red Packet system for player interactions

Implement a Red Packet system allowing players to send and receive virtual red packets with configurable amounts and counts. Includes GUI for sending, opening, and viewing red packets.
- Create tpa.py
- Add RTP system for random teleportation

Implement a random teleportation system with cooldown, cost, and safety checks.
- Add warp system for player teleportation

Implement a warp system allowing players to create, delete, and teleport to warps. Includes GUI for managing warps and saving/loading warp data.
- Add home system with GUI for player management

Implement home system for players including setting, deleting, and teleporting to homes. Also includes GUI for managing homes.
- Create economy.py
- Create language.py
- Add ConfigManager class for configuration handling
- Update and rename YEssential.py to mian.py
- Rename example_plugin.py to YEssential.py
- Merge pull request #2 from umarurize/feat/update-api-version
- Merge pull request #1 from smartcmd/feat/update-api-version
- Add sample plugin
- Initial commit
### 🔧 杂项

- V0.1.0-beta.1
- V0.1.0-beta1
- Bump api version
- Bump plugin version to v0.4.0
- Update api version
### 🚀 新功能

- 添加死亡记录查看功能和TPA设置管理，优化相关国际化支持
- 添加菜单触发监听器，优化菜单交互逻辑
- Feat(i18n): 添加菜单相关的多语言支持和翻译字符串
feat(cd): 优化菜单功能，添加右键钟表打开菜单的事件处理
fix(fcam): 修复 PlayerAuthInputPacket 的处理逻辑
- 添加调试日志功能并改进国际化
- Refactor code structure for improved readability and maintainability
- 引入国际化支持，更新多个模块以使用翻译函数
- 添加多语言支持，更新配置管理器的日志信息
- Add YEssential Sign-In System and Update Checker
- Add missing features from original YEssential
- Nico不会写Endstone的插件UwU
- 删除似人README内容
- 简单一点的更新，后续继续写
- Update api version to 0.6
- Update api version to 0.5
- Add an example of Server.dispatch_command
- Add example of explicitly removing one's permission of using a given command
- Add `/kickme` command
- Send current time to all online players
- Add example for scheduler
- Update player join/quit log messages
- Add examples of PlayerJoinEvent and PlayerQuitEvent
- Add an event handler for ServerListPingEvent to customise server info displayed to players
- Add an example of setting event handling priority
- Update ExamplePlugin to use @event_handler decorator
- Add ServerLoadEvent handling in example plugin
- Add api_version to ExamplePlugin class
- Add more usages to the test command
- Use pattern matching to handle different command cases
- Add example commands
## [v0.1.0-beta.1] - 2026-07-12

### ♻️ 重构

- 重写 RTP 系统，用 /spreadplayers 替代手动方块扫描
- Remove permissions related to test
- Clean up examples
- Use hatchling as the build backend instead of setuptools
- Datetime import in example_listener.py
- Logging messages in player join/quit events due to api change
- Update imports due to upstream API change
- Update to new plugin api
- Rename project
- Rename project and simplify pyproject.toml
- Use new command registration api
- Remove parentheses
- Plugin structure
### 🐛 修复

- 更新星标历史图表链接以指向正确的仓库
- 修正README中的图像链接和用户统计信息
- 修复发送版本信息时使用翻译函数
- 修复清理实体失败问题，改用 level.dimensions 遍历 actors
- 修复清理实体失败问题，改用 level.dimensions 遍历 actors
- Remove incompatible APIs (set_motd, transfer_server) and simplify code
- Remove non-existent PlayerHurtEvent import, use ActorDamageEvent
- 改善文件目录
- Avoid imports from endstone._internal
- Project name in pyproject.toml
### 📚 文档

- Update README.md
- Update README.md
- Update README.md
- Update README.md
- Update README.md
### 📝 其他

- Delete YEssential-main directory
- Merge branch 'dev' of https://github.com/Nico6719/YEssential-For-Endstone into dev
- 上传测试
- Replace CustomForm with ModalForm (not available in Endstone)
- Migrate 5 new modules from LSE: cd, fcam, redpacket, crash, cleanmgr
- Fix API compatibility issues

- Fix self.plugin.server to self.server in main.py tpa command
- Fix player.location.world to player.location.dimension in hub.py
- Replace get_world()/worlds with server.level in hub.py
- Test
- 删除不再使用的工作流文件和许可证
- 意义不明的commit
- Rename mian.py to main.py
- Create 2234
- Refactor plugin initialization and update exports
- Create plugin.yml for YEssential plugin

Added plugin.yml for YEssential with permissions and commands.
- Create clean.py
- Implement suicide system for players
- Implement HubSystem for player teleportation and GUI
- Add notice system for player notifications

Implement a notice system for players with options to show or hide notices, and an editor for OPs to set notice content.
- Add back system for death location tracking

Implement a back system to record and teleport to player death locations.
- Add PVP system with state management and GUI

Implement a PVP system allowing players to toggle their PVP state, handle entity damage events, and open a PVP settings GUI.
- Add Red Packet system for player interactions

Implement a Red Packet system allowing players to send and receive virtual red packets with configurable amounts and counts. Includes GUI for sending, opening, and viewing red packets.
- Create tpa.py
- Add RTP system for random teleportation

Implement a random teleportation system with cooldown, cost, and safety checks.
- Add warp system for player teleportation

Implement a warp system allowing players to create, delete, and teleport to warps. Includes GUI for managing warps and saving/loading warp data.
- Add home system with GUI for player management

Implement home system for players including setting, deleting, and teleporting to homes. Also includes GUI for managing homes.
- Create economy.py
- Create language.py
- Add ConfigManager class for configuration handling
- Update and rename YEssential.py to mian.py
- Rename example_plugin.py to YEssential.py
- Merge pull request #2 from umarurize/feat/update-api-version
- Merge pull request #1 from smartcmd/feat/update-api-version
- Add sample plugin
- Initial commit
### 🔧 杂项

- V0.1.0-beta.1
- V0.1.0-beta1
- Bump api version
- Bump plugin version to v0.4.0
- Update api version
### 🚀 新功能

- 添加死亡记录查看功能和TPA设置管理，优化相关国际化支持
- 添加菜单触发监听器，优化菜单交互逻辑
- Feat(i18n): 添加菜单相关的多语言支持和翻译字符串
feat(cd): 优化菜单功能，添加右键钟表打开菜单的事件处理
fix(fcam): 修复 PlayerAuthInputPacket 的处理逻辑
- 添加调试日志功能并改进国际化
- Refactor code structure for improved readability and maintainability
- 引入国际化支持，更新多个模块以使用翻译函数
- 添加多语言支持，更新配置管理器的日志信息
- Add YEssential Sign-In System and Update Checker
- Add missing features from original YEssential
- Nico不会写Endstone的插件UwU
- 删除似人README内容
- 简单一点的更新，后续继续写
- Update api version to 0.6
- Update api version to 0.5
- Add an example of Server.dispatch_command
- Add example of explicitly removing one's permission of using a given command
- Add `/kickme` command
- Send current time to all online players
- Add example for scheduler
- Update player join/quit log messages
- Add examples of PlayerJoinEvent and PlayerQuitEvent
- Add an event handler for ServerListPingEvent to customise server info displayed to players
- Add an example of setting event handling priority
- Update ExamplePlugin to use @event_handler decorator
- Add ServerLoadEvent handling in example plugin
- Add api_version to ExamplePlugin class
- Add more usages to the test command
- Use pattern matching to handle different command cases
- Add example commands
## [v0.1.0-beta.1] - 2026-07-12

### ♻️ 重构

- 重写 RTP 系统，用 /spreadplayers 替代手动方块扫描
- Remove permissions related to test
- Clean up examples
- Use hatchling as the build backend instead of setuptools
- Datetime import in example_listener.py
- Logging messages in player join/quit events due to api change
- Update imports due to upstream API change
- Update to new plugin api
- Rename project
- Rename project and simplify pyproject.toml
- Use new command registration api
- Remove parentheses
- Plugin structure
### 🐛 修复

- 更新星标历史图表链接以指向正确的仓库
- 修正README中的图像链接和用户统计信息
- 修复发送版本信息时使用翻译函数
- 修复清理实体失败问题，改用 level.dimensions 遍历 actors
- 修复清理实体失败问题，改用 level.dimensions 遍历 actors
- Remove incompatible APIs (set_motd, transfer_server) and simplify code
- Remove non-existent PlayerHurtEvent import, use ActorDamageEvent
- 改善文件目录
- Avoid imports from endstone._internal
- Project name in pyproject.toml
### 📚 文档

- Update README.md
- Update README.md
- Update README.md
- Update README.md
- Update README.md
### 📝 其他

- Delete YEssential-main directory
- Merge branch 'dev' of https://github.com/Nico6719/YEssential-For-Endstone into dev
- 上传测试
- Replace CustomForm with ModalForm (not available in Endstone)
- Migrate 5 new modules from LSE: cd, fcam, redpacket, crash, cleanmgr
- Fix API compatibility issues

- Fix self.plugin.server to self.server in main.py tpa command
- Fix player.location.world to player.location.dimension in hub.py
- Replace get_world()/worlds with server.level in hub.py
- Test
- 删除不再使用的工作流文件和许可证
- 意义不明的commit
- Rename mian.py to main.py
- Create 2234
- Refactor plugin initialization and update exports
- Create plugin.yml for YEssential plugin

Added plugin.yml for YEssential with permissions and commands.
- Create clean.py
- Implement suicide system for players
- Implement HubSystem for player teleportation and GUI
- Add notice system for player notifications

Implement a notice system for players with options to show or hide notices, and an editor for OPs to set notice content.
- Add back system for death location tracking

Implement a back system to record and teleport to player death locations.
- Add PVP system with state management and GUI

Implement a PVP system allowing players to toggle their PVP state, handle entity damage events, and open a PVP settings GUI.
- Add Red Packet system for player interactions

Implement a Red Packet system allowing players to send and receive virtual red packets with configurable amounts and counts. Includes GUI for sending, opening, and viewing red packets.
- Create tpa.py
- Add RTP system for random teleportation

Implement a random teleportation system with cooldown, cost, and safety checks.
- Add warp system for player teleportation

Implement a warp system allowing players to create, delete, and teleport to warps. Includes GUI for managing warps and saving/loading warp data.
- Add home system with GUI for player management

Implement home system for players including setting, deleting, and teleporting to homes. Also includes GUI for managing homes.
- Create economy.py
- Create language.py
- Add ConfigManager class for configuration handling
- Update and rename YEssential.py to mian.py
- Rename example_plugin.py to YEssential.py
- Merge pull request #2 from umarurize/feat/update-api-version
- Merge pull request #1 from smartcmd/feat/update-api-version
- Add sample plugin
- Initial commit
### 🔧 杂项

- V0.1.0-beta.1
- V0.1.0-beta1
- Bump api version
- Bump plugin version to v0.4.0
- Update api version
### 🚀 新功能

- 添加死亡记录查看功能和TPA设置管理，优化相关国际化支持
- 添加菜单触发监听器，优化菜单交互逻辑
- Feat(i18n): 添加菜单相关的多语言支持和翻译字符串
feat(cd): 优化菜单功能，添加右键钟表打开菜单的事件处理
fix(fcam): 修复 PlayerAuthInputPacket 的处理逻辑
- 添加调试日志功能并改进国际化
- Refactor code structure for improved readability and maintainability
- 引入国际化支持，更新多个模块以使用翻译函数
- 添加多语言支持，更新配置管理器的日志信息
- Add YEssential Sign-In System and Update Checker
- Add missing features from original YEssential
- Nico不会写Endstone的插件UwU
- 删除似人README内容
- 简单一点的更新，后续继续写
- Update api version to 0.6
- Update api version to 0.5
- Add an example of Server.dispatch_command
- Add example of explicitly removing one's permission of using a given command
- Add `/kickme` command
- Send current time to all online players
- Add example for scheduler
- Update player join/quit log messages
- Add examples of PlayerJoinEvent and PlayerQuitEvent
- Add an event handler for ServerListPingEvent to customise server info displayed to players
- Add an example of setting event handling priority
- Update ExamplePlugin to use @event_handler decorator
- Add ServerLoadEvent handling in example plugin
- Add api_version to ExamplePlugin class
- Add more usages to the test command
- Use pattern matching to handle different command cases
- Add example commands
## [v0.1.0-beta.1] - 2026-07-12

### ♻️ 重构

- 重写 RTP 系统，用 /spreadplayers 替代手动方块扫描
- Remove permissions related to test
- Clean up examples
- Use hatchling as the build backend instead of setuptools
- Datetime import in example_listener.py
- Logging messages in player join/quit events due to api change
- Update imports due to upstream API change
- Update to new plugin api
- Rename project
- Rename project and simplify pyproject.toml
- Use new command registration api
- Remove parentheses
- Plugin structure
### 🐛 修复

- 更新星标历史图表链接以指向正确的仓库
- 修正README中的图像链接和用户统计信息
- 修复发送版本信息时使用翻译函数
- 修复清理实体失败问题，改用 level.dimensions 遍历 actors
- 修复清理实体失败问题，改用 level.dimensions 遍历 actors
- Remove incompatible APIs (set_motd, transfer_server) and simplify code
- Remove non-existent PlayerHurtEvent import, use ActorDamageEvent
- 改善文件目录
- Avoid imports from endstone._internal
- Project name in pyproject.toml
### 📚 文档

- Update README.md
- Update README.md
- Update README.md
- Update README.md
- Update README.md
### 📝 其他

- Delete YEssential-main directory
- Merge branch 'dev' of https://github.com/Nico6719/YEssential-For-Endstone into dev
- 上传测试
- Replace CustomForm with ModalForm (not available in Endstone)
- Migrate 5 new modules from LSE: cd, fcam, redpacket, crash, cleanmgr
- Fix API compatibility issues

- Fix self.plugin.server to self.server in main.py tpa command
- Fix player.location.world to player.location.dimension in hub.py
- Replace get_world()/worlds with server.level in hub.py
- Test
- 删除不再使用的工作流文件和许可证
- 意义不明的commit
- Rename mian.py to main.py
- Create 2234
- Refactor plugin initialization and update exports
- Create plugin.yml for YEssential plugin

Added plugin.yml for YEssential with permissions and commands.
- Create clean.py
- Implement suicide system for players
- Implement HubSystem for player teleportation and GUI
- Add notice system for player notifications

Implement a notice system for players with options to show or hide notices, and an editor for OPs to set notice content.
- Add back system for death location tracking

Implement a back system to record and teleport to player death locations.
- Add PVP system with state management and GUI

Implement a PVP system allowing players to toggle their PVP state, handle entity damage events, and open a PVP settings GUI.
- Add Red Packet system for player interactions

Implement a Red Packet system allowing players to send and receive virtual red packets with configurable amounts and counts. Includes GUI for sending, opening, and viewing red packets.
- Create tpa.py
- Add RTP system for random teleportation

Implement a random teleportation system with cooldown, cost, and safety checks.
- Add warp system for player teleportation

Implement a warp system allowing players to create, delete, and teleport to warps. Includes GUI for managing warps and saving/loading warp data.
- Add home system with GUI for player management

Implement home system for players including setting, deleting, and teleporting to homes. Also includes GUI for managing homes.
- Create economy.py
- Create language.py
- Add ConfigManager class for configuration handling
- Update and rename YEssential.py to mian.py
- Rename example_plugin.py to YEssential.py
- Merge pull request #2 from umarurize/feat/update-api-version
- Merge pull request #1 from smartcmd/feat/update-api-version
- Add sample plugin
- Initial commit
### 🔧 杂项

- V0.1.0-beta.1
- V0.1.0-beta1
- Bump api version
- Bump plugin version to v0.4.0
- Update api version
### 🚀 新功能

- 添加死亡记录查看功能和TPA设置管理，优化相关国际化支持
- 添加菜单触发监听器，优化菜单交互逻辑
- Feat(i18n): 添加菜单相关的多语言支持和翻译字符串
feat(cd): 优化菜单功能，添加右键钟表打开菜单的事件处理
fix(fcam): 修复 PlayerAuthInputPacket 的处理逻辑
- 添加调试日志功能并改进国际化
- Refactor code structure for improved readability and maintainability
- 引入国际化支持，更新多个模块以使用翻译函数
- 添加多语言支持，更新配置管理器的日志信息
- Add YEssential Sign-In System and Update Checker
- Add missing features from original YEssential
- Nico不会写Endstone的插件UwU
- 删除似人README内容
- 简单一点的更新，后续继续写
- Update api version to 0.6
- Update api version to 0.5
- Add an example of Server.dispatch_command
- Add example of explicitly removing one's permission of using a given command
- Add `/kickme` command
- Send current time to all online players
- Add example for scheduler
- Update player join/quit log messages
- Add examples of PlayerJoinEvent and PlayerQuitEvent
- Add an event handler for ServerListPingEvent to customise server info displayed to players
- Add an example of setting event handling priority
- Update ExamplePlugin to use @event_handler decorator
- Add ServerLoadEvent handling in example plugin
- Add api_version to ExamplePlugin class
- Add more usages to the test command
- Use pattern matching to handle different command cases
- Add example commands
## [v0.1.0-beta.1] - 2026-07-12

### ♻️ 重构

- 重写 RTP 系统，用 /spreadplayers 替代手动方块扫描
- Remove permissions related to test
- Clean up examples
- Use hatchling as the build backend instead of setuptools
- Datetime import in example_listener.py
- Logging messages in player join/quit events due to api change
- Update imports due to upstream API change
- Update to new plugin api
- Rename project
- Rename project and simplify pyproject.toml
- Use new command registration api
- Remove parentheses
- Plugin structure
### 🐛 修复

- 更新星标历史图表链接以指向正确的仓库
- 修正README中的图像链接和用户统计信息
- 修复发送版本信息时使用翻译函数
- 修复清理实体失败问题，改用 level.dimensions 遍历 actors
- 修复清理实体失败问题，改用 level.dimensions 遍历 actors
- Remove incompatible APIs (set_motd, transfer_server) and simplify code
- Remove non-existent PlayerHurtEvent import, use ActorDamageEvent
- 改善文件目录
- Avoid imports from endstone._internal
- Project name in pyproject.toml
### 📚 文档

- Update README.md
- Update README.md
- Update README.md
- Update README.md
- Update README.md
### 📝 其他

- Delete YEssential-main directory
- Merge branch 'dev' of https://github.com/Nico6719/YEssential-For-Endstone into dev
- 上传测试
- Replace CustomForm with ModalForm (not available in Endstone)
- Migrate 5 new modules from LSE: cd, fcam, redpacket, crash, cleanmgr
- Fix API compatibility issues

- Fix self.plugin.server to self.server in main.py tpa command
- Fix player.location.world to player.location.dimension in hub.py
- Replace get_world()/worlds with server.level in hub.py
- Test
- 删除不再使用的工作流文件和许可证
- 意义不明的commit
- Rename mian.py to main.py
- Create 2234
- Refactor plugin initialization and update exports
- Create plugin.yml for YEssential plugin

Added plugin.yml for YEssential with permissions and commands.
- Create clean.py
- Implement suicide system for players
- Implement HubSystem for player teleportation and GUI
- Add notice system for player notifications

Implement a notice system for players with options to show or hide notices, and an editor for OPs to set notice content.
- Add back system for death location tracking

Implement a back system to record and teleport to player death locations.
- Add PVP system with state management and GUI

Implement a PVP system allowing players to toggle their PVP state, handle entity damage events, and open a PVP settings GUI.
- Add Red Packet system for player interactions

Implement a Red Packet system allowing players to send and receive virtual red packets with configurable amounts and counts. Includes GUI for sending, opening, and viewing red packets.
- Create tpa.py
- Add RTP system for random teleportation

Implement a random teleportation system with cooldown, cost, and safety checks.
- Add warp system for player teleportation

Implement a warp system allowing players to create, delete, and teleport to warps. Includes GUI for managing warps and saving/loading warp data.
- Add home system with GUI for player management

Implement home system for players including setting, deleting, and teleporting to homes. Also includes GUI for managing homes.
- Create economy.py
- Create language.py
- Add ConfigManager class for configuration handling
- Update and rename YEssential.py to mian.py
- Rename example_plugin.py to YEssential.py
- Merge pull request #2 from umarurize/feat/update-api-version
- Merge pull request #1 from smartcmd/feat/update-api-version
- Add sample plugin
- Initial commit
### 🔧 杂项

- V0.1.0-beta.1
- V0.1.0-beta1
- Bump api version
- Bump plugin version to v0.4.0
- Update api version
### 🚀 新功能

- 添加死亡记录查看功能和TPA设置管理，优化相关国际化支持
- 添加菜单触发监听器，优化菜单交互逻辑
- Feat(i18n): 添加菜单相关的多语言支持和翻译字符串
feat(cd): 优化菜单功能，添加右键钟表打开菜单的事件处理
fix(fcam): 修复 PlayerAuthInputPacket 的处理逻辑
- 添加调试日志功能并改进国际化
- Refactor code structure for improved readability and maintainability
- 引入国际化支持，更新多个模块以使用翻译函数
- 添加多语言支持，更新配置管理器的日志信息
- Add YEssential Sign-In System and Update Checker
- Add missing features from original YEssential
- Nico不会写Endstone的插件UwU
- 删除似人README内容
- 简单一点的更新，后续继续写
- Update api version to 0.6
- Update api version to 0.5
- Add an example of Server.dispatch_command
- Add example of explicitly removing one's permission of using a given command
- Add `/kickme` command
- Send current time to all online players
- Add example for scheduler
- Update player join/quit log messages
- Add examples of PlayerJoinEvent and PlayerQuitEvent
- Add an event handler for ServerListPingEvent to customise server info displayed to players
- Add an example of setting event handling priority
- Update ExamplePlugin to use @event_handler decorator
- Add ServerLoadEvent handling in example plugin
- Add api_version to ExamplePlugin class
- Add more usages to the test command
- Use pattern matching to handle different command cases
- Add example commands
## [v0.1.0-beta.1] - 2026-07-12

### ♻️ 重构

- 重写 RTP 系统，用 /spreadplayers 替代手动方块扫描
- Remove permissions related to test
- Clean up examples
- Use hatchling as the build backend instead of setuptools
- Datetime import in example_listener.py
- Logging messages in player join/quit events due to api change
- Update imports due to upstream API change
- Update to new plugin api
- Rename project
- Rename project and simplify pyproject.toml
- Use new command registration api
- Remove parentheses
- Plugin structure
### 🐛 修复

- 更新星标历史图表链接以指向正确的仓库
- 修正README中的图像链接和用户统计信息
- 修复发送版本信息时使用翻译函数
- 修复清理实体失败问题，改用 level.dimensions 遍历 actors
- 修复清理实体失败问题，改用 level.dimensions 遍历 actors
- Remove incompatible APIs (set_motd, transfer_server) and simplify code
- Remove non-existent PlayerHurtEvent import, use ActorDamageEvent
- 改善文件目录
- Avoid imports from endstone._internal
- Project name in pyproject.toml
### 📚 文档

- Update README.md
- Update README.md
- Update README.md
- Update README.md
- Update README.md
### 📝 其他

- Delete YEssential-main directory
- Merge branch 'dev' of https://github.com/Nico6719/YEssential-For-Endstone into dev
- 上传测试
- Replace CustomForm with ModalForm (not available in Endstone)
- Migrate 5 new modules from LSE: cd, fcam, redpacket, crash, cleanmgr
- Fix API compatibility issues

- Fix self.plugin.server to self.server in main.py tpa command
- Fix player.location.world to player.location.dimension in hub.py
- Replace get_world()/worlds with server.level in hub.py
- Test
- 删除不再使用的工作流文件和许可证
- 意义不明的commit
- Rename mian.py to main.py
- Create 2234
- Refactor plugin initialization and update exports
- Create plugin.yml for YEssential plugin

Added plugin.yml for YEssential with permissions and commands.
- Create clean.py
- Implement suicide system for players
- Implement HubSystem for player teleportation and GUI
- Add notice system for player notifications

Implement a notice system for players with options to show or hide notices, and an editor for OPs to set notice content.
- Add back system for death location tracking

Implement a back system to record and teleport to player death locations.
- Add PVP system with state management and GUI

Implement a PVP system allowing players to toggle their PVP state, handle entity damage events, and open a PVP settings GUI.
- Add Red Packet system for player interactions

Implement a Red Packet system allowing players to send and receive virtual red packets with configurable amounts and counts. Includes GUI for sending, opening, and viewing red packets.
- Create tpa.py
- Add RTP system for random teleportation

Implement a random teleportation system with cooldown, cost, and safety checks.
- Add warp system for player teleportation

Implement a warp system allowing players to create, delete, and teleport to warps. Includes GUI for managing warps and saving/loading warp data.
- Add home system with GUI for player management

Implement home system for players including setting, deleting, and teleporting to homes. Also includes GUI for managing homes.
- Create economy.py
- Create language.py
- Add ConfigManager class for configuration handling
- Update and rename YEssential.py to mian.py
- Rename example_plugin.py to YEssential.py
- Merge pull request #2 from umarurize/feat/update-api-version
- Merge pull request #1 from smartcmd/feat/update-api-version
- Add sample plugin
- Initial commit
### 🔧 杂项

- V0.1.0-beta.1
- V0.1.0-beta1
- Bump api version
- Bump plugin version to v0.4.0
- Update api version
### 🚀 新功能

- 添加死亡记录查看功能和TPA设置管理，优化相关国际化支持
- 添加菜单触发监听器，优化菜单交互逻辑
- Feat(i18n): 添加菜单相关的多语言支持和翻译字符串
feat(cd): 优化菜单功能，添加右键钟表打开菜单的事件处理
fix(fcam): 修复 PlayerAuthInputPacket 的处理逻辑
- 添加调试日志功能并改进国际化
- Refactor code structure for improved readability and maintainability
- 引入国际化支持，更新多个模块以使用翻译函数
- 添加多语言支持，更新配置管理器的日志信息
- Add YEssential Sign-In System and Update Checker
- Add missing features from original YEssential
- Nico不会写Endstone的插件UwU
- 删除似人README内容
- 简单一点的更新，后续继续写
- Update api version to 0.6
- Update api version to 0.5
- Add an example of Server.dispatch_command
- Add example of explicitly removing one's permission of using a given command
- Add `/kickme` command
- Send current time to all online players
- Add example for scheduler
- Update player join/quit log messages
- Add examples of PlayerJoinEvent and PlayerQuitEvent
- Add an event handler for ServerListPingEvent to customise server info displayed to players
- Add an example of setting event handling priority
- Update ExamplePlugin to use @event_handler decorator
- Add ServerLoadEvent handling in example plugin
- Add api_version to ExamplePlugin class
- Add more usages to the test command
- Use pattern matching to handle different command cases
- Add example commands
## [v0.1.0-beta.1] - 2026-07-12

### ♻️ 重构

- 重写 RTP 系统，用 /spreadplayers 替代手动方块扫描
- Remove permissions related to test
- Clean up examples
- Use hatchling as the build backend instead of setuptools
- Datetime import in example_listener.py
- Logging messages in player join/quit events due to api change
- Update imports due to upstream API change
- Update to new plugin api
- Rename project
- Rename project and simplify pyproject.toml
- Use new command registration api
- Remove parentheses
- Plugin structure
### 🐛 修复

- 更新星标历史图表链接以指向正确的仓库
- 修正README中的图像链接和用户统计信息
- 修复发送版本信息时使用翻译函数
- 修复清理实体失败问题，改用 level.dimensions 遍历 actors
- 修复清理实体失败问题，改用 level.dimensions 遍历 actors
- Remove incompatible APIs (set_motd, transfer_server) and simplify code
- Remove non-existent PlayerHurtEvent import, use ActorDamageEvent
- 改善文件目录
- Avoid imports from endstone._internal
- Project name in pyproject.toml
### 📚 文档

- Update README.md
- Update README.md
- Update README.md
- Update README.md
- Update README.md
### 📝 其他

- Delete YEssential-main directory
- Merge branch 'dev' of https://github.com/Nico6719/YEssential-For-Endstone into dev
- 上传测试
- Replace CustomForm with ModalForm (not available in Endstone)
- Migrate 5 new modules from LSE: cd, fcam, redpacket, crash, cleanmgr
- Fix API compatibility issues

- Fix self.plugin.server to self.server in main.py tpa command
- Fix player.location.world to player.location.dimension in hub.py
- Replace get_world()/worlds with server.level in hub.py
- Test
- 删除不再使用的工作流文件和许可证
- 意义不明的commit
- Rename mian.py to main.py
- Create 2234
- Refactor plugin initialization and update exports
- Create plugin.yml for YEssential plugin

Added plugin.yml for YEssential with permissions and commands.
- Create clean.py
- Implement suicide system for players
- Implement HubSystem for player teleportation and GUI
- Add notice system for player notifications

Implement a notice system for players with options to show or hide notices, and an editor for OPs to set notice content.
- Add back system for death location tracking

Implement a back system to record and teleport to player death locations.
- Add PVP system with state management and GUI

Implement a PVP system allowing players to toggle their PVP state, handle entity damage events, and open a PVP settings GUI.
- Add Red Packet system for player interactions

Implement a Red Packet system allowing players to send and receive virtual red packets with configurable amounts and counts. Includes GUI for sending, opening, and viewing red packets.
- Create tpa.py
- Add RTP system for random teleportation

Implement a random teleportation system with cooldown, cost, and safety checks.
- Add warp system for player teleportation

Implement a warp system allowing players to create, delete, and teleport to warps. Includes GUI for managing warps and saving/loading warp data.
- Add home system with GUI for player management

Implement home system for players including setting, deleting, and teleporting to homes. Also includes GUI for managing homes.
- Create economy.py
- Create language.py
- Add ConfigManager class for configuration handling
- Update and rename YEssential.py to mian.py
- Rename example_plugin.py to YEssential.py
- Merge pull request #2 from umarurize/feat/update-api-version
- Merge pull request #1 from smartcmd/feat/update-api-version
- Add sample plugin
- Initial commit
### 🔧 杂项

- V0.1.0-beta.1
- V0.1.0-beta1
- Bump api version
- Bump plugin version to v0.4.0
- Update api version
### 🚀 新功能

- 添加死亡记录查看功能和TPA设置管理，优化相关国际化支持
- 添加菜单触发监听器，优化菜单交互逻辑
- Feat(i18n): 添加菜单相关的多语言支持和翻译字符串
feat(cd): 优化菜单功能，添加右键钟表打开菜单的事件处理
fix(fcam): 修复 PlayerAuthInputPacket 的处理逻辑
- 添加调试日志功能并改进国际化
- Refactor code structure for improved readability and maintainability
- 引入国际化支持，更新多个模块以使用翻译函数
- 添加多语言支持，更新配置管理器的日志信息
- Add YEssential Sign-In System and Update Checker
- Add missing features from original YEssential
- Nico不会写Endstone的插件UwU
- 删除似人README内容
- 简单一点的更新，后续继续写
- Update api version to 0.6
- Update api version to 0.5
- Add an example of Server.dispatch_command
- Add example of explicitly removing one's permission of using a given command
- Add `/kickme` command
- Send current time to all online players
- Add example for scheduler
- Update player join/quit log messages
- Add examples of PlayerJoinEvent and PlayerQuitEvent
- Add an event handler for ServerListPingEvent to customise server info displayed to players
- Add an example of setting event handling priority
- Update ExamplePlugin to use @event_handler decorator
- Add ServerLoadEvent handling in example plugin
- Add api_version to ExamplePlugin class
- Add more usages to the test command
- Use pattern matching to handle different command cases
- Add example commands
# Changelog

All notable changes to YEssential (EndStone Python version) will be documented in this file.

---

## [0.1.0-beta.3] - 2026-07-12

### 🔧 修复与改进

- 完善 GitHub Actions 自动构建发布流程（合并 auto-tag 和 release 为单一 workflow）
- 修复 release notes 生成中 `echo | head` 导致 Broken pipe 错误
- 优化贡献者提取，使用 GitHub Compare API 一次性获取所有提交和作者
- 优化 release body 结构：CHANGELOG 总结 + 逐条提交 @作者 + 汇总贡献者
- 过滤 bot 提交，release notes 只显示真人贡献者
- Release 标题统一为 `vx.x.x` 格式

---

## [0.1.0-beta.2] - 2026-07-12

### 🔧 修复与改进

- 修复右键钟表无法呼出菜单的问题（改用 `player.inventory.item_in_main_hand` 检测手持物品）
- 修复 `PlayerInteractEvent` 未注册导致菜单事件不触发
- 修复 `fcam.py` 中 `PlayerAuthInput` → `PlayerAuthInputPacket` 属性名错误
- 修复经济系统「查看玩家金币」和「历史记录」的表单叠加闪烁问题
- 新增 `/tpasettings` 命令（开关 TPA 接收）
- 新增 `/deathlog` 命令（死亡记录查询）
- 新增 `/noticeset` 命令（公告管理）
- 新增 `/rtpreset` 命令（重置 RTP 冷却）
- 新增 `/redpacket` 和 `/redpackethelp` 命令
- 新增 `MenuTriggerListener` 独立监听器，修复菜单触发逻辑
- 新增 EasyCheckUpdate 支持（`update_url` 类属性）
- 新增 GitHub Actions 自动构建发布（PR + 自动打 tag + Release）
- README 更新为 EndStone Python 版信息

---

## [0.1.0-beta.1] - 2026-07-12

### 🎉 首个测试版

- 基于 EndStone 框架的 Python 重构版本
- 经济系统：支持计分板/LLMoney 双模式，排行榜，税率，交易历史
- 菜单系统：钟表右键呼出，GUI 编辑器，多级菜单
- 家园系统：GUI 管理多家园
- 公共传送点 (Warp)
- 玩家互传 (TPA)：支持 `/tpasettings` 屏蔽请求
- 随机传送 (RTP)：跨维度安全传送，冷却，花费
- 死亡回溯 (Back) + 死亡记录查询 (DeathLog)
- 回城 (Hub)：`/sethub` 设置回城点
- 个人 PVP 开关
- 维护模式：禁止非管理员进入
- 实体/掉落物自动清理：TPS 检测，白名单
- 动态 MOTD 轮播
- 公告系统：游戏内在线编辑
- 红包系统：随机/固定金额，离线缓存
- 跨服传送菜单
- 灵魂出窍 (Fcam)
- 每日签到：连续签到奖励
- 崩溃管理（管理员工具）
- 自杀功能
- 多语言国际化 (zh_CN / en_US)
- 开服自动开启死亡不掉落
- EasyCheckUpdate 支持
- 自动更新检查
