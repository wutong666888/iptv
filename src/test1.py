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
chrome_options.add_argument('--headless')
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
driver = webdriver.Chrome(options = chrome_options)
# 使用WebDriver访问网页
driver.get('http://tonkiang.us')  # 将网址替换为你要访问的网页地址
driver.implicitly_wait(30)

channelListNew = []
span_a_list = driver.find_elements(By.CSS_SELECTOR, "span.sh a")
for span in span_a_list:
    task_queue.put(span)
# 关闭WebDriver
#driver.quit()
# 定义工作线程函数
def worker():
    while True:
        try:
            # 从队列中获取一个任务
            url = task_queue.get()
            driver1 = webdriver.Chrome(options = chrome_options)
            # 获取完整的URL
            full_url = url.get_attribute('href')
            # url.click()
            driver1.get(full_url)
            # time.sleep(4)
            driver1.implicitly_wait(30)

            a_tags = driver1.find_elements(By.XPATH, '//a[contains(@href, "hotellist.html")]')

            newly_launched_a_tags = []
            for a_tag in a_tags:
                # print(a_tag.get_attribute('outerHTML'))
                # if  a_tag.get_attribute('outerHTML').find("新上线") != -1:
                newly_launched_a_tags.append(a_tag)

            # 输出新上线的`<a>`标签信息
            for tag in newly_launched_a_tags:
                print("Found a new launched link: ", tag.get_attribute('href'))
            if  newly_launched_a_tags:    
                newly_launched_a_tags[0].click()
            channelList = driver1.find_elements(By.CSS_SELECTOR,"div.channel a")
            print(channelList)
            for channel in channelList:
                                print(channel.get_attribute('outerHTML'))
                                soup = BeautifulSoup(channel.get_attribute('outerHTML'), 'html.parser')
                                # 找到a标签
                                a_tag = soup.find('a')

                                
                                if a_tag: 
                                    # 提取a标签的href属性
                                    href_value = a_tag['href']

                                    # 找到a标签下style="float: left;"的div标签
                                    div_tag = a_tag.find('div', style="float: left;")
                                    # 提取div标签中的文本
                                    div_text = div_tag.text.strip()
                                    result1 = "{},{}".format(div_text,href_value)
                                    print(result1)
                                    channelListNew.append(result1)
                                    break
                                else:
                                    print("Channel Name Not Found")
            driver1.quit() 
             # 标记任务完成
            task_queue.task_done()    
              
        except task_queue.Empty:
            driver1.quit()  
            break  # 如果队列为空，退出循环

# 创建多个工作线程
num_threads = task_queue.qsize()
for _ in range(2):
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
with open("itvlistNew1.txt", 'w', encoding='utf-8') as file:
    channel_counters = {}
    for result in sorted_res:
        file.write(f"{result}\n")
