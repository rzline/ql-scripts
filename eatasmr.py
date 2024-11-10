import requests
import re
import os
import time

BASE_URL = 'https://eatasmr.com'
COOKIE = os.getenv("eatASMR")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br"
}

def get_login_url():
    """获取签到 URL 并尝试签到"""
    url = f'{BASE_URL}/tasks/attendance'
    headers = HEADERS.copy()
    headers["Cookie"] = COOKIE
    headers["Referer"] = BASE_URL

    for _ in range(3):  # 重试3次
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            login_urls = re.findall(r"(/tasks/attendance\?a=check&__v=..........)", response.text)
            if login_urls:
                print("找到签到 URL:", login_urls)
                for login_url in login_urls:
                    login(login_url)
            else:
                print("未找到签到 URL，请检查页面内容。")
            break  # 成功后跳出重试循环
        except requests.exceptions.Timeout:
            print("请求超时，重试中...")
            time.sleep(2)
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}, 重试中...")
            time.sleep(2)

def login(path):
    """根据提供的路径发送签到请求"""
    url = f"{BASE_URL}{path}"
    headers = HEADERS.copy()
    headers["Cookie"] = COOKIE
    headers["Referer"] = f"{BASE_URL}/tasks/attendance"

    try:
        response = requests.post(url, json={"check": "簽到"}, headers=headers, timeout=10)
        response.raise_for_status()
        print("签到成功，响应:", response.text)
    except requests.exceptions.Timeout:
        print("签到请求超时，未能成功签到。")
    except requests.exceptions.RequestException as e:
        print(f"签到请求错误: {e}")

if __name__ == '__main__':
    if COOKIE:
        print("----------eatASMR 开始尝试签到----------")
        get_login_url()
        print("----------eatASMR 签到执行完毕----------")
    else:
        print("未找到 cookie，请设置 'cookie_eatASMR' 环境变量。")
