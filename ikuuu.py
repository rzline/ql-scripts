import requests
import os

# 从环境变量中获取账号和密码
email, password = os.getenv('IKUUU', '').split(';') if ';' in os.getenv('IKUUU', '') else ('', '')

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
            send_message_to_telegram(f"[{email}] 签到结果: {message}")
    except Exception as e:
        error_message = f"[{email}] 签到失败: {str(e)}"
        print(error_message)
        send_message_to_telegram(error_message)

if __name__ == "__main__":
    main()
