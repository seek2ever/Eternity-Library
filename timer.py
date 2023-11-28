"""
简单计时器功能，代码来自菜鸟教程（https://www.runoob.com/python3/python-simplestopwatch.html）
目前已知问题：按下Ctrl + C时无法停止计时，原因未知，只能人为停止运行代码
"""

import time

print('按下回车开始计时，按下 Ctrl + C 停止计时。')
while True:
    input("")  # 如果是 python 2.x 版本请使用 raw_input()
    starttime = time.time()
    print('开始')
    try:
        while True:
            print('\r计时: ', round(time.time() - starttime, 0), '秒', end="")
            time.sleep(1)
    except KeyboardInterrupt:
        print('\n结束')
        endtime = time.time()
        print('总共的时间为:', round(endtime - starttime, 2), 'secs')
        break
