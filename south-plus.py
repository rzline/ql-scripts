import requests
import os
import xml.etree.ElementTree as ET

def get_cookies(cookie_value):
    return {cookie.split('=')[0]: cookie.split('=')[1] for cookie in cookie_value.split('; ')}

def create_headers(referer=None):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cookie': os.getenv('SOUTHPLUSCOOKIE'),
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    }
    if referer:
        headers['referer'] = referer
    return headers

def create_params(action, cid):
    return {
        'H_name': 'tasks',
        'action': 'ajax',
        'nowtime': '1717167492479',
        'verify': '5af36471',
        'actions': action,
        'cid': cid,
    }

def parse_response(data):
    root = ET.fromstring(data)
    cdata = root.text
    return cdata.split('\t')

def tasks(url, action, cid, type):
    headers = create_headers(url + f'?H_name-tasks-actions-{action}.html.html')
    params = create_params(action, cid)
    
    response = requests.get(url, params=params, headers=headers)
    response.encoding = 'utf-8'
    
    try:
        values = parse_response(response.text)
        expected_length = 2 if '申请' in type else 3
        
        if len(values) == expected_length:
            message = values[1]
            print(f"{type} {message}")
            return "还没超过" not in message
        else:
            raise ValueError("XML格式不正确，请检查COOKIE设置")
    except ET.ParseError:
        raise ValueError("解析XML时出错，请检查返回的数据格式")

url = 'https://snow-plus.net/plugin.php'

if tasks(url, 'job', '15', "申请-日常: "):
    tasks(url, 'job2', '15', "完成-日常: ")
if tasks(url, 'job', '14', "申请-周常: "):
    tasks(url, 'job2', '14', "完成-周常: ")
