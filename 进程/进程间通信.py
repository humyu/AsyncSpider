# -*- coding: utf-8 -*-
"""
multiprocessing 模块的 Queue 类 没有 join() 和 taskdone() 方法，
如果需要使用，那么使用一般队列 Queue.Queue 或者 multiprocessing 模块的 JoinableQueue 类
"""
import os
import random
import time
from multiprocessing import Process, Queue, Pipe


class QueueDemo:

    def __init__(self):
        self.q = Queue()

    # 写数据进程执行的代码:
    def write(self):
        print('Process to write: %s' % os.getpid())
        for value in ['A', 'B', 'C']:
            print('Put %s to queue...' % value)
            self.q.put(value)
            time.sleep(random.random())

    # 读数据进程执行的代码:
    def read(self):
        print('Process to read: %s' % os.getpid())
        while True:
            value = self.q.get(True)
            print('Get %s from queue.' % value)

    def run(self):
        pw = Process(target=self.write, args=())
        pr = Process(target=self.read, args=())
        # 启动子进程pw，写入:
        pw.start()
        # 启动子进程pr，读取:
        pr.start()
        # 等待pw结束:
        pw.join()
        # pr进程里是死循环，无法等待其结束，只能强行终止:
        pr.terminate()


class PipeDemo:
    def __init__(self):
        self.pipe = Pipe()

    def write(self):
        for i in range(3):
            print("send:%s" % i)
            # pipe[0] 发送
            self.pipe[0].send(i)
            time.sleep(1)

    def read(self):
        while True:
            # pipe[1] 接收
            print("rev:", self.pipe[1].recv())
            time.sleep(1)

    def run(self):
        p1 = Process(target=self.write, args=())
        p2 = Process(target=self.read, args=())
        p1.start()
        p2.start()
        p1.join()
        # p2.join()
        p2.terminate()


if __name__ == '__main__':
    # 1.测试 Queue 通信
    # 父进程创建Queue，并传给各个子进程：
    queue_demo = QueueDemo()
    queue_demo.run()

    # 2.测试 Pipe 通信
    pipe_demo = PipeDemo()
    pipe_demo.run()
