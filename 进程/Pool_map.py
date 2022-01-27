# -*- coding: utf-8 -*-
import os
import time
from multiprocessing import Pool


import requests

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
    "http": "47.92.234.75:80"
}


def parse_url(url):
    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=6)
        return url, response.status_code
    except Exception as e:
        print(e)


if __name__ == '__main__':
    # 查看 cpu 个数
    print(f"cpu 个数: {os.cpu_count()}")
    # 最大四个进程
    p = Pool(4)
    urls = [
        'https://www.baidu.com',
        'https://www.sina.com.cn',
        'https://www.tmall.com',
        'https://blog.csdn.net/',
        'https://www.python.org',
        'https://www.openstack.org',
        'https://www.sohu.com/',
        'http://tuijian.hao123.com/',
        'http://www.163.com/',
        'http://www.xxsy.net/',
        'http://changba.com/',
    ]
    # 开 7 个任务
    # ret_list = p.map(parse_url, urls)
    ret_list = p.map_async(parse_url, urls)
    print(ret_list.get())
    # 禁止往进程池内在添加任务
    p.close()
    # 等待进程池
    p.join()
    print('主进程')