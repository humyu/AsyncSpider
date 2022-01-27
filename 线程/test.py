# -*- coding: utf-8 -*-
import sys
from multiprocessing.dummy import Pool

import requests
from retrying import retry

sys.path.append("..")

from handler import retry_handler as rh

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'zh-CN,zh;q=0.9', 'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Pragma': 'no-cache', 'Referer': 'https://www.hao123.com/',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"', 'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none', 'Sec-Fetch-User': '?1', 'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/96.0.4664.45 Safari/537.36'}
proxies = {
    "http": "115.218.2.203:9000"
}


@retry(wait_random_min=1000, wait_random_max=4000, wait_fixed=2000,
       retry_on_result=rh.retry_if_bad_code, retry_on_exception=rh.retry_if_exception)
def parse_url(url):
    response = requests.get(url, headers=headers, proxies=proxies, timeout=6)
    print(url, response.status_code)
    return response.status_code


def run():
    urls = [
        'https://www.baidu.com',
        'https://www.sina.com.cn',
        'https://www.tmall.com',
        'https://blog.csdn.net',
        'https://www.python.org',
        'https://www.openstack.org',
        'https://www.sohu.com',
        'https://tuijian.hao123.com',
        'https://www.163.com',
        'https://www.xxsy.net',
        'http://changba.com',
        'https://httpbin.org/get',
    ]
    pool = Pool(4)
    pool.map(parse_url, urls)


if __name__ == '__main__':
    run()
