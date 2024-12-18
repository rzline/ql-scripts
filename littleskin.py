import os
import requests
import time
from bs4 import BeautifulSoup

# 获取账号和密码
account = os.getenv('SKINACCOUNT')
password = os.getenv('SKINPASSWD')
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')


# 目标网站地址
endpoint = 'https://littleskin.cn/'

# 设置请求头
headers = {
    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.7,zh-TW;q=0.5,zh-HK;q=0.3,en;q=0.2",
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
}

# 初始化 session
session = requests.Session()
session.headers.update(headers)

# 执行任务
def task():
    # 获取 CSRF token
    home_page = session.get(endpoint + 'auth/login')
    csrf_token = BeautifulSoup(home_page.text, 'html.parser').find('meta', {'name': 'csrf-token'})['content']

    # 登录请求
    login_data = {'identification': account, 'keep': False, 'password': password}
    session.post(endpoint + 'auth/login', data=login_data, headers={'X-CSRF-TOKEN': csrf_token})

    # 获取用户页面，提取新的 CSRF token
    user_page = session.get(endpoint + 'user')
    csrf_token = BeautifulSoup(user_page.text, 'html.parser').find('meta', {'name': 'csrf-token'})['content']

    # 签到请求
    sign_response = session.post(endpoint + 'user/sign', headers={'X-CSRF-TOKEN': csrf_token})

    # 提取中文部分
    response_json = sign_response.json()
    message = response_json.get("message", "")
    
    # 打印并发送通知
    print(sign_response.text)
    telegram_notify("签到成功", sign_response.text)

# 主函数
def main():
    try:
        task()
    except Exception as e:
        telegram_notify("任务失败", f"错误信息：{str(e)}")

# 发送 Telegram 通知
def telegram_notify(title, content=""):
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        print("未配置 Telegram 推送所需的环境变量")
        return
        
    content = content.encode('utf-8').decode('unicode_escape')
    
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": f"{title}\n\n{content}", "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Telegram 推送失败：{e}")

if __name__ == '__main__':
    main()
