import requests
import os

# 从环境变量中获取账号和密码
email, password = os.getenv('IKUUU', '').split(';') if ';' in os.getenv('IKUUU', '') else ('', '')
telegram_chat_id = os.environ.get("TG_CHAT_ID", "")
telegram_bot_token = os.environ.get("TG_BOT_TOKEN", "")

header = {
    'origin': 'https://ikuuu.one',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
}

def main():
    login_url = 'https://ikuuu.one/auth/login'
    check_url = 'https://ikuuu.one/user/checkin'
    try:
        with requests.Session() as session:
            print(f'[{email}] 正在登录...')
            login_resp = session.post(login_url, headers=header, data={'email': email, 'passwd': password}).json()
            print(login_resp.get('msg', '登录无响应'))
            
            print(f'[{email}] 正在签到...')
            checkin_resp = session.post(check_url, headers=header).json()
            message = checkin_resp.get('msg', '签到无响应')
            print(message)
            telegram_notify(f"[{email}] 签到结果: {message}")
    except Exception as e:
        error_message = f"[{email}] 签到失败: {str(e)}"
        print(error_message)
        telegram_notify(error_message)
        
# Telegram 推送通知
def telegram_notify(title, content=""):
    if not telegram_bot_token or not telegram_chat_id:
        print("未配置 Telegram 推送所需的环境变量")
        return
    
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    message = f"{title}\n\n{content}"
    payload = {"chat_id": telegram_chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Telegram 推送失败：{e}")
        
if __name__ == "__main__":
    main()
