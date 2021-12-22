# -*- coding: utf-8 -*-
"""
multiprocessing 模块的 Process 类 创建子进程
multiprocessing 模块的 Process 类 作为进程间的通信
"""
import json
from multiprocessing import Process, Queue
import time

import requests
from lxml import etree


class ProcessSpider():

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
        for i in range(1, 5):
            self.url_queue.put(self.url_temp.format(i))
            print("生产%s馒头" % i)
        self.url_queue.put(None)

    # 发送请求，获取响应
    def parse_url(self):
        while True:
            url = self.url_queue.get()
            if url is None:
                break
            print("消费%s馒头" % url)
            response = requests.get(url, headers=self.headers)
            self.html_queue.put(response.content.decode())
        self.html_queue.put(None)

    # 提取数据
    def get_content_list(self):
        while True:
            html_str = self.html_queue.get()
            if html_str is None:
                print("提取完毕")
                break
            html = etree.HTML(html_str)
            content_list = []
            # 分组
            div_list = html.xpath("//div[@class='col1 old-style-col1']/div")
            for div in div_list:
                item = dict()
                item["author_img"] = div.xpath(".//div[@class='author clearfix']/a[@rel='nofollow']/img/@src")
                item["author_img"] = item["author_img"][0] if len(item["author_img"]) > 0 else None
                item["author_name"] = div.xpath(".//div[@class='author clearfix']/a[2]/h2/text()")
                item["author_name"] = item["author_name"][0].strip()
                item["author_gender"] = div.xpath(".//div[contains(@class,'articleGender')]/@class")
                item["author_gender"] = item["author_gender"][0].split(" ")[-1].replace("Icon", "") if len(
                    item["author_gender"]) > 0 else None
                item["author_age"] = div.xpath(".//div[contains(@class,'articleGender')]/text()")
                item["author_age"] = item["author_age"][0] if len(item["author_age"]) > 0 else None
                item["content"] = div.xpath(".//div[@class='content']/span[1]/text()")
                item["content"] = "".join(item["content"]).strip()
                item["content_href"] = div.xpath(".//a[@class='contentHerf']/@href")
                item["content_img"] = div.xpath(".//div[@class='thumb']/a/img/@src")
                item["content_img"] = item["content_img"][0] if len(item["content_img"]) > 0 else None
                item["god_cmt"] = div.xpath(
                    ".//a[@class='indexGodCmt']/div[@class='cmtMain']/div[@class='main-text']/text()")
                item["god_cmt"] = item["god_cmt"][0].strip() if len(item["god_cmt"]) > 0 else None
                content_list.append(item)
            self.content_queue.put(content_list)
        self.content_queue.put(None)

    # 保存
    def save_content_list(self):
        while True:
            # for i in content_list:
            #     print(i)
            content_list = self.content_queue.get()
            if content_list is None:
                print("保存完毕")
                break
            file_path = "糗事百科_多进程.txt"
            with open(file_path, "a", encoding="utf-8") as f:
                for content in content_list:
                    f.write(json.dumps(content, ensure_ascii=False, indent=2))
                    f.write("\n")

    def run(self):
        process1 = Process(target=self.get_url_list, args=())
        process2 = Process(target=self.parse_url, args=())
        process3 = Process(target=self.get_content_list, args=())
        process4 = Process(target=self.save_content_list, args=())
        process1.start()
        process2.start()
        process3.start()
        process4.start()
        process1.join()
        process2.join()
        process3.join()
        process4.join()


if __name__ == '__main__':
    begin = time.time()
    spider = ProcessSpider()
    spider.run()
    print("主进程结束")
    times = time.time() - begin
    print(times)
