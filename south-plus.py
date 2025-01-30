import requests
import os
import time
import xml.etree.ElementTree as ET
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 环境变量配置检查
required_env_vars = ['SOUTHPLUSCOOKIE', 'TG_CHAT_ID', 'TG_BOT_TOKEN']
missing = [var for var in required_env_vars if not os.getenv(var)]
if missing:
    raise EnvironmentError(f"缺少必需的环境变量: {', '.join(missing)}")

# 初始化日志模块
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 全局常量
BASE_URL = 'https://snow-plus.net/plugin.php'
H_NAME = 'tasks'
TASKS = [
    {'action': 'job', 'cid': '15', 'task_type': '日常申请'},
    {'action': 'job2', 'cid': '15', 'task_type': '日常完成'},
    {'action': 'job', 'cid': '14', 'task_type': '周常申请'},
    {'action': 'job2', 'cid': '14', 'task_type': '周常完成'},
]

# 请求会话配置（含重试逻辑）
session = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
)
session.mount('https://', HTTPAdapter(max_retries=retries))

# Telegram配置
TELEGRAM_CHAT_ID = os.environ["TG_CHAT_ID"]
TELEGRAM_BOT_TOKEN = os.environ["TG_BOT_TOKEN"]

# Cookie缓存优化
COOKIE_STR = None
def get_cookies():
    cookie_value = os.getenv('SOUTHPLUSCOOKIE', '').strip().replace('\n', '')
    return dict(cookie.split('=', 1) for cookie in cookie_value.split('; ')) if cookie_value else {}

def get_cookie_str():
    global COOKIE_STR
    if COOKIE_STR is None:
        cookies = get_cookies()
        COOKIE_STR = '; '.join(f'{k}={v}' for k, v in cookies.items())
    return COOKIE_STR

def create_headers(referer=None):
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'cookie': get_cookie_str()
    }
    if referer:
        headers['referer'] = referer
    return headers

def create_params(action, cid):
    return {
        'H_name': H_NAME,
        'action': 'ajax',
        'nowtime': str(int(time.time() * 1000)),
        'actions': action,
        'cid': cid,
    }

def tasks(url, action, cid, task_type):
    try:
        # 修正Referer构造
        referer = f"{url}?H_name={H_NAME}&actions={action}"
        headers = create_headers(referer)
        params = create_params(action, cid)

        # 发送请求（含超时和重试）
        response = session.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'

        # 增强XML解析安全性
        try:
            root = ET.fromstring(response.text)
        except ET.ParseError as e:
            logging.error(f"{task_type} XML解析失败: {e}")
            telegram_notify(f"{task_type}失败", "服务器返回无效的XML格式")
            return

        values = root.text.split('\t')
        message = values[1] if len(values) > 1 else "无返回内容"
        
        logging.info(f"{task_type}: {message}")
        telegram_notify(f"{task_type}结果", message)

    except Exception as e:
        logging.error(f"{task_type}请求失败: {str(e)}")
        telegram_notify(f"{task_type}失败", str(e))

def telegram_notify(title, content=""):
    message = f"*{title}*\n\n{content}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = session.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except Exception as e:
        logging.error(f"Telegram推送失败: {str(e)}")

if __name__ == "__main__":
    for task in TASKS:
        tasks(BASE_URL, **task)
