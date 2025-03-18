import re
import time
import os
from bs4 import BeautifulSoup
import requests

bot_token = os.environ.get("TG_BOT_TOKEN")
chat_id = os.environ.get("TG_CHAT_ID")
cookie = os.environ.get("TSDM")

# 基础 headers (保持不变)
base_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}

# --- Telegram 推送函数 (修改为使用 requests) ---
def telegram_push(message, bot_token, chat_id):
    """发送 Telegram 推送消息 (使用 requests)"""
    if not bot_token or not chat_id:
        print("Telegram config missing, push skipped.")
        return False
    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = { # payload 可以直接使用字典
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(api_url, json=payload, timeout=10) # 使用 requests.post, 直接传递 json payload
        response.raise_for_status() #  requests 自带 raise_for_status 检查 HTTP 错误
        return response.json().get("ok", False) # requests 自带 json() 方法解析 JSON 响应
    except requests.exceptions.RequestException as e: # 捕获 requests 的通用异常
        print(f"Telegram push failed: {e}")
        return False

# 函数 (修改为使用 requests)
def get_formhash(cookie):
    """获取 formhash 值 (使用 requests)"""
    headers = base_headers.copy()
    headers['Cookie'] = cookie
    try:
        response = requests.get("https://www.tsdm39.com/forum.php", headers=headers, timeout=10) # 使用 requests.get
        response.raise_for_status() # 检查 HTTP 错误
        match = re.search(r'formhash=(.+?)"', response.text) # requests response 对象可以直接 .text 访问响应内容
        return match.group(1) if match else None
    except requests.exceptions.RequestException: # 捕获 requests 异常
        print("Formhash error")
        return None

def tsdm_check_in(cookie):
    """天使动漫论坛签到 (使用 requests)"""
    formhash_value = get_formhash(cookie)
    if not formhash_value:
        print("Check-in failed: formhash")
        return

    payload = { # payload 可以直接使用字典
        "formhash": formhash_value, # formhash_value 已经是字符串，无需 urlencode
        "qdxq": "kx",
        "qdmode": "3",
        "todaysay": "",
        "fastreply": "1"
    }

    headers = base_headers.copy()
    headers["Referer"] = "https://www.tsdm39.com/forum.php"
    headers['Cookie'] = cookie
    headers['Content-Type'] = 'application/x-www-form-urlencoded' # 保持 content-type
    headers["Origin"] = 'https://www.tsdm39.com'

    try:
        response = requests.post( # 使用 requests.post
            "https://www.tsdm39.com/plugin.php?id=dsu_paulsign%3Asign&operation=qiandao&infloat=1&sign_as=1&inajax=1",
            data=payload, # requests 可以直接传递字典作为 data，它会自动 urlencode
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        print("签到完成")
    except requests.exceptions.RequestException: # 捕获 requests 异常
        print("Check-in request failed")


def tsdm_work(cookie):
    """天使动漫论坛打工 (使用 requests)"""
    work_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'cookie': cookie,
        'connection': 'Keep-Alive',
        'x-requested-with': 'XMLHttpRequest',
        'referer': 'https://www.tsdm39.net/plugin.php?id=np_cliworkdz:work',
        'content-type': 'application/x-www-form-urlencoded'
    }

    try:
        response_check = requests.get("https://www.tsdm39.com/plugin.php?id=np_cliworkdz%3Awork&inajax=1", headers=work_headers, timeout=10) # requests.get
        response_check.raise_for_status()
        if re.search(r"您需要等待\d+小时\d+分钟\d+秒后即可进行。", response_check.text): # .text 访问响应内容
            print("打工冷却中")
            return

        print("开始打工...")
        data = {"act": "clickad"} # payload 字典
        for _ in range(6):
            response_work = requests.post( # requests.post
                "https://www.tsdm39.com/plugin.php?id=np_cliworkdz:work",
                headers=work_headers,
                data=data, # 直接传递字典
                timeout=10
            )
            response_work.raise_for_status()
            time.sleep(3)

        data_reward = {"act": "getcre"} # reward payload 字典
        response_reward = requests.post( # requests.post
            "https://www.tsdm39.com/plugin.php?id=np_cliworkdz:work",
            headers=work_headers,
            data=data_reward, # 直接传递字典
            timeout=10
        )
        response_reward.raise_for_status()
        reward_content = response_reward.text.strip() # .text 访问响应内容
        print("打工完成:", reward_content)
    except requests.exceptions.RequestException: # 捕获 requests 异常
        print("Work request failed")


def get_score(cookie):
    """获取天使币积分 (使用 requests)"""
    headers = base_headers.copy()
    headers["Referer"] = "https://www.tsdm39.com/forum.php"
    headers['Cookie'] = cookie

    try:
        response = requests.get("https://www.tsdm39.com/home.php?mod=spacecp&ac=credit&showcredit=1", headers=headers, timeout=10) # requests.get
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser') # .text 访问响应内容
        ul_element = soup.find('ul', class_='creditl')
        if ul_element and (li_element := ul_element.find('li', class_='xi1')):
            angel_coins = li_element.get_text(strip=True).replace("天使币:", "").strip()
            return angel_coins
        else:
            print("Score elements not found")
            return "N/A"
    except requests.exceptions.RequestException: # 捕获 requests 异常
        print("Score request failed")
        return "N/A"


def run():
    """主程序入口"""
    print("开始执行天使动漫每日任务...")

    tsdm_check_in(cookie)
    tsdm_work(cookie)
    score = get_score(cookie)
    if score != "N/A":
        message = f"已拥有天使币数量: {score}"
        if telegram_push(message, bot_token, chat_id):
            print(f"已推送天使币数量: {score}")
        else:
            print("推送失败，请检查 Telegram 配置。")
    else:
        print("未能获取到天使币数量，推送可能未包含积分信息。")
    print("每日任务执行完毕。")


if __name__ == "__main__":
    run()
