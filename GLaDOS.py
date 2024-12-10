import requests
import json
import os

# 获取环境变量
cookies = [cookie.strip() for cookie in os.environ.get("GLADOS_COOKIE", "").split("&") if cookie.strip()]
telegram_chat_id = os.environ.get("TG_CHAT_ID", "")
telegram_bot_token = os.environ.get("TG_BOT_TOKEN", "")

if not cookies:
    print("未获取到有效的 COOKIE")
    exit(0)

# 请求头
HEADERS = {
    'referer': 'https://glados.one/console/checkin',
    'origin': 'https://glados.one',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    'content-type': 'application/json;charset=UTF-8'
}

# 签到 API 和状态 API
CHECKIN_URL = "https://glados.one/api/user/checkin"
STATUS_URL = "https://glados.one/api/user/status"

# 签到和状态获取逻辑
def check_in(cookie):
    try:
        # 签到
        response = requests.post(CHECKIN_URL, headers={**HEADERS, 'cookie': cookie}, data=json.dumps({'token': 'glados.one'}))
        response.raise_for_status()
        checkin_data = response.json()
        
        # 获取状态
        status_response = requests.get(STATUS_URL, headers={**HEADERS, 'cookie': cookie})
        status_response.raise_for_status()
        status_data = status_response.json()
        
        return checkin_data, status_data
    except requests.RequestException as e:
        print(f"请求失败：{e}")
        return None, None

# 主流程
def start():
    global sendContent
    sendContent = ""
    
    for cookie in cookies:
        checkin_data, status_data = check_in(cookie)
        if not checkin_data or not status_data:
            continue
        
        # 提取数据
        email = status_data['data'].get('email', '未知邮箱')
        left_days = str(status_data['data'].get('leftDays', '0')).split('.')[0]
        message = checkin_data.get('message', '未知消息')
        
        log = f"账号: {email}\n签到结果: {message}\n剩余天数: {left_days} 天\n"
        print(log)
        sendContent += log + "\n"

        # 如果 cookie 失效，推送通知
        if message.lower() == 'invalid token':
            telegram_notify(f"{email} 更新 cookie")
    
    # 全部完成后推送通知
    if sendContent:
        telegram_notify("VPN 签到成功", sendContent)

# Telegram 推送通知
def telegram_notify(title, content=""):
    if not telegram_bot_token or not telegram_chat_id:
        print("未配置 Telegram 推送所需的环境变量")
        return
    
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    message = f"{title}\n\n{content}".replace('_', '\\_')  # 防止 Markdown 解析问题
    payload = {"chat_id": telegram_chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Telegram 推送成功")
    except requests.RequestException as e:
        print(f"Telegram 推送失败：{e}")

# 云函数入口
def main_handler(event, context):
    return start()

if __name__ == '__main__':
    start()
