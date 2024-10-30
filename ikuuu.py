import requests
import json
import os

# 创建一个请求会话
session = requests.session()

# 从环境变量获取电子邮件和密码
emails = os.environ.get('IKUUUEMAIL', '').split(',')
passwords = os.environ.get('IKUUUPASSWD', '').split(',')

# URL 定义
login_url = 'https://ikuuu.pw/auth/login'
check_url = 'https://ikuuu.pw/user/checkin'

# 请求头定义
header = {
    'origin': 'https://ikuuu.pw',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
}

def send_message_to_telegram(message):
    """发送消息到Telegram Bot"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if bot_token and chat_id:  # 仅在设置了环境变量时发送消息
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        payload = {
            'chat_id': chat_id,
            'text': message
        }
        requests.post(url, json=payload)

# 逐个处理电子邮件和密码
for email, passwd in zip(emails, passwords):
    session = requests.session()
    data = {
        'email': email,
        'passwd': passwd
    }
    try:
        print(f'[{email}] 进行登录...')
        response = json.loads(session.post(url=login_url, headers=header, data=data).text)
        
        # 仅打印提示消息而不打印敏感信息
        print(f'登录结果: {response["msg"]}')
        
        # 进行签到
        result = json.loads(session.post(url=check_url, headers=header).text)
        
        # 打印签到结果
        print(f'签到结果: {result["msg"]}')
        content = result['msg']
        
        # 发送签到结果到Telegram
        send_message_to_telegram(f"[{email}] 签到结果: {content}")
        
    except Exception as e:
        content = '签到失败'
        print(content)
        send_message_to_telegram(f"[{email}] 签到失败: {str(e)}")
