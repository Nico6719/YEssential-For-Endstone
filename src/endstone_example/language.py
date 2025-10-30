import json
import os
from typing import Dict

class LanguageManager:
    def __init__(self, plugin):
        self.plugin = plugin
        self.languages = {}
        self.current_lang = "zh_cn"
        
        # 默认中文语言文件
        self.default_language = {
            "plugin.name": "YEssential",
            "plugin.version": "2.5.4",
            "plugin.author": "Nico6719, PHEyeji",
            
            # 通用消息
            "player.only": "§c只有玩家可以执行此命令！",
            "player.not.op": "§c权限不足！",
            "module.no.enabled": "§c所选模块（功能）未开启！",
            "success": "§a成功",
            "failed": "§c失败",
            "gui.exit": "§7表单已关闭，未收到操作",
            "no.permission": "§c你没有权限使用此命令！",
            
            # 经济系统
            "economy.balance": "§a您的余额: {balance} {currency}",
            "economy.transfer.success": "§a转账成功！实际到账: {amount}，手续费: {tax}",
            "economy.transfer.received": "§a收到来自 {player} 的转账: {amount}",
            "economy.transfer.failed": "§c转账失败，余额不足！",
            "economy.no.enough": "§c您的余额不足！",
            "economy.ranking.title": "§l§6财富排行榜",
            "economy.ranking.empty": "§c暂无排行榜数据！",
            
            # 家园系统
            "home.set.success": "§a成功设置家: {name}",
            "home.set.failed": "§c设置家失败！",
            "home.set.max": "§c家的数量已达到上限 {max}！",
            "home.set.exists": "§c家名称已存在！",
            "home.del.success": "§a成功删除家: {name}",
            "home.del.failed": "§c删除家失败！",
            "home.tp.success": "§a成功传送回家: {name}",
            "home.tp.failed": "§c传送回家失败！",
            "home.list.empty": "§c您还没有设置任何家！",
            "home.list.title": "§a您的家列表:",
            
            # 随机传送
            "rtp.searching": "§a正在寻找安全的传送位置...",
            "rtp.success": "§a随机传送成功！",
            "rtp.failed": "§c无法找到安全的传送位置，请稍后重试！",
            "rtp.cooldown": "§c传送冷却中，剩余时间: {time}秒",
            "rtp.cost": "§c需要 {cost} 金币才能随机传送！",
            "rtp.range": "§7传送范围: §f{min} - {max} 格",
            
            # 死亡回溯
            "back.recorded": "§a已记录您的死亡点！使用 /back 查看所有死亡点",
            "back.empty": "§c您没有死亡历史记录！",
            "back.success": "§a成功传送到死亡点！",
            "back.failed": "§c传送失败！",
            "back.cost": "§c需要 {cost} 金币才能回溯！",
            
            # 公告系统
            "notice.title": "§l§e服务器公告",
            "notice.empty": "§c暂无公告",
            "notice.dont.show": "§e以后进服不自动弹出(除非公告更新或停用此开关)",
            
            # PVP系统
            "pvp.enabled": "§6PVP 已开启",
            "pvp.disabled": "§6PVP 已关闭",
            "pvp.self.disabled": "§l§b你关闭了 PVP",
            "pvp.other.disabled": "§l§b对方关闭了 PVP",
            
            # 传送请求
            "tpa.request.sent": "§a已向 {player} 发送传送请求",
            "tpa.request.received": "§e收到传送请求({player}想{action})\n§a/tpayes同意 §c/tpano拒绝",
            "tpa.accepted": "§a已同意传送请求",
            "tpa.denied": "§c已拒绝传送请求",
            "tpa.timeout": "§c传送请求已超时",
            "tpa.no.requests": "§c没有待处理的传送请求",
            
            # 红包系统
            "redpacket.send.success": "§a成功发送红包！",
            "redpacket.send.failed": "§c发送红包失败！",
            "redpacket.open.success": "§a恭喜你领取到 {amount} 金币！",
            "redpacket.open.failed": "§c领取红包失败！",
            "redpacket.empty": "§c当前没有可领取的红包",
            "redpacket.expired": "§c红包已过期",
            
            # 维护模式
            "maintenance.enabled": "§c服务器正在维护中，请稍后再来！",
            
            # 欢迎消息
            "welcome.message": "§a欢迎 {player} 加入服务器！"
        }
    
    def load_language(self):
        """加载语言文件"""
        lang_code = self.plugin.config_manager.get("Language", "zh_cn")
        lang_path = os.path.join(self.plugin.data_folder, "lang", f"{lang_code}.json")
        
        try:
            if os.path.exists(lang_path):
                with open(lang_path, 'r', encoding='utf-8') as f:
                    self.languages = json.load(f)
            else:
                self.languages = self.default_language.copy()
                self.save_language()
            
            # 合并新键值
            merged = False
            for key, value in self.default_language.items():
                if key not in self.languages:
                    self.languages[key] = value
                    merged = True
            
            if merged:
                self.save_language()
            
            self.plugin.logger.info(f"语言文件加载完成: {lang_code}")
            
        except Exception as e:
            self.plugin.logger.error(f"加载语言文件失败: {e}")
            self.languages = self.default_language.copy()
    
    def save_language(self):
        """保存语言文件"""
        lang_code = self.plugin.config_manager.get("Language", "zh_cn")
        lang_path = os.path.join(self.plugin.data_folder, "lang", f"{lang_code}.json")
        
        try:
            os.makedirs(os.path.dirname(lang_path), exist_ok=True)
            with open(lang_path, 'w', encoding='utf-8') as f:
                json.dump(self.languages, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            self.plugin.logger.error(f"保存语言文件失败: {e}")
    
    def get_text(self, key: str) -> str:
        """获取文本"""
        return self.languages.get(key, key)
