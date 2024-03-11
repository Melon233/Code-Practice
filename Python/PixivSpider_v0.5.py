import requests
import re
from tqdm import tqdm
import os
import json
import zipfile
from PIL import Image

"""
Version 0.5:
    1.enhance code's robustness and anti-spider antier
Demand Analysis:
    1.get and save all the pictures of daily rank in the date range you enter
    2.download all the pictures in your favorite
    3.turn .zip file to .gif file
    4.optimize the performance

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
FileHeaders = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://www.pixiv.net/",
}
HtmlHeaders = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://www.pixiv.net/",  # users/37791664/bookmarks/artworks",
    "Cookie": "first_visit_datetime_pc=2023-10-05%2020%3A50%3A17; p_ab_id=9; p_ab_id_2=3; p_ab_d_id=1946143945; yuid_b=MxQTJiA; PHPSESSID=37791664_26B8zAQWjymY31RuwjBX6wSx2iy5Wbj9; c_type=23; privacy_policy_notification=0; a_type=0; b_type=0; privacy_policy_agreement=6; login_ever=yes; _gcl_au=1.1.536641633.1702227112; _ga_MZ1NL4PHH0=GS1.1.1702393379.2.0.1702393379.0.0.0; adr_id=zWLd0rCkecQ2fYAGpD1EiEsJnsZJIjM0SlhTMxTke6FXPFxP; _im_vid=01HMJWRM3J4FN732RE8W2T71EW; FCNEC=%5B%5B%22AKsRol88PsS8TQr1sghwtu4pjiAbJca2wsAwXqRk3RHrHpvuMcDztwUWWgfxIldnYTHQjoPddQ2wQTNAxwtcjp_E1tp5z1cKyOWXdZ49xAL6LQqa_DGy9Gwc9OsZ5KTZwb18Qs5X0ZGnBpsGGDHFGqAOdeLR2-tbjg%3D%3D%22%5D%5D; __utmv=235335808.|2=login%20ever=yes=1^3=plan=normal=1^6=user_id=37791664=1^9=p_ab_id=9=1^10=p_ab_id_2=3=1^11=lang=zh=1; __utmz=235335808.1706950110.23.4.utmcsr=pixivision|utmccn=article_parts__pixiv_illust|utmcmd=9372; _pbjs_userid_consent_data=3524755945110770; _im_vid=01HMJWRM3J4FN732RE8W2T71EW; _pubcid=e59e1092-cd46-49cd-80d6-48d5f5ff03b5; _ga_1Q464JT0V2=GS1.1.1708529072.1.0.1708529072.60.0.0; cto_bundle=wRnhrl9wTWV3dTJvJTJGcUViVHlXWjJuNlBDdFdna0RmRzlmZmtrN1VabllrSElRb2JyYlpkZiUyQlRiWDFDSGYzY1hBQnZZVHBqdGRSakRQMUp5Mmx4TVhhOUlvU0JyaGlZdTFyaURXNWgxUmVYaG5HNTVaVE8xTGxPbGV2OW1KQjRwT0Z5M2hBMDRtOTlBR1FGcnF2RW93TzdxJTJGUXdxMlNGUFpHMGhDN1JNUXNUNHh6WmN6N2ZrcFhhQUtRJTJCRFdEVVN4amN2Y3haVzJOJTJCbUNReiUyQkhrb1RSQXlEczRqWFAzWlBTTHFqMEFOMmY3SSUyRlIlMkJ4RjRBSyUyQmRNbjJZNzJrWXdnREk1amVo; cto_bidid=PHM6HF9KemRHRk1ZRmwlMkZ2Rk00elpMWUJqOW9UVEYzbU5HSDFEMFp5ZjBrMUh6UTNyeG9XME5LTGRrVnJaYWRzRTUzaE5pNU41aFFhTiUyQm9DZWZZeGNXMnFLN2V0TkppcjNkRE9raTVZQkxlYUc2QjAlM0Q; QSI_S_ZN_5hF4My7Ad6VNNAi=v:0:0; _gid=GA1.2.697826064.1709656703; _im_uid.3929=i.FXwh4SBcTay5gMjU4JVmNA; krt.vis=IwPn3nGQmdE2E0B; pbjs_sharedId=5ff0b712-6e56-4266-aaf3-97a6c9e03b84; pbjs_sharedId_cst=zix7LPQsHA%3D%3D; wcl_proc=a%3D1013%26b%3D0%26c%3D1709913496622; _ga_4BWHLKCEGD=GS1.1.1709913496.1.0.1709913497.59.0.0; __utma=235335808.1043789910.1696506618.1709962101.1709963982.55; __utmc=235335808; cf_clearance=zPHOPOsdi.Y_4JKLXaJBp_kSQMlvSh7ZA4S78Mfle20-1709963982-1.0.1.1-nNlE.kjzkM.xVQogHaJJl6m.2Pjde1g1NJ.Gw0iQM8G3jCya7RlwOXwE3GqH_FgVCwMpq852.KddeIQ_r0lChg; __cf_bm=8IirphUKCVM6wF0Sy1tzLE4AkHRr5Ig7bwTfsz_V8A8-1709967673-1.0.1.1-sJt2IED6CMN8dPt0v4uBv2U.Cqlai4C7xElylcRWuq9ZRfMafkbgFfUI8xm.XPVpXrJzd9rJtkuQTkBvtlemUC48pstZHT_4noIvXKjAPOI; __utmt=1; _ga=GA1.1.1980431366.1696506622; __utmb=235335808.30.9.1709965040641; _ga_75BBYNYN9J=GS1.1.1709961236.54.1.1709969397.0.0.0",
}
pictureSavePath = "D:/Pixiv/"


# get 50 pictures in one day's rankpages
# from rankpage get picture info to spawn direct link to download picture
def getRank():
    startDate, endDate = map(int, input("[Enter the date range pls]:").split())
    for date in range(startDate, endDate):  # detect and make path
        # module 1
        path = f"{pictureSavePath}/Rank/{date}"
        if os.path.exists(path) == False:
            os.makedirs(path)
        else:
            print("skip")
            continue
        os.chdir(path)
        # module 2
        rankPageUrl = f"https://www.pixiv.net/ranking.php?mode=daily&date={date}"  # get html text of rankpage
        rankPageResponse = requests.get(url=rankPageUrl, headers=HtmlHeaders, proxies=Proxies)
        if rankPageResponse.status_code != 200:  # detect legal or not
            continue
        rankPageHtml = rankPageResponse.text
        pids = re.findall("https://i.pximg.net/c/240x480/img-master/img/.*?/(\d+)_p0_master1200.jpg", rankPageHtml)  # match pictures' dates and pids
        titles = re.findall('data-title="(.*?)"', rankPageHtml)  # match titles
        for i in range(len(titles)):  # make titles legal
            titles[i] = re.sub(r'[\/:*?"<>|]', "-", titles[i])
        i = 0
        # module 3
        for pid in pids:
            i += 1
            print(f"[{i}/{50}]")
            urlDownload(pid, titles[i - 1])
    print("All done √")


# just for your favorite
# with the ajax json file contains the favorite pictures' info to spwan the source file direct link
def getFavorite():
    # module 1
    begin, end = map(int, input("[Enter the picture pos range you want(not include head)]:").split())  # scan data
    offset = begin
    limit = end - begin
    end = end - begin
    begin = 0
    path = pictureSavePath + "Favorite/"  # root path
    if os.path.exists(path) == False:  # path detect
        os.makedirs(path)
    os.chdir(path)
    # module 2
    favoritePageAjaxUrl = f"https://www.pixiv.net/ajax/user/37791664/illusts/bookmarks?tag=&offset={offset}&limit={limit}&rest=show&lang=zh&version=59e08d0871b7c68569ebe89084d52eca68a1685d"
    favoritePageAjaxJson = requests.get(url=favoritePageAjaxUrl, headers=HtmlHeaders, proxies=Proxies).text
    favoritePagePictureInfoDict = json.loads(favoritePageAjaxJson)  # pictures dict datas
    for info in favoritePagePictureInfoDict["body"]["works"]:  # legalize title
        info["title"] = re.sub(r'[\/:*?"<>|]', "-", info["title"])
        prefix = f'{info["title"]}-{info["id"]}'  # filename
        if os.path.exists(prefix + ".png") | os.path.exists(prefix + ".jpg") | os.path.exists(prefix + ".gif"):
            print("skip")  # file existence detect
            begin += 1
            continue
        begin += 1
        print(f"[{begin}/{end}]")
        # module 3
        urlDownload(info["id"], info["title"])
    print("All done √")


def urlDownload(pid, title):
    # module 1
    picturePageUrl = f"https://www.pixiv.net/artworks/{pid}"
    picturePageHtml = requests.get(url=picturePageUrl, headers=HtmlHeaders, proxies=Proxies).text
    pictureFileUrl = re.search('original":"(.*?)"', picturePageHtml).group(1)
    pageCount = int(re.search('pageCount":(\d+),"bookmarkCount', picturePageHtml).group(1))
    prefix = pictureFileUrl[:-5]
    format = pictureFileUrl[-4:]
    # module 2
    for i in range(pageCount):
        if pictureFileUrl[-11:-5] == "ugoira":
            format = ".zip"
            pictureFileUrl = f'https://i.pximg.net/img-zip-ugoira/img/{re.search("https://i.pximg.net/img-original/img/(.*?)_ugoira0.jpg",pictureFileUrl).group(1)}_ugoira1920x1080.zip'
        else:
            pictureFileUrl = f"{prefix}{i}{format}"
        pictureFile = requests.get(url=pictureFileUrl, headers=FileHeaders, proxies=Proxies, stream=True)
        try:
            size = int(pictureFile.headers.get("Content-Length"))
        except:
            size = 1000
        # module 3
        postfix = f"{'_p'+ str(i) if i>0 else ''}"
        fileName = f"{title}{postfix}-{pid}{format}"
        with open(fileName, "wb") as file:
            progressDesc = f"[{title}{postfix}]"
            with tqdm(desc=progressDesc, total=size, unit="B", unit_scale=True) as progressBar:  # file write in
                for chunk in pictureFile.iter_content(1024):
                    if chunk:
                        file.write(chunk)
                        progressBar.update(1024)
    if format == ".zip":
        transZIPtoGIF(fileName, fileName.replace(".zip", ".gif"), pid)


def transZIPtoGIF(zipPath, gifPath, id):
    durationAjaxUrl = f"https://www.pixiv.net/ajax/illust/{id}/ugoira_meta?lang=zh&version=59e08d0871b7c68569ebe89084d52eca68a1685d"
    durationAjaxJson = requests.get(url=durationAjaxUrl, headers=HtmlHeaders, proxies=Proxies).text
    durationInfoDict = json.loads(durationAjaxJson)
    delay = durationInfoDict["body"]["frames"][0]["delay"]
    images = []
    with zipfile.ZipFile(zipPath, "r") as zip:
        for jpgZip in zip.filelist:
            with zip.open(jpgZip) as file:
                with Image.open(file, "r") as image:
                    image = image.convert("RGB")
                    images.append(image)
    print("Transforming...")
    images[0].save(gifPath, save_all=True, append_images=images[1:], duration=delay, loop=0)
    os.remove(zipPath)
    print("Completed")


def test():
    info = "https://i.pximg.net/img-zip-ugoira/img/2023/02/04/00/00/02/105059613_ugoira1920x1080.zip"
    response = requests.get(url=info, headers=FileHeaders, proxies=Proxies, verify=False)
    with open("1.zip", "wb") as file:
        file.write(response.content)
    images = []
    with zipfile.ZipFile("1.zip", "r") as zip:
        for jpgZip in zip.filelist:
            with zip.open(jpgZip) as file:
                with Image.open(file, "r") as image:
                    image = image.convert("RGB")
                    images.append(image)
    print("Transforming...")
    images[0].save("1.gif", save_all=True, append_images=images[1:], duration=58, loop=0)
    os.remove("1.zip")
    print("Completed")


while 1:
    print("A.Get rank pictures in 50th")
    print("B:Get Favorite pictures")
    print("G.Exit")
    sel = input("Enter your selection pls:")  # main menu
    if sel.upper() == "A":
        getRank()
    if sel.upper() == "B":
        getFavorite()
    if sel.upper() == "G":
        break
