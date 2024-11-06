import requests
import os

# 从环境变量中获取账号和密码，使用分号分隔
credentials = os.getenv('IKUUU', '')
email, password = credentials.split(';') if ';' in credentials else ('', '')

# URL 定义
login_url = 'https://ikuuu.one/auth/login'
check_url = 'https://ikuuu.one/user/checkin'

# 请求头定义
header = {
    'origin': 'https://ikuuu.one',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
}

def send_message_to_telegram(message):
    """发送消息到 Telegram Bot"""
    bot_token, chat_id = os.getenv('TG_BOT_TOKEN'), os.getenv('TG_CHAT_ID')
    if bot_token and chat_id:
        requests.post(
            f'https://api.telegram.org/bot{bot_token}/sendMessage',
            json={'chat_id': chat_id, 'text': message}
        )

def main():
    data = {'email': email, 'passwd': password}
    try:
        with requests.Session() as session:
            # 登录
            print(f'[{email}] 正在登录...')
            login_resp = session.post(login_url, headers=header, data=data).json()
            print(login_resp.get('msg', '登录响应无消息'))
            
            # 签到
            checkin_resp = session.post(check_url, headers=header).json()
            content = checkin_resp.get('msg', '签到响应无消息')
            print(content)
            
            # 发送签到结果到 Telegram
            send_message_to_telegram(f"[{email}] 签到结果: {content}")
            
    except Exception as e:
        error_message = f"[{email}] 签到失败: {str(e)}"
        print(error_message)
        send_message_to_telegram(error_message)

if __name__ == "__main__":
    main()
