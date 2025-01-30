import requests
import os

# 设置目标网站 URL 和 Cookie
base_url = 'https://eatasmr.com'
cookie = os.environ.get("cookie_eatASMR")

# 发送 GET 请求获取签到页面（如果需要）
def get_attendance_page():
    url = f'{base_url}/tasks/attendance'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'Cookie': cookie,
    }
    res = requests.get(url, headers=headers)
    return res

# 直接发送签到请求
def sign_in():
    url = f'{base_url}/tasks/attendance?a=check'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'Cookie': cookie,
        'Referer': f'{base_url}/tasks/attendance'
    }
    data = {'check': '签到'}  # 根据实际签到按钮的值设置
    res = requests.post(url, headers=headers, data=data)
    if res.status_code == 200:
        print("签到成功！")
    else:
        print("签到失败！")

if __name__ == '__main__':
    if cookie:
        print("开始尝试签到...")
        get_attendance_page()  # 获取签到页面
        sign_in()  # 提交签到请求
        print("签到执行完毕。")
    else:
        print("未找到有效的 Cookie，无法签到。")
