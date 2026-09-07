import threading
import time


def cpu_heavy_work(n):
	"""模拟 CPU 密集计算。"""
	total = 0
	for i in range(n):
		total += i * i
	return total


N = 50_000_000

# 单线程：约 3.2 秒
start = time.perf_counter()
cpu_heavy_work(N)
cpu_heavy_work(N)
print(f"单线程耗时: {time.perf_counter() - start:.2f} 秒")
# 输出：单线程耗时：6.41 秒

# 多线程：约 6.4 秒（没有并行加速，GIL 限制了执行）
start = time.perf_counter()
t1 = threading.Thread(target=cpu_heavy_work, args=(N,))
t2 = threading.Thread(target=cpu_heavy_work, args=(N,))
t1.start()
t2.start()
t1.join()
t2.join()
print(f"多线程耗时: {time.perf_counter() - start:.2f} 秒")
# 输出：多线程耗时：6.38 秒（几乎没有加速）