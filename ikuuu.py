import requests, json, re, os

session = requests.session()
# 配置用户名（一般是邮箱）
# email = os.environ.get('EMAIL')
# 配置用户名对应的密码 和上面的email对应上
# passwd = os.environ.get('PASSWD')
# 从设置的环境变量中的Variables多个邮箱和密码 ,分割
emails = os.environ.get('IKUUUEMAIL', '').split(',')
passwords = os.environ.get('IKUUUPASSWD', '').split(',')

login_url = 'https://ikuuu.pw/auth/login'
check_url = 'https://ikuuu.pw/user/checkin'
info_url = 'https://ikuuu.pw/user/profile'

header = {
        'origin': 'https://ikuuu.pw',
        'user-agent':'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
}

for email, passwd in zip(emails, passwords):
    session = requests.session()
    data = {
        'email': email,
        'passwd': passwd
    }
    try:
        print(f'[{email}] 进行登录...')
        response = json.loads(session.post(url=login_url,headers=header,data=data).text)
        print(response['msg'])
        # 获取账号名称
        # info_html = session.get(url=info_url,headers=header).text
        # info = "".join(re.findall('<span class="user-name text-bold-600">(.*?)</span>', info_html, re.S))
        # 进行签到
        result = json.loads(session.post(url=check_url,headers=header).text)
        print(result['msg'])
        content = result['msg']
        # 进行推送
        push(content)
    except:
        content = '签到失败'
        print(content)
        push(content)  let cookie = cache[cacheKey] || '';

  if (email && passwd) {
    if (!cookie) {
      cookie = await login(email, passwd, HOST);
      if (cookie) {
        cache[cacheKey] = cookie;
        $.storage.setItem('ikuuu_cookie', cache);
      } else {
        return;
      }
    } else {
      $.log(`使用缓存 cookie: ${cookie}`);
    }
  }

  $.req.setCookie(cookie);
  return await checkin(`${HOST}/user/checkin`);
}

async function checkin(url) {
  const { data } = await $.req.request('POST', url, {}, {}, false);
  if (data.ret === 1 || String(data.msg).includes('签到过')) {
    $.log(`签到成功！${data.msg}`);
    return true;
  } else {
    $.log(`签到失败：${data.msg}`, 'error');
  }
  return false;
}

// process.env.IKUUU = '';
if (require.main === module) {
  $.init(signCheckIn, 'IKUUU').then(() => $.done());
}
