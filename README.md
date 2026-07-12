<div align="center">

![YEssential](https://socialify.git.ci/Nico6719/YEssential-For-Endstone/image?custom_language=Python&description=1&font=Inter&forks=1&issues=1&language=1&logo=https://zh.minecraft.wiki/images/Bookshelf_JE4_BE2.png?21f85&name=1&owner=1&pattern=Plus&pulls=1&stargazers=1&theme=Auto)

# 📦 YEssential

**基于 EndStone 的多功能基础插件**

![](https://img.shields.io/github/v/release/Nico6719/YEssential-For-Endstone?style=flat-square&logo=github&color=orange&label=Version)
![](https://img.shields.io/github/downloads/Nico6719/YEssential-For-Endstone/total?style=flat-square&logo=github&color=33ccff&label=Downloads)
![](https://img.shields.io/github/languages/top/Nico6719/YEssential-For-Endstone?style=flat-square&logo=python&color=yellow)

![](https://img.shields.io/github/stars/Nico6719/YEssential-For-Endstone?style=flat-square&logo=github&color=yellow&label=Stars)
![](https://img.shields.io/github/last-commit/Nico6719/YEssential-For-Endstone?style=flat-square&color=lightgrey)
![](https://komarev.com/ghpvc/?username=Nico6719&repo=YEssential-For-Endstone&color=green&style=flat-square&label=Views)

</div>

---

> 一个简洁、实用的多功能基础插件，适用于基岩版服务器。基于 EndStone 框架重构的 Python 版本，支持国际化、完整的 GUI 交互体验。

## 📌 基本信息

- **名称**：YEssential
- **类型**：基础插件 / 多功能模块化插件
- **平台**：EndStone (Python)
- **主要功能**：提供服务器基础功能（Home / TPA / Warp / Money / 菜单 / RTP 等）
- **语言支持**：中文 / English（i18n 国际化）

---

### 📦 安装方法

1. 下载 `.whl` 文件放入 `plugins/` 目录
2. 重启服务器

---

## ⚙️ 功能

| 功能          | 描述                                                   | 状态 |
| ------------- | ------------------------------------------------------ | ---- |
| Economic      | 经济核心（支持计分板/LLMoney），排行榜，税率，历史记录 | ✅   |
| 菜单          | 钟表右键呼出菜单，GUI 编辑器，多级菜单                 | ✅   |
| Hub           | 一键回城，/sethub 设置传送点                           | ✅   |
| RTP           | 随机传送，支持不同维度安全传送，动画，冷却，花费       | ✅   |
| TPA           | 玩家互传系统，支持 /tpasettings 屏蔽请求               | ✅   |
| Home          | 家园系统，GUI 管理多家园                               | ✅   |
| Warp          | 公共传送点系统                                         | ✅   |
| Fcam          | 灵魂出窍（旁观者模式）                                 | 🚧 开发中   |
| Back          | 返回死亡点                                             | ✅   |
| DeathLog      | 死亡记录查询，支持点击传送                             | ✅   |
| MOTD          | 动态 Motd 轮播                                         | ✅   |
| Maintenance   | 维护模式，禁止非管理员进入                             | 🚧 开发中   |
| Clean         | 实体/掉落物自动清理，TPS 检测，白名单                  | ✅   |
| Suicide       | 玩家自杀                                               | ✅   |
| Notice        | 自定义公告，游戏内在线编辑                             | ✅   |
| Crash         | 崩溃玩家客户端（管理员工具）                           | 🚧 开发中   |
| RedPacket     | 红包系统（随机金额/固定金额），支持离线缓存            | ✅   |
| Servers       | 跨服传送菜单                                           | ✅   |
| PVP           | 个人 PVP 开关                                          | ✅   |
| Sign          | 每日签到，连续签到奖励                                 | ✅   |
| KeepInventory | 开服自动开启死亡不掉落                                 | ✅   |
| i18n          | 多语言国际化（zh_CN / en_US）                          | ✅   |
| UpdateChecker | 启动时检查插件更新                                     | ✅   |

---

## 📦 示例指令

以下是部分常用指令示例（视插件版本可能会有所变动）：

```txt
/cd 菜单
/cd {set} 菜单{配置}
/home	 #家系统菜单(设置、传送到家)
/tpa	 #玩家互传系统(发送传送请求)
/tpayes	 #同意传送请求
/tpano	 #拒绝传送请求
/tpasettings	 #拒绝或者同意所有传送请求
/rtp	 #随机传送(在不同维度安全随机传送)
/pvp	 #开关个人PVP功能
/warp	 #公共传送点菜单
/servers	 #跨服传送菜单
/back	 #死亡点传送(返回死亡位置)
/deathlog	 #查询以往的死亡记录
/moneygui	 #打开GUI经济系统
/moneys add & del & set get 玩家（非get时加上“金额”）	 #经济操作 ：添加/减少/增加玩家的金额
/notice	 #查看公告
/noticeset	 #更改公告
/wh	 #打开或关闭维护状态
/clean {air} status & cancel & tps &toast &help	 #清理掉落物 & 清理状态 & 取消清理 & 查询tps & 关闭顶部弹出通知 & 帮助
/suicide	 #自杀
/fcam	 #开关灵魂出窍功能
/rtpreset	 #重置冷却时间（Only 管理员）
/hub	 #一键回到指定地点（所有人可用）
/sethub	 #设置/hub传送的地点
/crash	 #打开崩溃玩家客户端菜单
/redpacket history && list && open && send	 #红包功能（长指令版）
/rp history && list && open && send	 #红包功能（短指令版）
/redpackethelp	 #红包功能详解（GUI界面）
/yest	 #主命令，/yest reload 重载插件
/menu	 #打开主菜单（同 /cd）
/getclock	 #领取钟表（每人限领一次）
/sign	 #每日签到
/signset	 #签到管理（管理员）
```

---

## 贡献

本项目的诞生离不开PHEyeji等人的帮助与支持！<br>
如果您也想为YEssential做贡献欢迎提交 Issue，共同完善 YEssential。 
