import base64
import socket
import requests
import os
import sys
import re
import json

ret_message_map = {
    0: "成功", 1: "账号或密码不对，请重新输入", 2: "终端IP已经在线", 3: "系统繁忙，请稍后再试",
    4: "发生未知错误，请稍后再试", 5: "REQ_CHALLENGE 失败，请联系AC确认", 6: "REQ_CHALLENGE 超时，请联系AC确认",
    7: "Radius 认证失败", 8: "Radius 认证超时", 9: "Radius 下线失败", 10: "Radius 下线超时",
    11: "发生其他错误，请稍后再试", 998: "Portal协议参数不全，请稍后再试"
}
mac = "000000000000"


def get_ip_address():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)


def get_home_dir():
    home_dir = "."
    if sys.platform == 'win32':
        home_dir = os.environ['USERPROFILE']
    elif sys.platform == 'linux' or sys.platform == 'darwin':
        home_dir = os.environ['HOME']
    return home_dir


def get_cache_file_path():
    return get_home_dir() + os.path.sep + ".ahu_wifi"


def set_account():
    # 输入信息
    account = input("学号：")
    password = input("密码：")
    # 写入信息
    cache_file = open(get_cache_file_path(), "wb")

    cache_file.write(base64.b64encode(account.encode()))
    cache_file.write(os.linesep.encode())
    cache_file.write(base64.b64encode(password.encode()))
    cache_file.close()


def get_account():
    cache_file = open(get_cache_file_path(), "r")
    if cache_file is None:
        return None
    account = base64.b64decode(cache_file.readline().strip()).decode()
    password = base64.b64decode(cache_file.readline().strip()).decode()
    cache_file.close()
    return account, password


if not os.path.exists(get_cache_file_path()):
    set_account()

user_account, user_password = get_account()

url = "http://172.16.253.3:801/eportal/?c=Portal&a=login&callback=dr1003&login_method=1&user_account=%s" \
      "&user_password=%s&wlan_user_ip=%s&wlan_user_ipv6=&wlan_user_mac=%s&wlan_ac_ip=172.16.253.1" \
      "&wlan_ac_name=&jsVersion=3.3.2&v=9915" % (user_account, user_password, get_ip_address(), mac)
resp = requests.get(url, headers={"Referer": "http://172.16.253.3/"})
regex = re.compile(r"dr1003\((.+?)\)", re.I)
matchRes = regex.match(resp.text)
if matchRes is not None:
    respJson = json.loads(matchRes.group(1))
    ret_code = respJson['ret_code']
    if ret_code in ret_message_map.keys():
        print(ret_message_map[ret_code])
        # 密码错误，删除配置文件
        if ret_code == 1:
            os.remove(get_cache_file_path())
            print("检测到密码错误，已经为您删除配置文件，请关闭本窗口后重新输入账号，密码尝试连接！")
    else:
        print("未知异常，即常见的 AC认证失败")
