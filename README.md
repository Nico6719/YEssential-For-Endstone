<div align="center">

![YEssential](https://socialify.git.ci/Nico6719/YEssential/image?custom_language=JavaScript&description=1&font=Inter&forks=1&issues=1&language=1&logo=https://zh.minecraft.wiki/images/Bookshelf_JE4_BE2.png?21f85&name=1&owner=1&pattern=Plus&pulls=1&stargazers=1&theme=Auto)

> 来试试[NEssential](https://github.com/Nico6719/NEssential)？全新一代基础插件，以YEssential为基础重构的高性能，多功能的基础插件!

# 📦 YEssential

**基于 LSE 的多功能基础插件**

![](https://img.shields.io/github/v/release/Nico6719/YEssential?style=flat-square&logo=github&color=orange&label=Version)
![](https://img.shields.io/github/downloads/Nico6719/YEssential/total?style=flat-square&logo=github&color=33ccff&label=Downloads)
![](https://img.shields.io/github/languages/top/Nico6719/YEssential?style=flat-square&logo=javascript&color=yellow)

![](https://img.shields.io/github/stars/Nico6719/YEssential?style=flat-square&logo=github&color=yellow&label=Stars)
![](https://img.shields.io/github/last-commit/Nico6719/YEssential?style=flat-square&color=lightgrey)
![](https://komarev.com/ghpvc/?username=Nico6719-YEssential&color=green&style=flat-square&label=Views)

</div>

---

> 一个简洁、实用的基础插件，适用于基岩版服务器。基于 LegacyScriptEngine (LSE) 的插件，并且可以迁移 TMEssential 的部分数据（如 home 和 warp 的数据）以及 [PMenu](https://www.minebbs.com/resources/pmenu.4277/) 的菜单数据（100%兼容！）导入配置文件/数据教程在文末。<br>
> **如果您使用的是低于1.21.80的版本的服务端请使用（小于等于2.10.2）旧版本插件!**

## 📌 基本信息

- **名称**：YEssential
- **类型**：基础插件 / 多功能模块化插件
- **平台**：LegacyScriptEngine (LSE)
- **主要功能**：提供服务器基础功能（如：Home Tpr Tpa Warp Money 等）
- **支持迁移其他插件数据**：如 TMEssential 的 home 和 warp 数据可迁移到本插件等

---

### 📦 安装方法

- 方法1：使用lip安装，指令：lip install github.com/Nico6719/YEssential
- 方法2：下载本插件解压到Plugins目录内即可

---

## ⚙️ 插件亮点

### 功能

| 功能                | 描述                                                                               | 状态      |
| ------------------- | ---------------------------------------------------------------------------------- | --------- |
| Modules             | 多模块支持！                                                                       | ✅        |
| Economic            | 经济核心                                                                           | ✅        |
| 菜单                | 菜单功能，兼容[PMenu](https://www.minebbs.com/resources/pmenu.4277/)的配置文件！！ | ✅        |
| Hub                 | 一键回城，可通过指令设置传送点。                                                   | ✅        |
| Rtp                 | 随机传送，附带动画。                                                               | ✅        |
| Tpa                 | 传送系统，借鉴了子邪大佬写的 TeleportMaster。                                      | 🚧 开发中 |
| Home&Warp           | 家系统和公共传送点系统。                                                           | ✅        |
| Fcam                | 灵魂出窍（旁观者）。                                                               | 🚧 开发中 |
| Back&DeathLog       | 回死亡点以及记录玩家死亡点。                                                       | ✅        |
| DMotd               | 动态 Motd 功能。                                                                   | ✅        |
| WeiHu               | 维护服务器功能，禁止其他非管理成员进入服务器。                                     | 🚧 开发中 |
| Clean               | 自动清理掉落物和实体，掉落物过多时 & 定时自动清理，支持白名单。                    | 🚧 开发中 |
| Suicide             | 玩家紫砂（kill myself）。                                                          | ✅        |
| BetterStopMsg       | 自定义关服提示。                                                                   | ✅        |
| i18n Support        | 多语言支持。                                                                       | 🚧 开发中 |
| Notice              | 自定义公告，支持颜色符号，\n换行，支持游戏内在线编辑！                             | ✅        |
| FixExpLag           | 防止经验球卡服。                                                                   | 🚧 开发中 |
| Crash               | 崩溃玩家客户端（慎用！）。                                                         | 🚧 开发中 |
| RedPacket           | 玩家可以自行发红包。                                                               | 🚧 开发中 |
| ServersTP           | 一键传送到其他服务器。                                                             | ✅️        |
| PVP                 | 防止玩家恶意攻击。                                                                 | 🚧 开发中 |
| Keepinventory       | 开服自动开启死亡不掉落。                                                           | ✅️        |
| AutoUpdate          | 自动更新插件本体并重载。                                                           | 🚧 开发中 |
| Bstats统计          | 统计BDS信息和在线人数（可在Config内关闭）                                          | 🚧 开发中 |
| Gui修改插件配置     | 网页编辑器。                                                                       | 🚧 开发中 |
| Plugin for Endstone | Endstone 版本的 YEssential。                                                       | 🚧 开发中 |
| SideBar             | 支持自定义侧边栏以及支持 PAPI 变量。                                               | 📅 计划中 |

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
```

---

## 迁移其他插件的数据

- 迁移TMET基础插件配置文件教程：
  把 服务端目录\plugins\Timiya\data内的homelist.json和warplist.json
  移动到服务端目录\plugins\YEssential\data内并且分别重命名为homedata.json和warpdata.json然后保存即可

- 迁移PMenu菜单插件配置文件教程：
  把 服务端目录\plugins\Planet\PMENU\packs内的所有东西
  移动 到 服务端目录\plugins\YEssential\data\menus内即可

---

## 贡献

本项目的诞生离不开PHEyeji等人的帮助与支持！<br>
如果您也想为YEssential做贡献欢迎提交 Issue，共同完善 YEssential。 

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Nico6719/YEssential-For-Levilamina&type=Date)](https://star-history.com/#Nico6719/YEssential-For-Levilamina&Date)
