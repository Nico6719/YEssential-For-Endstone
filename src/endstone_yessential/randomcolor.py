import random

# --- 随机颜色系统 ---
GLOBAL_C1 = None
GLOBAL_C2 = None

def randomVividColor():
    """生成一个鲜艳的随机颜色"""
    rand = random.random() * 260
    if rand < 90:
        h = rand
    elif rand < 200:
        h = rand + 60
    else:
        h = rand + 100
    s = 0.90 + random.random() * 0.10
    l = 0.65 + random.random() * 0.15
    a = s * min(l, 1 - l)
    def f(n):
        k = (n + h / 30) % 12
        return round((l - a * max(-1, min(k - 3, 9 - k, 1))) * 255)
    return [f(0), f(8), f(4)]

def generateColorPair():
    """生成一对颜色"""
    c1 = randomVividColor()
    c2, attempts = 0, 0
    while True:
        c2 = randomVividColor()
        diff = abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) + abs(c1[2] - c2[2])
        if diff > 150 or attempts > 20:
            break
        attempts += 1
    return [c1, c2]

GLOBAL_C1, GLOBAL_C2 = generateColorPair()

def globalLerpColor(t):
    """在全局颜色对之间进行线性插值"""
    return [
        round(GLOBAL_C1[0] + (GLOBAL_C2[0] - GLOBAL_C1[0]) * t),
        round(GLOBAL_C1[1] + (GLOBAL_C2[1] - GLOBAL_C1[1]) * t),
        round(GLOBAL_C1[2] + (GLOBAL_C2[2] - GLOBAL_C1[2]) * t)
    ]

def randomGradientColor(text):
    """生成随机渐变色文本"""
    lenth = len(text)
    out = ''
    for i in range(lenth):
        t = 0 if lenth <= 1 else i / (lenth - 1)
        r, g, b = globalLerpColor(t)
        out += f"\x1b[38;2;{r};{g};{b}m{text[i]}"
    return out + "\x1b[0m"

class RandomColor:
    """随机颜色类，用于生成随机渐变色文本"""
    def __init__(self, text):
        self.text = text
    def __str__(self):
        return randomGradientColor(self.text)