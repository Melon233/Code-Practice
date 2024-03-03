import requests
import time
import re
from tqdm import tqdm
import os
import random
proxies = {
    "http":"http://127.0.0.1:7890",
    "https":"http://127.0.0.1:7890",
}
userAgents = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
              "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
              "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
              "Mozilla/5.0 (Windows NT 10.0; WOW64) Gecko/20100101 Firefox/61.0",
              "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
              "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
              "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
              "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
              "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",]
headers={"User-Agent":random.choice(userAgents),
         "Referer": "https://www.pixiv.net/",}
startDate, endDate = map(int,input("请输入日期范围").split())
#startDate=20240212;endDate=20240213
data = list(range(100))
for date in range(startDate,endDate):
    url1='https://www.pixiv.net/ranking.php?mode=daily&date='+str(date)
    html1=requests.get(url=url1,headers=headers,proxies=proxies).text
    url2s=re.findall('https://i.pximg.net/c/240x480/img-master/img/([\d+/]*?)(?:_p0)?_master1200.jpg',html1)
    datas=re.findall('data-title="(.*?)" data-user-name="(.*?)"',html1)
    i=0
    for url2 in url2s:
        i+=1
        url3='https://i.pximg.net/img-original/img/'+url2+'_p0.png'
        format='.png'
        response=requests.get(url3,headers=headers,proxies=proxies,stream=True)
        if(response.status_code==404):
            url3='https://i.pximg.net/img-original/img/'+url2+'_p0.jpg'
            format='.jpg'
            response=requests.get(url3,headers=headers,proxies=proxies,stream=True)
        size=int(response.headers.get('content-length'))
        progressBar=tqdm(desc=f"[{i:0>5}]",total=size,unit='B',unit_scale=True)
        with open(datas[i-1][0]+format,"wb") as file:
            for chunk in response.iter_content(1024):
                if chunk:
                    file.write(chunk)
                    progressBar.update(1024)  
        
                        
                
    
