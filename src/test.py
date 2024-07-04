from math import e
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import re
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import threading
from queue import Queue
task_queue = Queue()
# 创建一个Chrome WebDriver实例
chrome_options = Options()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--disable-dev-shm-usage')
# chrome_options.add_argument('--ignore-certificate-errors')
# chrome_options.add_argument('--ignore-ssl-errors')
chrome_options.add_experimental_option("detach",True)

ch = [
        "凤凰卫视",
        "浙江卫视"
]
for channel in ch:
    task_queue.put(channel)
driver = webdriver.Chrome(options = chrome_options)
# 使用WebDriver访问网页
driver.get('http://tonkiang.us')  # 将网址替换为你要访问的网页地址
time.sleep(1)
channelListNew = []
# 关闭WebDriver
#driver.quit()
# 定义工作线程函数
def worker():
    while True:
        try:
            # 从队列中获取一个任务
            url = task_queue.get()
            # 获取网页内容
            search_box = driver.find_element(By.ID, "search")
            search_box.clear()
            print(search_box)
            search_box.send_keys(url)
            driver.find_element(By.NAME, "Submit").click()
            channelList = driver.find_elements(By.CLASS_NAME,"resultplus")
            print(channelList)
            for channel in channelList:
                                print(channel.get_attribute('outerHTML'))
                                soup = BeautifulSoup(channel.get_attribute('outerHTML'), 'html.parser')
                                # 方法二：从<img>标签的onclick事件中获取链接
                                img_tag = soup.find('img', title="copy to clip")
                                if img_tag: 
                                    link_from_img_onclick = img_tag['onclick'].split('"')[1]  # 提取onclick事件中的链接
                                    result1 = "{},{}".format(url,link_from_img_onclick)
                                    print(result1)
                                    channelListNew.append(result1)
                                    break
                                else:
                                    print("Channel Name Not Found")
             # 标记任务完成
            task_queue.task_done()       
        except task_queue.Empty:
            break  # 如果队列为空，退出循环

# 创建多个工作线程
num_threads = task_queue.qsize()
for _ in range(1):
    t = threading.Thread(target=worker, daemon=True)  # 将工作线程设置为守护线程
    t.start()


# 等待所有任务完成
task_queue.join()    
# 关闭WebDriver
driver.quit()         
def channel_key(channel_name):
    match = re.search(r'\d+', channel_name)
    if match:
        return int(match.group())
    else:
        return float('inf')  # 返回一个无穷大的数字作为关键字

# 对频道进行排序
sorted_res = sorted(channelListNew, key=lambda x: x.split(',')[0].strip())
print(channelListNew)
# sorted_res =  ch.sort(key=lambda x: channel_key(x[0]))
with open("itvlistNew.txt", 'w', encoding='utf-8') as file:
    channel_counters = {}
    for result in sorted_res:
        file.write(f"{result}\n")
