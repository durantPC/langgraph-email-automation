"""
邮件紧急程度识别器
基于关键词匹配和规则引擎分析邮件的紧急程度
"""
import re
from typing import Tuple, List
from ..state import EmailUrgencyLevel


class EmailUrgencyDetector:
    """
    邮件紧急程度识别器
    
    通过分析邮件主题和正文中的关键词，
    自动识别邮件的紧急程度等级。
    """
    
    # 紧急程度关键词配置
    URGENCY_KEYWORDS = {
        # 最高紧急 - 立即响应
        EmailUrgencyLevel.URGENT: [
            # 英文关键词
            r'urgent', r'asap', r'immediately', r'emergency', r'critical',
            r'crisis', r'outage', r'down', r'not working', r'broken',
            r'fail', r'failure', r'error', r'panic', r'help',
            # 中文关键词
            r'紧急', r'立即', r'马上', r'立刻', r'十万火急',
            r'急件', r'急事', r'催促', r'尽快', r'非常重要',
            r'系统宕机', r'服务中断', r'无法访问', r'出问题了',
            r'非常着急', r'现在就 需要', r'尽快处理', r'刻不容缓',
            r'生死攸关', r'迫在眉睫', r'火烧眉毛'
        ],
        
        # 高紧急 - 快速响应
        EmailUrgencyLevel.HIGH: [
            # 英文关键词
            r'important', r'priority', r'as soon as possible',
            r'need response', r'waiting for', r'follow up',
            r'time sensitive', r'deadline', r'due today',
            # 中文关键词
            r'重要', r'重要事项', r'重要通知', r'重要客户',
            r'尽快', r'尽快处理', r'尽快回复', r'尽快完成',
            r'重要提醒', r'重要提醒', r'请尽快', r'麻烦尽快',
            r'催促', r'提醒', r'注意事项', r'需要尽快',
            r'请马上', r'请立即', r'请立刻', r'麻烦您',
            r'尽快安排', r'尽快处理', r'尽快解决'
        ],
        
        # 中等紧急 - 当天响应
        EmailUrgencyLevel.MEDIUM: [
            # 英文关键词
            r'request', r'please', r'would you', r'could you',
            r'when possible', r'at your convenience', r'no rush',
            # 中文关键词
            r'请', r'请问', r'希望', r'期望', r'建议',
            r'能否', r'是否可以', r'方便的话', r'谢谢配合',
            r'麻烦', r'感谢', r'请帮忙', r'请协助',
            r'希望您', r'请您', r'如有可能', r'如果方便'
        ]
    }
    
    # 降低紧急程度的词汇
    LOWER_URGENCY_WORDS = [
        r'不急', r'慢慢来', r'有空再说', r'随你', r'没关系',
        r'不必着急', r'不用急', r'慢慢处理', r'不着急',
        r'有时间再说', r'以后再说', r'延后处理', r'低优先级',
        r'no rush', r'take your time', r'whenever', r'not urgent'
    ]
    
    def __init__(self):
        """初始化紧急程度识别器"""
        # 编译所有正则表达式
        self._compile_patterns()
        
    def _compile_patterns(self):
        """编译所有正则表达式模式"""
        self.patterns = {}
        
        # 编译紧急程度关键词
        for level, keywords in self.URGENCY_KEYWORDS.items():
            self.patterns[level] = [
                re.compile(keyword, re.IGNORECASE) 
                for keyword in keywords
            ]
        
        # 编译降低紧急程度的词汇
        self.lower_patterns = [
            re.compile(word, re.IGNORECASE) 
            for word in self.LOWER_URGENCY_WORDS
        ]
        
    def analyze_urgency(self, subject: str, body: str) -> Tuple[str, List[str]]:
        """
        分析邮件的紧急程度
        
        @param subject: 邮件主题
        @param body: 邮件正文
        @return: (紧急程度等级, 匹配的关键词列表)
        """
        # 合并主题和正文进行分析
        text = f"{subject} {body}".lower()
        
        # 首先检查是否有降低紧急程度的词汇
        has_lower_words = any(
            pattern.search(text) 
            for pattern in self.lower_patterns
        )
        
        if has_lower_words:
            # 如果发现降低紧急程度的词汇，降低一个等级
            return EmailUrgencyLevel.LOW, []
        
        # 统计各等级的匹配数量
        matches = {
            EmailUrgencyLevel.URGENT: [],
            EmailUrgencyLevel.HIGH: [],
            EmailUrgencyLevel.MEDIUM: [],
            EmailUrgencyLevel.LOW: []
        }
        
        # 检查各等级的关键词
        for level, patterns in self.patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    # 提取匹配的关键词（去除正则的特殊字符）
                    keyword = pattern.pattern
                    if keyword.startswith('r\'') and keyword.endswith('\''):
                        keyword = keyword[2:-1]
                    elif keyword.startswith('r"') and keyword.endswith('"'):
                        keyword = keyword[2:-1]
                    matches[level].append(keyword)
        
        # 根据匹配结果确定紧急程度
        # 优先级：URGENT > HIGH > MEDIUM > LOW
        if matches[EmailUrgencyLevel.URGENT]:
            return EmailUrgencyLevel.URGENT, matches[EmailUrgencyLevel.URGENT]
        
        if matches[EmailUrgencyLevel.HIGH]:
            return EmailUrgencyLevel.HIGH, matches[EmailUrgencyLevel.HIGH]
        
        if matches[EmailUrgencyLevel.MEDIUM]:
            return EmailUrgencyLevel.MEDIUM, matches[EmailUrgencyLevel.MEDIUM]
        
        # 默认低紧急程度
        return EmailUrgencyLevel.LOW, []
    
    def get_urgency_score(self, subject: str, body: str) -> int:
        """
        获取紧急程度分数（0-100）
        
        @param subject: 邮件主题
        @param body: 邮件正文
        @return: 紧急程度分数
        """
        level, _ = self.analyze_urgency(subject, body)
        
        score_map = {
            EmailUrgencyLevel.LOW: 25,
            EmailUrgencyLevel.MEDIUM: 50,
            EmailUrgencyLevel.HIGH: 75,
            EmailUrgencyLevel.URGENT: 100
        }
        
        return score_map.get(level, 25)
    
    def get_urgency_display_name(self, level: str) -> str:
        """
        获取紧急程度的显示名称
        
        @param level: 紧急程度等级
        @return: 显示名称
        """
        display_names = {
            EmailUrgencyLevel.LOW: "🟢 低",
            EmailUrgencyLevel.MEDIUM: "🟡 中",
            EmailUrgencyLevel.HIGH: "🟠 高",
            EmailUrgencyLevel.URGENT: "🔴 紧急"
        }
        
        return display_names.get(level, "🟢 低")
    
    def get_urgency_color(self, level: str) -> str:
        """
        获取紧急程度的颜色代码
        
        @param level: 紧急程度等级
        @return: 颜色代码
        """
        colors = {
            EmailUrgencyLevel.LOW: "#4CAF50",      # 绿色
            EmailUrgencyLevel.MEDIUM: "#FFC107",   # 黄色
            EmailUrgencyLevel.HIGH: "#FF9800",     # 橙色
            EmailUrgencyLevel.URGENT: "#F44336"    # 红色
        }
        
        return colors.get(level, "#4CAF50")


# 创建全局实例
urgency_detector = EmailUrgencyDetector()


def analyze_email_urgency(subject: str, body: str) -> Tuple[str, List[str]]:
    """
    分析邮件紧急程度的便捷函数
    
    @param subject: 邮件主题
    @param body: 邮件正文
    @return: (紧急程度等级, 匹配的关键词列表)
    """
    return urgency_detector.analyze_urgency(subject, body)


def get_urgency_info(subject: str, body: str) -> dict:
    """
    获取邮件紧急程度完整信息
    
    @param subject: 邮件主题
    @param body: 邮件正文
    @return: 包含等级、分数、显示名称、颜色的字典
    """
    level, keywords = urgency_detector.analyze_urgency(subject, body)
    
    return {
        "level": level,
        "score": urgency_detector.get_urgency_score(subject, body),
        "display_name": urgency_detector.get_urgency_display_name(level),
        "color": urgency_detector.get_urgency_color(level),
        "keywords": keywords
    }