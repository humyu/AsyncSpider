# -*- coding: utf-8 -*-
"""
1. 使用 threading模块中的 Thread类 创建线程
2. 数据结构：队列
"""
import json
import threading
import time
from queue import Queue

import requests
from lxml import etree


class QiubaiSpider:
    def __init__(self):
        self.url_temp = "https://www.qiushibaike.com/text/page/{}/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/86.0.4240.193 Safari/537.36"}
        self.url_queue = Queue()
        self.html_queue = Queue()
        self.content_queue = Queue()

    # url_list
    def get_url_list(self):
        # return [self.url_temp.format(i) for i in range(1, 14)]
        for i in range(1, 5):
            self.url_queue.put(self.url_temp.format(i))

    # 发送请求，获取响应
    def parse_url(self):
        while True:
            url = self.url_queue.get()
            response = requests.get(url, headers=self.headers)
            self.html_queue.put(response.content.decode())
            # return response.content.decode()
            # 表示当前工作完成
            self.url_queue.task_done()

    # 提取数据
    def get_content_list(self):
        while True:
            html_str = self.html_queue.get()
            html = etree.HTML(html_str)
            content_list = []
            # 分组
            div_list = html.xpath("//div[@class='col1 old-style-col1']/div")
            for div in div_list:
                item = dict()
                item["author_name"] = div.xpath(".//div[@class='author clearfix']/a[2]/h2/text()")
                item["author_name"] = item["author_name"][0].strip()
                item["content_href"] = div.xpath(".//a[@class='contentHerf']/@href")
                item["content_img"] = div.xpath(".//div[@class='thumb']/a/img/@src")
                item["content_img"] = item["content_img"][0] if len(item["content_img"]) > 0 else None
                item["god_cmt"] = div.xpath(
                    ".//a[@class='indexGodCmt']/div[@class='cmtMain']/div[@class='main-text']/text()")
                item["god_cmt"] = item["god_cmt"][0].strip() if len(item["god_cmt"]) > 0 else None
                content_list.append(item)
            self.content_queue.put(content_list)
            self.html_queue.task_done()

    # 保存
    def save_content_list(self):
        while True:
            # for i in content_list:
            #     print(i)
            content_list = self.content_queue.get()
            file_path = "糗事百科_多线程.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                for content in content_list:
                    f.write(json.dumps(content, ensure_ascii=False, indent=2))
                    f.write("\n")
            self.content_queue.task_done()

    # 实现主要逻辑
    def run(self):
        thread_list = []
        # 1.url_list
        t_url = threading.Thread(target=self.get_url_list)
        thread_list.append(t_url)
        # 2.遍历，发送请求，获取响应
        # 多设置几个线程
        for i in range(4):
            t_parse = threading.Thread(target=self.parse_url)
            thread_list.append(t_parse)
        # 3.提取数据
        t_html = threading.Thread(target=self.get_content_list)
        thread_list.append(t_html)
        # 4.保存
        for i in range(10):
            t_save = threading.Thread(target=self.save_content_list)
            thread_list.append(t_save)

        for t in thread_list:
            # 把子线程设置为守护线程，即当主线程结束时，子线程结束。必须在start()之前设置
            t.setDaemon(True)
            t.start()

        for q in [self.url_queue, self.html_queue, self.content_queue]:
            # 等到队列为空，再执行别的操作
            q.join()


if __name__ == '__main__':
    begin = time.time()
    qiubai = QiubaiSpider()
    qiubai.run()
    print("主线程结束")
    times = time.time() - begin
    print(times)
