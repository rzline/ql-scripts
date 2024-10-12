import requests
import os
import xml.etree.ElementTree as ET

def get_cookies(cookie_value):
    """将 cookie 字符串解析为字典格式"""
    return {cookie.split('=')[0]: cookie.split('=')[1] for cookie in cookie_value.split('; ')}

def create_headers(referer=None):
    """构建 HTTP 请求头，包括用户代理和 Cookie"""
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cookie': os.getenv('SOUTHPLUSCOOKIE'),  # 从环境变量获取 Cookie
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    }
    if referer:
        headers['referer'] = referer  # 如果提供了 referer，则添加到请求头中
    return headers

def create_params(action, cid):
    """创建请求参数"""
    return {
        'H_name': 'tasks',
        'action': 'ajax',
        'nowtime': str(int(requests.get('https://worldtimeapi.org/api/timezone/Etc/UTC').json()['unixtime'] * 1000)),  # 获取当前时间戳
        'verify': '5af36471',  # 固定的验证参数，可以考虑动态获取
        'actions': action,
        'cid': cid,
    }

def parse_response(data):
    """解析 XML 响应，提取所需信息"""
    root = ET.fromstring(data)
    cdata = root.text
    return cdata.split('\t')  # 按制表符分割提取的数据

def tasks(url, action, cid, task_type):
    """主任务处理函数，进行任务申请和完成操作"""
    headers = create_headers(url + f'?H_name-tasks-actions-{action}.html.html')
    params = create_params(action, cid)
    
    # 发送 GET 请求
    response = requests.get(url, params=params, headers=headers)
    response.encoding = 'utf-8'
    
    try:
        values = parse_response(response.text)  # 解析响应内容
        expected_length = 2 if '申请' in task_type else 3  # 根据任务类型确定期望的返回长度
        
        if len(values) == expected_length:  # 检查返回数据的长度
            message = values[1]  # 获取消息内容
            print(f"{task_type} {message}")  # 打印消息
            return "还没超过" not in message  # 返回是否可以继续任务
        else:
            raise ValueError("XML格式不正确，请检查COOKIE设置")  # 抛出格式错误
    except ET.ParseError:
        raise ValueError("解析XML时出错，请检查返回的数据格式")  # 捕获解析错误

# 主程序执行部分
if __name__ == "__main__":
    url = 'https://snow-plus.net/plugin.php'
    
    # 处理日常任务
    if tasks(url, 'job', '15', "申请-日常: "):
        tasks(url, 'job2', '15', "完成-日常: ")
    
    # 处理周常任务
    if tasks(url, 'job', '14', "申请-周常: "):
        tasks(url, 'job2', '14', "完成-周常: ")
