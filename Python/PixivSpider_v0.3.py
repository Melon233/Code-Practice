import requests
import time
import re
from tqdm import tqdm
import os
import random
import json

"""
Version 0.3:
    1.enhance code's robustness and anti-spider antier
Demand Analysis:
    1.get and save all the pictures of daily rank in the date range you enter
    2.download all the pictures in your favorite
    3.turn .zip file to .gif file

Technique Analysis:
    1.check severl html match test examples before generic code
    2.some pixiv's picture page's html texts have anti-crawler technique,which lead to 
      the lack of key information and can't realize the getWithPid() function!
      METHOD:sniff the ajax file which contains the key info of pictures
    

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
RankHeaders = {
    "User-Agent": random.choice(UserAgents),
    "Referer": "https://www.pixiv.net/",
}
FavoriteHeaders = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://www.pixiv.net/users/37791664/bookmarks/artworks?p=1",
    "Cookie": "first_visit_datetime_pc=2023-10-05%2020%3A50%3A17; p_ab_id=9; p_ab_id_2=3; p_ab_d_id=1946143945; yuid_b=MxQTJiA; PHPSESSID=37791664_26B8zAQWjymY31RuwjBX6wSx2iy5Wbj9; c_type=23; privacy_policy_notification=0; a_type=0; b_type=0; privacy_policy_agreement=6; login_ever=yes; _gcl_au=1.1.536641633.1702227112; _ga_MZ1NL4PHH0=GS1.1.1702393379.2.0.1702393379.0.0.0; adr_id=zWLd0rCkecQ2fYAGpD1EiEsJnsZJIjM0SlhTMxTke6FXPFxP; _im_vid=01HMJWRM3J4FN732RE8W2T71EW; FCNEC=%5B%5B%22AKsRol88PsS8TQr1sghwtu4pjiAbJca2wsAwXqRk3RHrHpvuMcDztwUWWgfxIldnYTHQjoPddQ2wQTNAxwtcjp_E1tp5z1cKyOWXdZ49xAL6LQqa_DGy9Gwc9OsZ5KTZwb18Qs5X0ZGnBpsGGDHFGqAOdeLR2-tbjg%3D%3D%22%5D%5D; __utmv=235335808.|2=login%20ever=yes=1^3=plan=normal=1^6=user_id=37791664=1^9=p_ab_id=9=1^10=p_ab_id_2=3=1^11=lang=zh=1; __utmz=235335808.1706950110.23.4.utmcsr=pixivision|utmccn=article_parts__pixiv_illust|utmcmd=9372; _pbjs_userid_consent_data=3524755945110770; _im_vid=01HMJWRM3J4FN732RE8W2T71EW; _pubcid=e59e1092-cd46-49cd-80d6-48d5f5ff03b5; _ga_1Q464JT0V2=GS1.1.1708529072.1.0.1708529072.60.0.0; cto_bundle=wRnhrl9wTWV3dTJvJTJGcUViVHlXWjJuNlBDdFdna0RmRzlmZmtrN1VabllrSElRb2JyYlpkZiUyQlRiWDFDSGYzY1hBQnZZVHBqdGRSakRQMUp5Mmx4TVhhOUlvU0JyaGlZdTFyaURXNWgxUmVYaG5HNTVaVE8xTGxPbGV2OW1KQjRwT0Z5M2hBMDRtOTlBR1FGcnF2RW93TzdxJTJGUXdxMlNGUFpHMGhDN1JNUXNUNHh6WmN6N2ZrcFhhQUtRJTJCRFdEVVN4amN2Y3haVzJOJTJCbUNReiUyQkhrb1RSQXlEczRqWFAzWlBTTHFqMEFOMmY3SSUyRlIlMkJ4RjRBSyUyQmRNbjJZNzJrWXdnREk1amVo; cto_bidid=PHM6HF9KemRHRk1ZRmwlMkZ2Rk00elpMWUJqOW9UVEYzbU5HSDFEMFp5ZjBrMUh6UTNyeG9XME5LTGRrVnJaYWRzRTUzaE5pNU41aFFhTiUyQm9DZWZZeGNXMnFLN2V0TkppcjNkRE9raTVZQkxlYUc2QjAlM0Q; QSI_S_ZN_5hF4My7Ad6VNNAi=v:0:0; _gid=GA1.2.697826064.1709656703; _im_uid.3929=i.FXwh4SBcTay5gMjU4JVmNA; krt.vis=IwPn3nGQmdE2E0B; pbjs_sharedId=5ff0b712-6e56-4266-aaf3-97a6c9e03b84; pbjs_sharedId_cst=zix7LPQsHA%3D%3D; wcl_proc=a%3D1013%26b%3D0%26c%3D1709913496622; _ga_4BWHLKCEGD=GS1.1.1709913496.1.0.1709913497.59.0.0; __utma=235335808.1043789910.1696506618.1709962101.1709963982.55; __utmc=235335808; cf_clearance=zPHOPOsdi.Y_4JKLXaJBp_kSQMlvSh7ZA4S78Mfle20-1709963982-1.0.1.1-nNlE.kjzkM.xVQogHaJJl6m.2Pjde1g1NJ.Gw0iQM8G3jCya7RlwOXwE3GqH_FgVCwMpq852.KddeIQ_r0lChg; __cf_bm=8IirphUKCVM6wF0Sy1tzLE4AkHRr5Ig7bwTfsz_V8A8-1709967673-1.0.1.1-sJt2IED6CMN8dPt0v4uBv2U.Cqlai4C7xElylcRWuq9ZRfMafkbgFfUI8xm.XPVpXrJzd9rJtkuQTkBvtlemUC48pstZHT_4noIvXKjAPOI; __utmt=1; _ga=GA1.1.1980431366.1696506622; __utmb=235335808.30.9.1709965040641; _ga_75BBYNYN9J=GS1.1.1709961236.54.1.1709969397.0.0.0",
}
Params = {"lang": "zh"}
pictureSavePath = "D:/Pixiv/"


def getWithInfo():
    return


# get 50 pictures in one day's rankpage
# form rankpage get picture info to spawn direct link to download picture
def getRank():
    startDate, endDate = map(int, input("[Enter the date range pls]:").split())
    for date in range(startDate, endDate):  # detect and make path
        path = pictureSavePath + str(date) + "/" + "Rank/"
        if os.path.exists(path) == False:
            os.makedirs(path)
            print(os.getcwd)
        os.chdir(path)
        rankPageUrl = "https://www.pixiv.net/ranking.php?mode=daily&date=" + str(date)  # get html text of rankpage
        rankPageResponse = requests.get(url=rankPageUrl, headers=RankHeaders, proxies=Proxies)
        if rankPageResponse.status_code != 200:
            continue
        rankPageHtml = rankPageResponse.text
        datePids = re.findall("https://i.pximg.net/c/240x480/img-master/img/([\d+/]*?)_p0_master1200.jpg", rankPageHtml)  # match pictures' dates and pids
        titles = re.findall('data-title="(.*?)"', rankPageHtml)  # match titles
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
                    response = requests.get(pictureSourceUrl, headers=RankHeaders, proxies=Proxies, stream=True)
                    if response.status_code == 404:  # picture format detect
                        pictureSourceUrl = "https://i.pximg.net/img-original/img/" + datePid + "_p0.jpg"
                        format = ".jpg"
                        response = requests.get(url=pictureSourceUrl, headers=RankHeaders, proxies=Proxies, stream=True)
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


# just for your favorite
# with the ajax json file contains the favorite pictures' info to spwan the source file direct link
def getFavorite():
    begin, end = map(int, input("[Enter the picture pos range you want(not include head)]:").split())
    offset = begin
    limit = end - begin
    path = pictureSavePath + "Favorite/"
    if os.path.exists(path) == False:
        os.makedirs(path)
    os.chdir(path)
    favoritePageAjaxUrl = f"https://www.pixiv.net/ajax/user/37791664/illusts/bookmarks?tag=&offset={offset}&limit={limit}&rest=show&lang=zh&version=59e08d0871b7c68569ebe89084d52eca68a1685d"
    favoritePageAjaxJson = requests.get(url=favoritePageAjaxUrl, headers=FavoriteHeaders, proxies=Proxies).text
    favoritePagePictureInfoList = json.loads(favoritePageAjaxJson)
    for info in favoritePagePictureInfoList["body"]["works"]:
        info["title"] = info["title"].replace("/", "-")
        info["title"] = info["title"].replace("|", "-")
        info["title"] = info["title"].replace("*", "-")
        prefix = f'{info["title"]}-{info["id"]}'
        if os.path.exists(prefix + ".png") | os.path.exists(prefix + ".jpg") | os.path.exists(prefix + ".zip"):
            print("skip")
            offset += 1
            continue
        datePid = re.search("https://i.pximg.net/c/250x250_80_a2/(custom-thumb|img-master)/img/(.*?)_", info["url"])
        while 1:  # anti-spider antier
            try:
                pictureSourceUrl = "https://i.pximg.net/img-original/img/" + datePid.group(2) + "_p0.png"
                format = ".png"
                response = requests.get(url=pictureSourceUrl, headers=FavoriteHeaders, proxies=Proxies, stream=True)
                if response.status_code == 404:  # picture format detect
                    pictureSourceUrl = "https://i.pximg.net/img-original/img/" + datePid.group(2) + "_p0.jpg"
                    format = ".jpg"
                    response = requests.get(url=pictureSourceUrl, headers=FavoriteHeaders, proxies=Proxies, stream=True)
                    if response.status_code == 404:
                        gifZipSourceUrl = "https://i.pximg.net/img-zip-ugoira/img/" + datePid.group(2) + "_ugoira600x600.zip"
                        format = ".zip"
                        response = requests.get(url=gifZipSourceUrl, headers=RankHeaders, proxies=Proxies, stream=True)
            except:
                print("A connection is rejected")
                time.sleep(10)
            else:
                break
        n = 0
        while 1:
            if format != ".zip":
                pictureSourceUrl = "https://i.pximg.net/img-original/img/" + datePid.group(2) + "_p" + f"{n}{format}"
                response = requests.get(url=pictureSourceUrl, headers=RankHeaders, proxies=Proxies)
                if response.status_code == 404:
                    break
            try:
                size = int(response.headers.get("content-length"))
            except:
                print("TypeError")
                size = 5000
            with open(info["title"] + f"{'_p'+ str(n) if n>0 else ''}" + "-" + info["id"] + format, "wb") as file:
                progressBar = tqdm(desc="[" + str(begin + 1) + "/" + str(end) + "][" + info["title"] + f"{'_p'+ str(n) if n>0 else ''}" + "]", total=size, unit="B", unit_scale=True)  # file write in
                for chunk in response.iter_content(1024):
                    if chunk:
                        file.write(chunk)
                        progressBar.update(1024)
                progressBar.close()
            if format == ".zip":
                break
            n += 1
        begin += 1
    print("All done...")


def urlDownload():
    url = "https://www.pixiv.net/ajax/user/37791664/illusts/bookmarks?tag=&offset=0&limit=100&rest=show&lang=zh&version=59e08d0871b7c68569ebe89084d52eca68a1685d"
    js = requests.get(url=url, headers=FavoriteHeaders, proxies=Proxies, params=Params).text
    dict = json.loads(js)
    print(dict)  # should be print in exclusive terminal


while 1:
    print("A.Get rank pictures in 50th")
    print("B:Get Favorite pictures")
    print("H.Get file with url")
    print("G.Exit")
    sel = input("Enter your selection pls:")  # main menu
    if sel.upper() == "A":
        getRank()
    if sel.upper() == "B":
        getFavorite()
    if sel.upper() == "H":
        urlDownload()
    if sel.upper() == "G":
        break
