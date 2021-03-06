# -*- coding: utf-8 -*-
import requests
import random

test_url = 'http://httpbin.org/get'  # 测试ip是否可用的 url
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/86.0.4240.193 Safari/537.36'}


def test_proxy(proxy):
    proxies = {
        'http': f'http://{proxy}',
        'https': f'https://{proxy}',
    }
    resp = requests.get(url=test_url, proxies=proxies, headers=headers, timeout=10)
    if resp.status_code == 200:
        return proxies
    else:
        return False


def get_proxies():
    result = []
    with open('ip_in_file.txt', 'r') as f:
        for line in f:
            result.append(line.strip('\n'))
    ips = list(filter(None, result))
    return ips


def ip_select():
    ips = get_proxies()
    while True:
        ip = random.choice(ips)
        result = test_proxy(ip)
        if result:
            break
    return result
