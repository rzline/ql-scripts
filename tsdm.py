import httpx
import re
import urllib.parse
import time
import os
# import yaml # No longer needed
from bs4 import BeautifulSoup

# --- 从环境变量中读取配置变量 ---
bot_token = os.environ.get("TG_BOT_TOKEN")  # 从环境变量中获取 BOT_TOKEN
chat_id = os.environ.get("TG_CHAT_ID")      # 从环境变量中获取 CHAT_ID
cookie = os.environ.get("TSDM")        # 从环境变量中获取 COOKIE

# 检查环境变量是否设置
if not bot_token:
    print("Error: BOT_TOKEN 环境变量未设置。")
    exit(1) # 退出程序并返回错误代码
if not chat_id:
    print("Error: CHAT_ID 环境变量未设置。")
    exit(1) # 退出程序并返回错误代码
if not cookie:
    print("Error: COOKIE 环境变量未设置。")
    exit(1) # 退出程序并返回错误代码
# --- 环境变量读取结束 ---


# 基础 headers，减少重复 (保持不变)
base_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}

# ---  Telegram 推送函数  ---
def telegram_push(message, bot_token, chat_id):
    """发送 Telegram 推送消息"""
    if not bot_token or not chat_id:
        print("Telegram Bot Token 或 Chat ID 未配置，无法发送推送。")
        return False

    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown" # 可以选择 "Markdown" 或 "HTML" 来格式化消息
    }

    try:
        response = httpx.post(api_url, json=payload, timeout=10) # 设置超时时间
        response.raise_for_status() # 检查 HTTP 错误状态码
        response_json = response.json()
        if response_json.get("ok"):
            print("Telegram 推送消息发送成功！")
            return True
        else:
            print(f"Telegram 推送消息发送失败: {response_json}")
            return False
    except httpx.HTTPError as e:
        print(f"Telegram 推送请求失败 (HTTPError): {e}")
        return False
    except httpx.TimeoutException as e:
        print(f"Telegram 推送请求超时: {e}")
        return False
    except Exception as e:
        print(f"Telegram 推送过程中发生错误: {e}")
        return False
# --- Telegram 推送函数结束 ---


# 函数 (保持不变 -  tsdm_check_in, tsdm_work, get_score, get_formhash)
def get_formhash(client, cookie):
    """获取 formhash 值"""
    headers = base_headers.copy()
    headers['Cookie'] = cookie
    try:
        response = client.get("https://www.tsdm39.com/forum.php", headers=headers)
        response.raise_for_status()  # 检查 HTTP 错误
        match = re.search(r'formhash=(.+?)"', response.text)
        if match:
            return match.group(1)
        else:
            print("Error: formhash not found.")
            return None
    except httpx.HTTPError as e:
        print(f"HTTP Error while getting formhash: {e}")
        return None
    except Exception as e:
        print(f"Error getting formhash: {e}")
        return None


def tsdm_check_in(cookie, bot_token, chat_id):
    """天使动漫论坛签到"""
    headers = base_headers.copy()  # 复制基础 headers
    headers["Referer"] = "https://www.tsdm39.com/forum.php"
    headers['Cookie'] = cookie

    with httpx.Client(headers=headers) as client:
        formhash_value = get_formhash(client, cookie)
        if not formhash_value:
            print("签到失败，无法获取 formhash")
            return

        encoded_formhash = urllib.parse.quote(formhash_value)
        checkin_headers = headers.copy()
        checkin_headers['Content-Type'] = 'application/x-www-form-urlencoded'
        checkin_headers["Origin"] = 'https://www.tsdm39.com'
        payload = {"formhash": encoded_formhash, "qdxq": "kx", "qdmode": "3", "todaysay": "", "fastreply": "1"}

        try:
            response = client.post(
                "https://www.tsdm39.com/plugin.php?id=dsu_paulsign%3Asign&operation=qiandao&infloat=1&sign_as=1&inajax=1",
                data=payload, headers=checkin_headers
            )
            response.raise_for_status()
            print("签到完成")
        except httpx.HTTPError as e:
            print(f"签到请求失败: {e}")
        except Exception as e:
            print(f"签到过程中发生错误: {e}")


def tsdm_work(cookie, bot_token, chat_id):
    """天使动漫论坛打工"""
    work_headers = { # 工作的 headers 不需要 Referer 等通用信息，简化
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'cookie': cookie,
        'connection': 'Keep-Alive',
        'x-requested-with': 'XMLHttpRequest',
        'referer': 'https://www.tsdm39.net/plugin.php?id=np_cliworkdz:work', # 仍然需要 Referer
        'content-type': 'application/x-www-form-urlencoded'
    }

    with httpx.Client(headers=work_headers) as client:
        try:
            response = client.get("https://www.tsdm39.com/plugin.php?id=np_cliworkdz%3Awork&inajax=1")
            response.raise_for_status()
            if re.search(r"您需要等待\d+小时\d+分钟\d+秒后即可进行。", response.text):
                print("打工冷却中，请稍后再试")
                return

            print("开始打工...")
            data = {"act": "clickad"}
            for _ in range(6): # 使用 _ 表示循环变量不使用
                work_response = client.post("https://www.tsdm39.com/plugin.php?id=np_cliworkdz:work", headers=work_headers, data=data)
                work_response.raise_for_status()
                time.sleep(3)

            data = {"act": "getcre"}
            reward_response = client.post("https://www.tsdm39.com/plugin.php?id=np_cliworkdz:work", headers=work_headers, data=data)
            reward_response.raise_for_status()
            print("打工完成:", reward_response.text.strip()) # 简化输出
        except httpx.HTTPError as e:
            print(f"打工请求失败: {e}")
        except Exception as e:
            print(f"打工过程中发生错误: {e}")


def get_score(cookie, bot_token, chat_id):
    """获取天使币积分"""
    headers = base_headers.copy()
    headers["Referer"] = "https://www.tsdm39.com/forum.php"
    headers['Cookie'] = cookie

    with httpx.Client(headers=headers) as client:
        try:
            response = client.get("https://www.tsdm39.com/home.php?mod=spacecp&ac=credit&showcredit=1", headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            ul_element = soup.find('ul', class_='creditl')
            if ul_element: # 检查 ul_element 是否找到
                li_element = ul_element.find('li', class_='xi1')
                if li_element: # 检查 li_element 是否找到
                    angel_coins = li_element.get_text(strip=True).replace("天使币:", "").strip()
                    return angel_coins
                else:
                    print("Error: 天使币 li 元素未找到")
                    return "N/A"
            else:
                print("Error: creditl ul 元素未找到")
                return "N/A"

        except httpx.HTTPError as e:
            print(f"获取积分请求失败: {e}")
            return "N/A"
        except Exception as e:
            print(f"获取积分过程中发生错误: {e}")
            return "N/A"


def run():
    """主程序入口"""
    print("开始执行天使动漫每日任务...")

    tsdm_check_in(cookie, bot_token, chat_id) # 直接使用环境变量读取的变量
    tsdm_work(cookie, bot_token, chat_id)     # 直接使用环境变量读取的变量
    score = get_score(cookie, bot_token, chat_id) # 直接使用环境变量读取的变量
    if score != "N/A":
        message = f"已拥有天使币数量: {score}" # 准备推送消息
        telegram_push(message, bot_token, chat_id) # 使用新的 Telegram 推送函数
        print(f"已推送天使币数量: {score}")
    else:
        print("未能获取到天使币数量，推送可能未包含积分信息。")
    print("每日任务执行完毕。")


if __name__ == "__main__":
    run()