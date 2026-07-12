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
