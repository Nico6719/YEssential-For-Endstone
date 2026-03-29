import logging
from datetime import datetime
from pathlib import Path
from threading import Lock

from .randomcolor import RandomColor
from .constant import *

print_lock = Lock()  # 用于线程安全的日志输出

# TAG: 日志系统设置
log_dir = Path(f"./logs/{plugin_name}")
if not log_dir.exists():
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[{plugin_name}] 创建日志目录失败: {e}")

log_file = log_dir / f"{plugin_name_smallest}_{datetime.now().strftime('%Y%m%d')}.log"
logger = logging.getLogger(plugin_name)
logger.setLevel(logging.DEBUG)

try:
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
except Exception as e:
    print(f"[{plugin_name}] 配置日志文件处理器失败: {e}")

def plugin_print(text, level="INFO") -> bool:
    level_colors = {
        "DEBUG": "\x1b[36m", "INFO": "\x1b[37m", "WARNING": "\x1b[33m",
        "ERROR": "\x1b[31m", "SUCCESS": "\x1b[32m"
    }
    level_color = level_colors.get(level, "\x1b[37m")
    logger_head = f"[\x1b[96m{plugin_name}\x1b[0m] [{level_color}{level}\x1b[0m] "
    with print_lock:
        print(logger_head + str(RandomColor(text)))
    log_level_map = {
        "DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING,
        "ERROR": logging.ERROR, "SUCCESS": logging.INFO
    }
    log_level = log_level_map.get(level, logging.INFO)
    logger.log(log_level, str(text))
    return True