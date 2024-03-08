import requests
import time
import re
from tqdm import tqdm
import os
import random

"""
Demand Analysis:
    1.get and save all the pictures of daily rank in the date range you enter
    2.download all the pictures in your favorite
Technique Analysis:
    1.check severl html match test examples before generic code
    2.some pixiv's picture page's html texts have anti-crawler technique,which lead to 
      the lack of key information and can't realize the getWithPid() function!
"""
# environment variables
Proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890",
}
UserAgents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) Gecko/20100101 Firefox/61.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",
]
Headers = {
    "User-Agent": random.choice(UserAgents),
    "Referer": "https://www.pixiv.net/",
}
pictureSavePath = "D:/Pixiv/"


# get 50 pictures in one day's rankpage
def getRank():
    startDate, endDate = map(int, input("Enter the date range pls:").split())
    for date in range(startDate, endDate):  # detect and make path
        path = pictureSavePath + str(date) + "/"
        if os.path.exists(path) == False:
            os.makedirs(path)
            print(os.getcwd)
        os.chdir(path)
        rankPageUrl = "https://www.pixiv.net/ranking.php?mode=daily&date=" + str(date)  # get html text of rankpage
        rankPageResponse = requests.get(url=rankPageUrl, headers=Headers, proxies=Proxies)
        if rankPageResponse.status_code == 404:
            continue
        datePids = re.findall("https://i.pximg.net/c/240x480/img-master/img/([\d+/]*?)(?:_p0)?_master1200.jpg", rankPageResponse)  # match pictures' dates and pids
        titles = re.findall('data-title="(.*?)"', rankPageResponse)  # match titles
        for i in range(len(titles)):  # make titles legal
            titles[i] = titles[i].replace("/", "-")
            titles[i] = titles[i].replace("*", "-")
            titles[i] = titles[i].replace("|", "-")
        i = 0
        for datePid in datePids:  # start to deal with all pictures info
            i += 1
            pictureSourceUrl = "https://i.pximg.net/img-original/img/" + datePid + "_p0.png"
            format = ".png"
            while 1:  # anti-spider antier
                try:
                    response = requests.get(pictureSourceUrl, headers=Headers, proxies=Proxies, stream=True)
                    if response.status_code == 404:  # picture format detect
                        pictureSourceUrl = "https://i.pximg.net/img-original/img/" + datePid + "_p0.jpg"
                        format = ".jpg"
                        response = requests.get(url=pictureSourceUrl, headers=Headers, proxies=Proxies, stream=True)
                except:
                    print("A connection is rejected")
                    time.sleep(10)
                else:
                    break
            try:
                size = int(response.headers.get("content-length"))
            except:
                print("TypeError")
                size = 5000
            progressBar = tqdm(desc=f"[{i:0>2}/50]", total=size, unit="B", unit_scale=True)  # file write in
            with open(titles[i - 1] + format, "wb") as file:
                for chunk in response.iter_content(1024):
                    if chunk:
                        file.write(chunk)
                        progressBar.update(1024)
            progressBar.close()
    print("All done!")


while 1:
    sel = input("Enter your selection pls:")  # main menu
    if sel.upper() == "A":
        getRank()
    if sel.upper() == "G":
        exit
