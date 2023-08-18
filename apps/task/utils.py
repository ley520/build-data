# coding=utf-8
# data：2023/2/23-20:31
from concurrent.futures.thread import ThreadPoolExecutor


class MyThreadPool:
    def __int__(self):
        self.execute = ThreadPoolExecutor(5)

    def __del__(self):
        self.execute.shutdown()


threadPool = MyThreadPool()
