import requests
import os
from bs4 import BeautifulSoup

# 获取 Cookie 环境变量
cookie = os.environ.get("cookie_eatASMR")

# 请求头模板
headers = {
    "cookie": cookie,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36 Edg/80.0.361.69",
    "referer": "https://eatasmr.com"
}

# 获取签到页的 formhash 并执行签到
def sign_in():
    # 第一步：获取签到页
    url = 'https://eatasmr.com/tasks/attendance'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # 使用 BeautifulSoup 解析页面
        soup = BeautifulSoup(response.text, 'html.parser')
        # 尝试找到 formhash （通常是一个类似于 URL 参数的值）
        formhash_tag = soup.find('a', href=True, string='签到')  # 根据签到按钮文本进行匹配
        if formhash_tag:
            formhash = formhash_tag['href'].split('=')[-1]  # 提取 __v 参数
            print(f"获取到 formhash: {formhash}")
            # 第二步：进行签到请求
            check_in(formhash)
        else:
            print("未找到 formhash，签到失败。")
    else:
        print(f"获取签到页失败，状态码: {response.status_code}")

# 执行签到请求
def check_in(formhash):
    url = f"https://eatasmr.com/tasks/attendance?a=check&__v={formhash}"
    data = {"check": "簽到"}

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        print("签到成功！")
    else:
        print(f"签到失败，状态码: {response.status_code}")

# 主程序
if __name__ == '__main__':
    if cookie:
        print("----------eatASMR开始尝试签到----------")
        sign_in()
        print("----------eatASMR签到执行完毕----------")
    else:
        print("未设置 cookie_eatASMR 环境变量，无法进行签到。")
