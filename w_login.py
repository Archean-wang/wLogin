import re
import time
import json
import base64
import requests
import binascii

import rsa

ss = requests.Session()
username = b'username'
passwd = 'password'

# 用户名base64加密
su = base64.b64encode(username)

# 预登录参数
data = {
    "entry": "weibo",
    "callback": "sinaSSOController.preloginCallBack",
    "su": su,
    "rsakt": "mod",
    "checkpin": 1,
    "client": "ssologin.js(v1.4.19)",
    "_": time.time()*1000
    }
# 预登录地址
pre_url = 'https://login.sina.com.cn/sso/prelogin.php'
# 预登录返回参数
pre_res = ss.get(pre_url, params=data)
params = re.findall(r'\((.*)\)', pre_res.text)[0]
pre_json = json.loads(params)

# 用返回的公钥加密密码
pub_key = rsa.PublicKey(int(pre_json["pubkey"], 16), int('10001', 16))
string = '\t'.join([str(pre_json["servertime"]), str(pre_json["nonce"])]) + '\n' + passwd
sp = rsa.encrypt(string.encode('utf-8'), pub_key)

# 登录参数
data1 = {
    "entry": "weibo",
    "gateway": 1,
    "from": "",
    "savestate": 7,
    "qrcode_flag": "false",
    "useticket": 1,
    "pagerefer": "https://login.sina.com.cn/crossdomain2.php?action=logout&r=https%3A%2F%2Fpassport.weibo.com%2Fwbsso%2Flogout%3Fr%3Dhttps%253A%252F%252Fweibo.com%26returntype%3D1",
    "vsnf": 1,
    "su": su,
    "service": "miniblog",
    "servertime": pre_json["servertime"],
    "nonce": pre_json["nonce"],
    "pwencode": "rsa2",
    "rsakv": pre_json["rsakv"],
    "sp": binascii.b2a_hex(sp).decode(),
    "sr": "1680*1050",
    "encoding": "UTF-8",
    "prelt": 21,
    "url": "https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
    "returntype": "META",
    }
login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
res = ss.post(login_url, data=data1)

# 登录会有两次跳转
first_url = re.findall(r'replace\("(.*)"\)', res.text)[0]
first_res = ss.get(first_url)
second_url = re.findall(r"replace\('(.*)'\)", first_res.text)[0]
second_res = ss.get(second_url)
print(ss.cookies)
