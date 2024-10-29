import { Env } from './utils';

const $ = new Env('ikuuu签到');

async function getIkuuuHost() {
  if (process.env.SSPANEL_HOST) return process.env.SSPANEL_HOST;

  let host = 'https://ikuuu.pw';
  try {
    const { data: html } = await $.req.get('https://ikuuu.club', {}, { 'content-type': 'text/html' });
    host = /<p><a href="(https:\/\/[^"]+)\/?"/g.exec(html)?.[1] || host;
  } catch (error) {
    console.error('获取主机地址失败:', error.message);
  }
  return host.replace(/\/$/, '');
}

async function login(email, passwd, host) {
  const url = `${host}/auth/login`;
  const { data, headers } = await $.req.post(url, { email, passwd });

  if (data.ret === 1) {
    const cookie = headers['set-cookie']!.map(d => d.split(';')[0]).join(';');
    $.log(data.msg || '登录成功！');
    return cookie;
  } else {
    $.log(data.msg || '登录失败！', 'error');
    return null;
  }
}

async function signCheckIn(cfg) {
  const [email, passwd, HOST = await getIkuuuHost()] = cfg.split('#');
  const cacheKey = `${HOST}_${email}`;
  const cache = $.storage.getItem('ikuuu_cookie') || {};

  let cookie = cache[cacheKey] || '';

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
