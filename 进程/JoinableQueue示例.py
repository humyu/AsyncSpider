# -*- coding: utf-8 -*-
from multiprocessing import Process, JoinableQueue


class JQ:
    def __init__(self):
        self.url_queue = JoinableQueue()
        self.page_queue = JoinableQueue()

    def fun1(self):
        for i in range(8):
            url = f"http://www.example.com/{i}"
            print(url)
            self.url_queue.put(url)

    def fun2(self):
        while True:
            url = self.url_queue.get()
            page = f"page: {url}"
            print(page)
            self.page_queue.put(page)
            self.url_queue.task_done()

    def fun3(self):
        while True:
            page = self.page_queue.get()
            content = f"输出 content==>{page}"
            print(content)
            self.page_queue.task_done()

    def run(self):
        # 多个生产者进程
        p = Process(target=self.fun1)
        # 既是消费者，又是生产者
        c_p = Process(target=self.fun2)
        # 消费者进程
        c = Process(target=self.fun3)
        # 启动生产者进程
        p.start()
        # 把消费者设为守护进程
        c_p.daemon = True
        c.daemon = True
        c_p.start()
        c.start()

        # 等待生产者生产完毕
        p.join()
        # join()方法：生产者将使用此方法进行阻塞，直到队列中所有项目均被处理
        for element in [self.url_queue, self.page_queue]:
            element.join()


if __name__ == '__main__':
    spider = JQ()
    spider.run()
    print('主进程结束')
