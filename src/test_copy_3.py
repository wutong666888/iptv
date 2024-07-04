
import re
import requests
from random import choice
from bs4 import BeautifulSoup
import threading
from queue import Queue
# 发送HTTP GET请求
response = requests.get('http://tonkiang.us')
ch = []
channelsUrl = []
# 线程安全的队列，用于存储下载任务
task_queue = Queue()

# 检查请求是否成功（响应状态码为200表示成功）
if response.status_code == 200:
    
    ip_match = re.search(r'href="hoteliptv\.php\s*s=(\d+\.\d+\.\d+\.\d+)"', response.text)
    ip_pattern = re.compile(r'href="[^"]+s=(\d+\.\d+\.\d+\.\d+)"')
    match = ip_pattern.findall(response.text)
    urls = []
    if match:
        #urls_all = match.group()
        ip_addresses = [match for match in match]
        # urls = list(set(urls_all))  # 去重得到唯一的URL列表
        urls = set(ip_addresses)  # 去重得到唯一的URL列表
        
        for url in urls:  
            task_queue.put(url)
            
            
else:
    print("请求失败，状态码：{response.status_code}")





# 线程安全的列表，用于存储结果
results = []

error_channels = []
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    # 更多 User-Agent ...
]

# 定义工作线程函数
def worker():
    while True:
        try:
            x_urls = []
            # 从队列中获取一个任务
            url = task_queue.get()
            print(f"url{url}")
            # 对urls进行处理，ip第四位修改为1，并去重
            url = url.strip()
            response1 = requests.post('http://tonkiang.us/hoteliptv.php?s='+url)
            # print(response1.text)
            ip_pattern = re.compile(r'href="hotellist.html\s*s=([\d.:]+)"')
            pattern = r'href=\'hotellist.html\?s=([\d.:]+)\''


            # 使用findall方法提取所有匹配的IP地址及端口号
            ip_matches = re.findall(pattern, response1.text)
            # ip_pattern = r'href="hotellist.html\s*s=([\d.:]+)"'
            # ip_matches = ip_pattern.findall(response1.text)
            ip_port_from_href_hotel = [match for match in ip_matches]
            for te in ip_matches: 
                x_urls.append(te)
            print(f"内容{x_urls}")
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": choice(user_agents),
                "Host": "tonkiang.us",
                "Referer": "http://tonkiang.us/hotellist.html?s=125.76.174.199%3A8888&Submit=+"
            }

            for url in x_urls: 
                result = "http://tonkiang.us/alllist.php?s={}&c=false".format(url)
                #print(result)
                response3 = requests.get(result, headers=headers)
                print(response3.text)
                soup = BeautifulSoup(response3.text, 'html.parser')
                channels = soup.find_all('div', class_='result')
                for channel in channels:

                # 在每个结果div中查找频道名称
                    channel_name_div = channel.find('div', style='float: left;')
                    channel_name = channel_name_div.text.strip() if channel_name_div else "Channel Name Not Found"
                    
                    # 查找并提取URL
                    onclick_attrs = channel.find_all('img', onclick=True)
                    for onclick_attr in onclick_attrs:
                        url_start = onclick_attr['onclick'].find('"') + 1
                        url_end = onclick_attr['onclick'].rfind('"')
                        url = onclick_attr['onclick'][url_start:url_end]
                        result1 = "{},{}".format(channel_name,url)
                        print(result1)

                        ch.append(result1)
                        #print("频道名称:", result1)
                        # #break  # 假设每个result只对应一个有效URL
                        # try:
                        #     response = requests.get(url, timeout=1)
                        #     if response.status_code == 200:
                        #         file_size = 0
                        #         start_time = time.time()
                        #         # 多获取的视频数据进行12秒钟限制
                        #         response = requests.get(url, stream=True, timeout=1)
                        #         for chunk in response.iter_content(chunk_size=1024):
                        #             if chunk:
                        #                 file_size += len(chunk)
                        #         response.close()
                        #         end_time = time.time()
                        #         response_time = end_time - start_time
                        #         if response_time >=12:
                        #             file_size = 0
                        #         download_speed = file_size / response_time / 1024
                        #         normalized_speed =download_speed / 1024  # 将速率从kB/s转换为MB/s
                        #         if normalized_speed >= 1:
                        #             if file_size >= 12000000:
                        #                 result = channel_name, url, f"{normalized_speed:.3f} MB/s"
                        #                 results.append(result)
                        #                 numberx = (len(results) + len(error_channels)) / len(channels) * 100
                        #                 print(f"可用频道：{len(results)} , 网速：{normalized_speed:.3f} MB/s , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")
                        #             else:
                        #                 error_channel = channel_name, url
                        #                 error_channels.append(error_channel)
                        #                 numberx = (len(results) + len(error_channels)) / len(channels) * 100
                        #                 print(f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} , 网速：{normalized_speed:.3f} MB/s , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")
                        #         else:
                        #             error_channel = channel_name, url
                        #             error_channels.append(error_channel)
                        #             numberx = (len(results) + len(error_channels)) / len(channels) * 100
                        #             print(f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} , 网速：{normalized_speed:.3f} MB/s , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")
                        #     else:
                        #         error_channel = channel_name, url
                        #         error_channels.append(error_channel)
                        #         numberx = (len(results) + len(error_channels)) / len(channels) * 100
                        #         print(
                        #             f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")
                        # except:
                        #     error_channel = channel_name, url
                        #     error_channels.append(error_channel)
                        #     numberx = (len(results) + len(error_channels)) / len(channels) * 100
                        #     print(f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")
                    
                #print(result)
             # 标记任务完成
            task_queue.task_done()       
        except task_queue.Empty:
            break  # 如果队列为空，退出循环

       


# 创建多个工作线程
num_threads = task_queue.qsize()
for _ in range(num_threads):
    t = threading.Thread(target=worker, daemon=True)  # 将工作线程设置为守护线程
    t.start()


# 等待所有任务完成
task_queue.join()             
def channel_key(channel_name):
    match = re.search(r'\d+', channel_name)
    if match:
        return int(match.group())
    else:
        return float('inf')  # 返回一个无穷大的数字作为关键字

# 对频道进行排序
sorted_res = sorted(ch, key=lambda x: x.split(',')[0].strip())
print(ch)
# sorted_res =  ch.sort(key=lambda x: channel_key(x[0]))
with open("./src/itvlist.txt", 'w', encoding='utf-8') as file:
    channel_counters = {}
    for result in sorted_res:
        file.write(f"{result}\n")
