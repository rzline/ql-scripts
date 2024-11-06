import requests
import re
import os
import random

# 基本 URL
BASE_URL = 'https://eatasmr.com'
COOKIE = os.getenv("eatASMR")

def get_login_url():
    """获取签到 URL 并尝试签到"""
    url = f'{BASE_URL}/tasks/attendance'
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Content-Length": "24",  # 注意：这通常由requests自动处理
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": COOKIE,  # 使用有效的Cookie
        "Origin": "https://eatasmr.com",
        "Referer": "https://eatasmr.com/tasks/attendance",
        "Sec-Ch-Ua": '"Not-A.Brand";v="99", "Chromium";v="124"',
        "Sec-Ch-Ua-Mobile": "?1",
        "Sec-Ch-Ua-Platform": '"Android"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
    }
    
    try:
        # 发送 GET 请求获取页面内容
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        login_urls = re.findall(r"(/tasks/attendance\?a=check&__v=..........)", response.text)
        
        if login_urls:
            print("找到签到 URL:", login_urls)
            for login_url in login_urls:
                login(login_url)
        else:
            print("未找到签到 URL，请检查页面内容。")
            
    except requests.RequestException as e:
        print(f"请求错误: {e}")

def login(path):
    """根据提供的路径发送签到请求"""
    url = f"{BASE_URL}{path}"
    headers = {
        ":authority": "eatasmr.com",
        ":method": "POST",
        ":path": path,
        ":scheme": "https",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": COOKIE,
        "Origin": "https://eatasmr.com",
        "Referer": f"{BASE_URL}/tasks/attendance",
        "Sec-Ch-Ua": '"Not-A.Brand";v="99", "Chromium";v="124"',
        "Sec-Ch-Ua-Mobile": "?1",
        "Sec-Ch-Ua-Platform": '"Android"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
    }
    
    try:
        # 发送 POST 请求进行签到
        response = requests.post(url, data={"check": "簽到"}, headers=headers)
        response.raise_for_status()
        print("签到成功，响应:", response.text)
    except requests.RequestException as e:
        print(f"签到请求错误: {e}")

# 主执行点
if __name__ == '__main__':
    if COOKIE:
        print("----------eatASMR 开始尝试签到----------")
        get_login_url()
        print("----------eatASMR 签到执行完毕----------")
    else:
        print("未找到 cookie，请设置 'cookie_eatASMR' 环境变量。")
