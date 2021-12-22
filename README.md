# AsynSpider

## 并发与并行
- 并发：指多个线程对应的多条指令被快速地轮换执行。 在宏观上看起来是同时执行的效果，但在微观上并不是同时执行的。
  因此同一时刻其实只有一个线程被执行。
- 并行：指同一时刻有多条指令在多个处理器上同时执行。不论从宏观还是微观，多个线程都是在同一时刻一起执行的。

> 但是由于 GIL 锁存在，python 里一个进程永远只能同一时刻执行一个线程 (拿到 GIL 的线程才能执行)，所以python多线程无法发挥多核并行的优势。

### 多线程
- 使用 threading模块中的 Thread 类创建线程，通过
```for _ in range(n): t = threading.Thread(target)```来创建多线程对象

### 线程池
- multiprocessing.dummy 所提供的 Pool 函数会返回一个 ThreadPool 的实例，该类是 Pool 的子类，它支持所有相同的方法调用但会使用一个工作线程池而非工作进程池
- 从Python3.2开始，标准库为我们提供了 concurrent.futures 模块，它提供了 ThreadPoolExecutor (线程池)和ProcessPoolExecutor (进程池)两个类。

