import requests
import os
import time
import xml.etree.ElementTree as ET

def get_cookies():
    cookie_value = os.getenv('SOUTHPLUSCOOKIE', '').strip().replace('\n', '')
    return dict(cookie.split('=', 1) for cookie in cookie_value.split('; ')) if cookie_value else {}

def create_headers(referer=None):
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
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
        'actions': action,
        'cid': cid,
    }

def tasks(url, action, cid, task_type):
    headers = create_headers(url + f'?H_name-tasks-actions-{action}.html')
    params = create_params(action, cid)
    try:
        response = requests.get(url, params=params, headers=headers)
        response.encoding = 'utf-8'
        root = ET.fromstring(response.text)
        values = root.text.split('\t')

        message = values[1] if len(values) > 1 else "无返回内容"
        print(f"{task_type}: {message}")
        send_message_to_telegram(f"{task_type}: {message}")
    except Exception as e:
        print(f"{task_type}请求失败: {e}")
        send_message_to_telegram(f"{task_type}失败: {e}")

if __name__ == "__main__":
    base_url = 'https://snow-plus.net/plugin.php'
    tasks(base_url, 'job', '15', "日常申请")
    tasks(base_url, 'job2', '15', "日常完成")
    tasks(base_url, 'job', '14', "周常申请")
    tasks(base_url, 'job2', '14', "周常完成")
