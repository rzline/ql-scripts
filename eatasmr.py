import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import re
import json
import os

base_url = 'https://eatasmr.com'
cookie = os.environ.get("cookie_eatASMR")

def getLoginUrl():
    url = 'https://eatasmr.com/tasks/attendance'
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "Referer": "https://eatasmr.com/",
        "Cookie": cookie  # 确保 cookie 作为单独的键
    }
    res = requests.get(url, headers=headers).text
    loginUrl = re.findall(r"(/tasks/attendance\?a=check&__v=..........)", res)
    print(loginUrl)
    for i in range(0, len(loginUrl)):
        login(loginUrl[i])

session = HTMLSession()
response = session.get('https://eatasmr.com/tasks/attendance')
response.html.render()  # 执行 JavaScript
print(response.html.html)

def login(path):
    url = f"https://eatasmr.com/tasks/attendance?a=check&__v={path.split('=')[-1]}"
    print(url)
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "Referer": "https://eatasmr.com/",
        "Cookie": cookie
    }
    data = {
        "check": "簽到"
    }
    res = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {res.status_code}")  # 打印状态码
    print(res.text)  # 打印返回内容

if __name__ == '__main__':
    if cookie:
        print("----------eatASMR开始尝试签到----------")
        getLoginUrl()
        print("----------eatASMR签到执行完毕----------")
