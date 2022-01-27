# -*- coding: utf-8 -*-
"""
multiprocessing模块结合 Process类和 JoinableQueue类
"""
from multiprocessing import Process,JoinableQueue
import requests
from lxml import etree
import json
import time


class ProcessSpider():

    def __init__(self):
        self.url_temp = "https://ssr1.scrape.center/page/{}"
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'zh-CN,zh;q=0.9', 'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': 'UM_distinctid=17e004b8696638-054f1543e7fd3c-978183a-100200-17e004b8697346', 'DNT': '1',
            'Host': 'ssr1.scrape.center', 'Pragma': 'no-cache', 'Referer': 'https://ssr1.scrape.center/',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"', 'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-User': '?1', 'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/96.0.4664.45 Safari/537.36'}
        self.url_queue = JoinableQueue()
        self.html_queue = JoinableQueue()
        self.content_queue = JoinableQueue()
        self.proxies = {
            "http": "58.55.231.237:7082"
        }

    # url_list
    def get_url_list(self):
        for i in range(1, 5):
            self.url_queue.put(self.url_temp.format(i))

    # 发送请求，获取响应
    def parse_url(self):
        while True:
            url = self.url_queue.get()
            response = requests.get(url, headers=self.headers, proxies=self.proxies)
            self.html_queue.put(response.content.decode())
            self.url_queue.task_done()

    # 提取数据
    def crawl_page(self):
        while True:
            html_str = self.html_queue.get()
            html = etree.HTML(html_str)
            content_list = []
            div_list = html.xpath("//div[@class='el-card item m-t is-hover-shadow']")
            for div in div_list:
                detail_url = div.xpath("./div/div/div[2]/a/@href")
                detail_url = detail_url[0]
                title = div.xpath("./div/div/div[2]/a/h2/text()")
                title = title[0]
                categories = div.xpath("./div/div/div[2]/div[1]//span/text()")
                categories = ",".join(categories)
                item = {
                    "detail_url": detail_url,
                    "title": title,
                    "categories": categories,
                }
                content_list.append(item)
            self.content_queue.put(content_list)
            self.html_queue.task_done()

    # 保存
    def save_to_file(self):
        file_path = "spider1.txt"
        while True:
            content_list = self.content_queue.get()
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
        process3 = Process(target=self.crawl_page,args=())
        process_list.append(process3)
        process4 = Process(target=self.save_to_file,args=())
        process_list.append(process4)
        for p in process_list:
            p.daemon = True
            p.start()
        process1.join()
        for q in [self.url_queue, self.html_queue, self.content_queue]:
            q.join()


if __name__ == '__main__':
    begin = time.time()
    spider = ProcessSpider()
    spider.run()
    times = time.time() - begin
    print("主进程结束")
    print(times)
