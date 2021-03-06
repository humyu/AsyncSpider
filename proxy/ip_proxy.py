# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import time
from lxml import etree
import tesserocr
from PIL import Image
import requests
from setting import db_mysql

# db_mysql = DBMysql()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/86.0.4240.193 Safari/537.36"}


def parse_img(url):
    response = requests.get(url, headers=headers)
    return response.content


async def parse_url(url):
    """多任务的架构中数据的爬取是封装在特殊函数中的，我们一定要保证数据请求结束后，在实现数据解析"""
    async with aiohttp.ClientSession() as sess:  # 实例化一个请求对象
        # get/post(url,headers,params/data,proxy="http://ip:port")
        async with await sess.get(url=url) as response:  # 使用get发起请求，返回一个相应对象
            page_text = await response.text()  # text()获取字符串形式的相应数据  read()获取byte类型的响应数据
            return page_text


def img_recognition(url):
    r = parse_img(url)
    with open('img.png', 'wb') as f:
        f.write(r)
    image = Image.open("img.png")
    result = tesserocr.image_to_text(image).strip()
    return result


async def parse(url):
    page_text = await parse_url(url)
    tree = etree.HTML(page_text)
    tr_list = tree.xpath("//div[@class='free-content']/table[@class='mimvp-tbl free-proxylist-tbl']/tbody/tr")
    proxy_list = []
    for tr in tr_list:
        ip = tr.xpath("./td[@class='free-proxylist-tbl-proxy-ip']/text()")
        ip = ip[0].strip()
        port_url = tr.xpath("./td[@class='free-proxylist-tbl-proxy-port']/img/@src")
        port_url = port_url[0].strip()
        port_url = "https://proxy.mimvp.com/" + port_url
        port = img_recognition(port_url)
        proxy_str = ip + ":" + port
        proxy_list.append(proxy_str)
    return proxy_list


# def save_to_mysql(proxy_list):
#     for proxy in proxy_list.result():
#         item = {"proxy": proxy}
#         db_mysql.process_item(item)


def save_to_file(proxy_list):
    file_path = "ip_in_file.txt"
    with open(file_path, "w+", encoding="utf-8") as f:
        for content in proxy_list.result():
            f.write(content)
            f.write("\n")


if __name__ == "__main__":
    start = time.time()
    proxy_url = "https://proxy.mimvp.com/freesecret"
    # 1.创建协程对象
    c = parse(proxy_url)
    # 2.创建任务对象
    task = asyncio.ensure_future(c)
    task.add_done_callback(save_to_file)
    # 3.创建事件循环对象
    loop = asyncio.get_event_loop()
    # 4.将任务对象注册到事件循环中且开启事件循环
    loop.run_until_complete(task)  # 必须使用wait方法对tasks封装
    print("总耗时:", time.time() - start)
