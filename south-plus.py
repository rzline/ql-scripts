import requests
import os
import time
import xml.etree.ElementTree as ET

def get_cookies():
    cookie_value = os.getenv('SOUTHPLUSCOOKIE', '').strip().replace('\n', '')
    return dict(cookie.split('=', 1) for cookie in cookie_value.split('; ')) if cookie_value else {}

def create_headers(referer=None):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'cookie': '; '.join(f'{k}={v}' for k, v in get_cookies().items())
    }
    if referer:
        headers['referer'] = referer
    return headers

def create_params(action, cid):
    return {
        'H_name': 'tasks',
        'action': 'ajax',
        'nowtime': str(int(time.time() * 1000)),
        'verify': '5af36471',
        'actions': action,
        'cid': cid,
    }

def parse_response(data):
    try:
        root = ET.fromstring(data)
        return root.text.split('\t')
    except ET.ParseError:
        return []

def send_telegram_message(message):
    bot_token, chat_id = os.getenv('TG_BOT_TOKEN'), os.getenv('TG_CHAT_ID')
    if bot_token and chat_id:
        requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', json={'chat_id': chat_id, 'text': message})

def tasks(url, action, cid, task_type, notify=True):
    headers = create_headers(url + f'?H_name-tasks-actions-{action}.html.html')
    params = create_params(action, cid)

    try:
        response = requests.get(url, params=params, headers=headers)
        response.encoding = 'utf-8'
        values = parse_response(response.text)
        if len(values) == (2 if '申请' in task_type else 3):
            message = values[1]
            print(f"{task_type} {message}")
            if notify:
                send_telegram_message(f"{task_type} {message}")
            return "还没超过" not in message
        else:
            print("XML格式不正确，请检查COOKIE设置")
            return False
    except requests.RequestException as e:
        print(f"请求出错: {e}")
        return False

if __name__ == "__main__":
    url = 'https://snow-plus.net/plugin.php'
    
    if tasks(url, 'job', '15', "申请-日常: "):
        tasks(url, 'job2', '15', "完成-日常: ")
    
    if tasks(url, 'job', '14', "申请-周常: "):
        tasks(url, 'job2', '14', "完成-周常: ")
