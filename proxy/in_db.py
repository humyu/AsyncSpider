# -*- coding: utf-8 -*-

import pymysql
import requests
from bs4 import BeautifulSoup
import pickle
import aiohttp
import asyncio
import time
import random


async def test_newip(ip_, url, ip_ok):
    """
    测试新爬取的 ip
    :param ip_: 新爬取的 ip 列表
    :param url: 测试的网站
    :param ip_ok: 返回的结果列表
    :return:
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    conn = aiohttp.TCPConnector(verify_ssl=False)
    async with aiohttp.ClientSession(connector=conn) as session:
        print('正在测试ip: ' + ip_)
        try:
            proxy_ip = 'http://' + ip_
            async with session.get(url=url, headers=headers, proxy=proxy_ip, timeout=15) as response:
                if response.status == 200:
                    print('代理可用: ' + ip_)
                    ip_ok.append((ip_, 5))
                else:
                    print('请求响应码不合法 ' + ip_)
        except:
            ip_ok.append((ip_, 4))
            print('代理请求失败', ip_)


async def test_mysqlip(ip_, url, ip_ok):
    """
    测试数据库里的ip
    :param ip_: 数据库里的 ip 列表
    :param url: 测试的网站
    :param ip_ok: 返回的结果列表
    :return:
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    conn = aiohttp.TCPConnector(verify_ssl=False)
    async with aiohttp.ClientSession(connector=conn) as session:
        print('正在测试ip: ' + ip_[0])
        try:
            proxy_ip = 'http://' + ip_[0]
            async with session.get(url=url, headers=headers, proxy=proxy_ip, timeout=15) as response:
                if response.status == 200:
                    print('ip可用: ' + ip_[0])
                    new_score = 5 if ip_[1] == 5 else ip_[1] + 1
                    ip_ok.append((ip_[0], new_score))
                else:
                    print('请求响应码不合法 ' + ip_[0])
        except:
            new_score = 0 if ip_[1] == 0 else ip_[1] - 1
            ip_ok.append((ip_[0], new_score))
            print('代理请求失败', ip_[0])


def get_mysqlip():
    """
    获取数据库里的 ip
    :return:
    """
    db = pymysql.connect(host='localhost', port=3306, user='用户名', password='密码',
                         database='数据库名', charset='utf8')
    cursor = db.cursor()
    sql = 'select ip, score from ipproxy'
    try:
        cursor.execute(sql)
        mysql_ip = list(cursor.fetchall())
        return mysql_ip
    except Exception as err:
        print('查询错误!!!')
        print(err)


def update_ipscore(ip_list):
    """
    更新数据库里的 ip 的分数
    :param ip_list:
    :return:
    """
    db = pymysql.connect(host='localhost', port=3306, user='用户名', password='密码',
                         database='数据库名', charset='utf8')
    cursor = db.cursor()
    for ip_ in ip_list:
        sql = 'update ipproxy set score=%s where ip=%s'
        cursor.execute(sql, (ip_[1], ip_[0]))
        db.commit()
    cursor.close()
    db.close()


def delete_ip():
    """
    删除数据库里分数为 0 的 ip
    :return:
    """
    db = pymysql.connect(host='localhost', port=3306, user='用户名', password='密码',
                         database='数据库名', charset='utf8')
    cursor = db.cursor()
    sql = 'delete from ipproxy where score=0'
    try:
        cursor.execute(sql)
    except Exception as err:
        print('删除错误!!!')
        print(err)
    db.commit()
    cursor.close()
    db.close()


def delete_ideticalip():
    """
    去重
    :return:
    """
    db = pymysql.connect(host='localhost', port=3306, user='用户名', password='密码',
                         database='数据库名', charset='utf8')
    cursor = db.cursor()
    sql = 'delete from ipproxy where ip in (select ip  from (select ip from ipproxy group by ip having count(*)>1) s1)' \
          'and id not in (select id from (select id from ipproxy group by ip having count(*)>1) s2)'
    try:
        cursor.execute(sql)
    except Exception as err:
        print('删除错误!!!')
        print(err)
    db.commit()
    cursor.close()
    db.close()


def insert_ip(ip_list):
    # 新爬取的ip直接插入数据库
    db = pymysql.connect(host='localhost', port=3306, user='用户名', password='密码',
                         database='数据库名', charset='utf8')
    cursor = db.cursor()
    sql = 'create table if not exists ipproxy(' \
          'id int not null primary key auto_increment, ' \
          'ip char(21) not null , ' \
          'score int not null ) default charset utf8'
    cursor.execute(sql)

    try:
        sql = 'insert into ipproxy (ip, score) values (%s, %s)'
        cursor.executemany(sql, ip_list)
        # cursor.execute('drop table ipproxy')
    except Exception as err:
        print('插入错误!!!')
        print(err)
    db.commit()
    cursor.close()
    db.close()


def insret_mysqlip(urls):
    """
    ip 爬取、测试、插入一体化函数
    :param urls:
    :return:
    """
    ip_list1 = get_66ip()
    ip_list2 = get_kaixinip()
    ip_list3 = get_goubanjiaip()
    ip_list = list(set(ip_list1 + ip_list2 + ip_list3))
    print('已做去重处理!')

    ip_ok = []
    print('开始测试新爬取的ip: ')
    try:
        loop = asyncio.get_event_loop()
        for i in range(0, len(ip_list), 10):
            proxies_ip = ip_list[i: i + 10]
            tasks = [test_newip(proxy_ip, random.choice(urls), ip_ok) for proxy_ip in proxies_ip]
            loop.run_until_complete(asyncio.wait(tasks))
            time.sleep(3)
    except Exception as err:
        print('发生错误:', err.args)

    insert_ip(ip_ok)
    print('数据保存完毕!')


def update_mysqlip(urls):
    """
    ip 更新、去零、去重一体化函数
    :param urls:
    :return:
    """
    ip_list = get_mysqlip()
    ip_ok = []
    print('开始测试新爬取的ip: ')
    try:
        loop = asyncio.get_event_loop()
        for i in range(0, len(ip_list), 10):
            proxies_ip = ip_list[i: i + 10]
            tasks = [test_mysqlip(proxy_ip, random.choice(urls), ip_ok) for proxy_ip in proxies_ip]
            loop.run_until_complete(asyncio.wait(tasks))
            time.sleep(3)
    except Exception as err:
        print('发生错误:', err.args)

    update_ipscore(ip_ok)


print('数据更新完毕!')

delete_ip()
print('已删除score为0的ip!')

delete_ideticalip()
print('已做去重处理!')

if __name__ == '__main__':
    urls = ['https://blog.csdn.net/qq_42730750/article/details/107868879',
            'https://blog.csdn.net/qq_42730750/article/details/107931738',
            'https://blog.csdn.net/qq_42730750/article/details/107869022',
            'https://blog.csdn.net/qq_42730750/article/details/108016855',
            'https://blog.csdn.net/qq_42730750/article/details/107703589',
            'https://blog.csdn.net/qq_42730750/article/details/107869233',
            'https://blog.csdn.net/qq_42730750/article/details/107869944',
            'https://blog.csdn.net/qq_42730750/article/details/107919690']

    insret_mysqlip(urls)
    update_mysqlip(urls)
