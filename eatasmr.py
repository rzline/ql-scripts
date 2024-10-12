import requests  # 导入请求库，用于发送 HTTP 请求
import re  # 导入正则表达式库，用于字符串处理
import os  # 导入 OS 库，用于处理环境变量

# 基本 URL
BASE_URL = 'https://eatasmr.com'
# 从环境变量获取 cookie
COOKIE = os.environ.get("cookie_eatASMR")

def get_login_url():
    """获取登录 URL 并尝试签到"""
    url = f'{BASE_URL}/tasks/attendance'
    headers = {
        "Cookie": COOKIE,  # 添加 cookie 以保持登录状态
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "Referer": BASE_URL  # 设置 referer
    }
    
    try:
        # 发送 GET 请求获取页面内容
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        # 使用正则表达式查找登录 URL
        login_urls = re.findall(r"(/tasks/attendance\?a=check&__v=..........)", response.text)
        print("找到登录 URL:", login_urls)
        # 遍历每个找到的登录 URL 并尝试登录
        for login_url in login_urls:
            login(login_url)
    except requests.RequestException as e:
        print(f"请求错误: {e}")

def login(path):
    """根据提供的路径发送签到请求"""
    url = f"{BASE_URL}{path}"  # 完整的登录 URL
    print("登录到 URL:", url)
    
    headers = {
        "Cookie": COOKIE,  # 添加 cookie 以保持登录状态
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "Referer": f"{BASE_URL}/tasks/attendance"  # 设置 referer
    }
    
    data = {
        "check": "簽到"  # 要发送的签到数据
    }
    
    try:
        # 发送 POST 请求进行签到
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        print("签到成功，响应:", response.text)  # 打印响应内容以确认签到成功
    except requests.RequestException as e:
        print(f"签到请求错误: {e}")

# 主执行点
if __name__ == '__main__':
    if COOKIE:
        print("----------eatASMR 开始尝试签到----------")
        get_login_url()  # 获取登录 URL 并尝试签到
        print("----------eatASMR 签到执行完毕----------")
    else:
        print("未找到 cookie，请设置 'cookie_eatASMR' 环境变量。")  # 提示用户设置 cookie
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
