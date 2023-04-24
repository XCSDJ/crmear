from threading import Thread
from time import sleep, ctime
import time
import multiprocessing as mp


def multcore():
    p1 = mp.Process(target=job, args=(task1, ))
    p2 = mp.Process(target=job, args=(task2, ))
    p3 = mp.Process(target=job, args=(task3, ))

    p1.start()
    p2.start()
    p3.start()
    
    p1.join()
    p2.join()
    p3.join()

def func(name, sec):
    print('---开始---', name )
    sleep(sec)
    print('***结束***', name)

# 创建 Thread 实例
t1 = Thread(target=func, args=('第一个线程', 6))
t2 = Thread(target=func, args=('第二个线程', 6))
p1 = mp.Process(target=func, args=('第一个进程', 3 ))
p2 = mp.Process(target=func, args=('第二个进程', 3))

# 启动线程运行
s1 = time.time()
t1.setDaemon(True)
t1.start()
t2.start()
# p1.start()
# p2.start()
# p1.join()
# p2.join()
print(1)

# 等待所有线程执行完毕

# t1.join()  # join() 等待线程终止，要不然一直挂起
# t2.join()

time.sleep(3)
print(2)
s2 =time.time()
print(f'总运行时间为{s2-s1}')

