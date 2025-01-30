import requests
import os
import time
import xml.etree.ElementTree as ET
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 环境变量配置检查：检查是否存在必要的环境变量，缺失则抛出异常
required_env_vars = ['SOUTHPLUSCOOKIE', 'TG_CHAT_ID', 'TG_BOT_TOKEN']
missing = [var for var in required_env_vars if not os.getenv(var)]
if missing:
    raise EnvironmentError(f"缺少必需的环境变量: {', '.join(missing)}")

# 初始化日志模块，设置日志输出格式和日志级别
logging.basicConfig(
    level=logging.INFO,  # 日志级别，INFO 表示记录信息级别的日志
    format='%(asctime)s - %(levelname)s: %(message)s',  # 日志输出的格式
    datefmt='%Y-%m-%d %H:%M:%S'  # 日期格式
)

# 全局常量配置
BASE_URL = 'https://snow-plus.net/plugin.php'  # 请求的基础 URL
H_NAME = 'tasks'  # 固定的请求参数 H_name
TASKS = [
    # 任务列表，包含不同的 action 和 cid，分别对应不同的任务类型
    {'action': 'job', 'cid': '15', 'task_type': '日常申请'},
    {'action': 'job2', 'cid': '15', 'task_type': '日常完成'},
    {'action': 'job', 'cid': '14', 'task_type': '周常申请'},
    {'action': 'job2', 'cid': '14', 'task_type': '周常完成'},
]

# 配置 requests 会话，支持重试机制
session = requests.Session()  # 创建请求会话
retries = Retry(
    total=3,  # 重试总次数
    backoff_factor=1,  # 重试时的间隔因子
    status_forcelist=[500, 502, 503, 504]  # 遇到这些 HTTP 错误时才会重试
)
session.mount('https://', HTTPAdapter(max_retries=retries))  # 为 session 添加重试适配器

# Telegram 配置，用于推送消息
TELEGRAM_CHAT_ID = 'TG_CHAT_ID'  # 从环境变量中获取 Telegram 聊天 ID
TELEGRAM_BOT_TOKEN = 'TG_BOT_TOKEN'  # 从环境变量中获取 Telegram bot Token

# Cookie 缓存，用于优化请求性能
COOKIE_STR = None

# 从环境变量获取 cookies 字符串，并转换为字典形式
def get_cookies():
    cookie_value = os.getenv('SOUTHPLUSCOOKIE', '').strip().replace('\n', '')  # 获取 Cookie 字符串
    return dict(cookie.split('=', 1) for cookie in cookie_value.split('; ')) if cookie_value else {}

# 获取 Cookie 字符串，缓存化优化性能
def get_cookie_str():
    global COOKIE_STR
    if COOKIE_STR is None:
        cookies = get_cookies()  # 获取 cookies 字典
        COOKIE_STR = '; '.join(f'{k}={v}' for k, v in cookies.items())  # 转换为字符串形式
    return COOKIE_STR

# 构造请求头
def create_headers(referer=None):
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'cookie': get_cookie_str()  # 添加 Cookie 到请求头
    }
    if referer:  # 如果提供了 referer，则加入头部
        headers['referer'] = referer
    return headers

# 构造请求参数
def create_params(action, cid):
    return {
        'H_name': H_NAME,  # 固定的 H_name
        'action': 'ajax',  # action 类型，固定为 'ajax'
        'nowtime': str(int(time.time() * 1000)),  # 当前时间戳，精确到毫秒
        'actions': action,  # 任务的具体动作（如 'job' 或 'job2'）
        'cid': cid,  # 任务的 ID
    }

# 执行任务函数
def tasks(url, action, cid, task_type):
    try:
        # 构造 Referer 和请求头
        referer = f"{url}?H_name={H_NAME}&actions={action}"
        headers = create_headers(referer)
        params = create_params(action, cid)

        # 发送 GET 请求，带有请求参数和头部
        response = session.get(url, params=params, headers=headers, timeout=10)  # 设置超时时间为 10 秒
        response.raise_for_status()  # 如果响应码是 4xx 或 5xx，抛出异常
        response.encoding = 'utf-8'  # 设置响应的编码为 UTF-8

        # 增强 XML 解析的安全性
        try:
            root = ET.fromstring(response.text)  # 解析 XML 响应
        except ET.ParseError as e:
            logging.error(f"{task_type} XML解析失败: {e}")  # 解析失败时记录日志
            telegram_notify(f"{task_type}失败", "服务器返回无效的XML格式")  # 发送失败通知
            return

        # 从 XML 响应中提取有用的信息
        values = root.text.split('\t')  # 假设返回的 XML 格式是通过 tab 分隔的
        message = values[1] if len(values) > 1 else "无返回内容"  # 如果有第二个值，则取其内容

        # 记录日志并发送 Telegram 通知
        logging.info(f"{task_type}: {message}")
        telegram_notify(f"{task_type}结果", message)

    except Exception as e:
        # 处理请求失败时的异常
        logging.error(f"{task_type}请求失败: {str(e)}")
        telegram_notify(f"{task_type}失败", str(e))  # 发送失败通知

# 通过 Telegram 发送通知
def telegram_notify(title, content=""):
    message = f"*{title}*\n\n{content}"  # 格式化通知内容
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"  # Telegram API URL
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,  # Telegram 聊天 ID
        "text": message,  # 消息内容
        "parse_mode": "Markdown"  # 设置 Markdown 格式
    }

    try:
        response = session.post(url, json=payload, timeout=10)  # 发送 POST 请求
        response.raise_for_status()  # 如果请求失败，抛出异常
    except Exception as e:
        logging.error(f"Telegram推送失败: {str(e)}")  # 记录 Telegram 推送失败的错误

# 主程序：遍历任务列表并执行任务
if __name__ == "__main__":
    for task in TASKS:  # 遍历每个任务
        tasks(BASE_URL, **task)  # 执行任务，解包字典传递参数
