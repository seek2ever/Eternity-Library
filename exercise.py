import time
from tqdm import tqdm, trange


for i in trange(100):
    time.sleep(0.01)

for i in tqdm(range(100), desc='processing'):
    time.sleep(0.05)

dic = ['a', 'b', 'c', 'd', 'e']
pbar = tqdm(dic)
for i in pbar:
    pbar.set_description('processing' + i)
    time.sleep(0.2)

print("hello")
