import os
import requests
from bs4 import BeautifulSoup
import time

# 获取账号和密码
account = os.getenv('SKINACCOUNT')
password = os.getenv('SKINPASSWORD')

# 目标网站地址
endpoint = 'https://littleskin.cn/'

# 初始化 session
session = requests.Session()

# 直接设置请求头
with open('headers.json', 'r', encoding='utf-8') as f:
    session.headers.update(json.load(f))

def task():
    # 登录页面获取 CSRF token
    home_page = session.get(endpoint + 'auth/login')
    csrf_token = BeautifulSoup(home_page.text, 'html.parser').find('meta', {'name': 'csrf-token'})['content']

    # 登录请求
    login_data = {'identification': account, 'keep': False, 'password': password}
    session.post(endpoint + 'auth/login', data=login_data, headers={'X-CSRF-TOKEN': csrf_token})

    # 获取用户页面，再次提取 CSRF token
    user_page = session.get(endpoint + 'user')
    csrf_token = BeautifulSoup(user_page.text, 'html.parser').find('meta', {'name': 'csrf-token'})['content']

    # 签到请求
    sign_response = session.post(endpoint + 'user/sign', headers={'X-CSRF-TOKEN': csrf_token})
    print(sign_response.text)

def main():
    max_retry = 3
    for i in range(max_retry):
        try:
            task()
            break
        except Exception as e:
            print(f"Attempt {i + 1} failed: {e}")
            if i < max_retry - 1:
                time.sleep(10)  # 等待 10 秒再重试
            else:
                raise

if __name__ == '__main__':
    main()
