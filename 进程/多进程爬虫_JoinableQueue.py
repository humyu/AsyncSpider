# -*- coding: utf-8 -*-
from multiprocessing import Process,JoinableQueue
import requests
from lxml import etree
import json


class ProcessSpider():

    def __init__(self):
        self.url_temp = "https://www.qiushibaike.com/text/page/{}/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/86.0.4240.193 Safari/537.36"}
        self.url_queue = JoinableQueue()
        self.html_queue = JoinableQueue()
        self.content_queue = JoinableQueue()

    # url_list
    def get_url_list(self):
        for i in range(1, 3):
            self.url_queue.put(self.url_temp.format(i))

    # 发送请求，获取响应
    def parse_url(self):
        while True:
            url = self.url_queue.get()
            response = requests.get(url, headers=self.headers)
            self.html_queue.put(response.content.decode())
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
            self.html_queue.task_done()

    # 保存
    def save_content_list(self):
        while True:
            content_list = self.content_queue.get()
            file_path = "糗事百科_多进程2.txt"
            with open(file_path, "a", encoding="utf-8") as f:
                for content in content_list:
                    f.write(json.dumps(content, ensure_ascii=False, indent=2))
                    f.write("\n")
            self.content_queue.task_done()

    def run(self):
        process_list = []
        process1 = Process(target=self.get_url_list,args=())
        process_list.append(process1)
        process2 = Process(target=self.parse_url,args=())
        process_list.append(process2)
        process3 = Process(target=self.get_content_list,args=())
        process_list.append(process3)
        process4 = Process(target=self.save_content_list,args=())
        process_list.append(process4)
        for p in process_list:
            p.daemon = True
            p.start()
        process1.join()
        for q in [self.url_queue, self.html_queue, self.content_queue]:
            q.join()
        print("主进程结束")


if __name__ == '__main__':
    spider = ProcessSpider()
    spider.run()
