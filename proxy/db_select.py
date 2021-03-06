# -*- coding: utf-8 -*-
import pymysql
import aiohttp
import asyncio
import time
import random


async def test_new_ip(ip, url, ips_ok):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    conn = aiohttp.TCPConnector(verify_ssl=False)
    async with aiohttp.ClientSession(connector=conn) as session:
        try:
            proxy_ip = 'http://' + ip
            async with session.get(url=url, headers=headers, proxy=proxy_ip, timeout=15) as response:
                if response.status == 200:
                    ips_ok.append((ip, 5))
        except:
            ips_ok.append((ip, 4))


async def test_mysql_ip(ip, url, ips_ok):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    conn = aiohttp.TCPConnector(verify_ssl=False)
    async with aiohttp.ClientSession(connector=conn) as session:
        try:
            proxy_ip = 'http://' + ip[0]
            async with session.get(url=url, headers=headers, proxy=proxy_ip, timeout=15) as response:
                if response.status == 200:
                    new_score = 5 if ip[1] == 5 else ip[1] + 1
                    ips_ok.append((ip[0], new_score))
        finally:
            new_score = 0 if ip[1] == 0 else ip[1] - 1
            ips_ok.append((ip[0], new_score))


def get_mysql_ip():
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


def update_score(ip_list):
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


def delete_duplicate_ip():
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


def insert_mysql_ip(test_url):
    """
    ip 爬取、测试、插入一体化函数
    :param urls:
    :return:
    """
    ips = get_mysql_ip()
    ip_list = list(set(ips))
    print('已做去重处理!')

    ips_ok = []
    print('开始测试新爬取的ip: ')
    try:
        loop = asyncio.get_event_loop()
        for i in range(0, len(ip_list), 10):
            proxies_ip = ip_list[i: i + 10]
            tasks = [test_new_ip(proxy_ip, test_url, ips_ok) for proxy_ip in proxies_ip]
            loop.run_until_complete(asyncio.wait(tasks))
            time.sleep(3)
    except Exception as err:
        print('发生错误:', err.args)

    insert_ip(ips_ok)
    print('数据保存完毕!')


def update_mysql_ip(test_url):
    """
    ip 更新、去零、去重一体化函数
    :param urls:
    :return:
    """
    ip_list = get_mysql_ip()
    ips_ok = []
    print('开始测试新爬取的ip: ')
    try:
        loop = asyncio.get_event_loop()
        for i in range(0, len(ip_list), 10):
            proxies_ip = ip_list[i: i + 10]
            tasks = [test_mysql_ip(proxy_ip, test_url, ips_ok) for proxy_ip in proxies_ip]
            loop.run_until_complete(asyncio.wait(tasks))
            time.sleep(3)
    except Exception as err:
        print('发生错误:', err.args)

    update_score(ips_ok)


print('数据更新完毕!')

delete_ip()
print('已删除score为0的ip!')

delete_duplicate_ip()
print('已做去重处理!')

if __name__ == '__main__':
    test_url = "http://httpbin.org/get"
    insert_mysql_ip(test_url)
    update_mysql_ip(test_url)
