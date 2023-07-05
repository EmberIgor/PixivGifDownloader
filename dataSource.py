import os
import sys
import uuid
import zipfile
import imageio.v2 as imageio
from configparser import ConfigParser
from pixivpy3 import *
import requests

proxySetting = {
    'need_proxy': False,
    'proxy': 'http://localhost:10809',
}
config = ConfigParser()
userCookie = ''
userHeaders = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0",
    'Accept': "application/json",
    'Accept-Language': "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    'Accept-Encoding': "gzip, deflate, br",
    'x-user-id': '66516855',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'Sec-Fetch-Mode',
    'Sec-Fetch-Site': 'same-origin',
    'Referer': 'https://www.pixiv.net/artworks/98733409',
    'Connection': 'keep-alive',
    'Cookie': userCookie,
    'TE': 'trailers'
}

_REFRESH_TOKEN = "TPJ-ZcaLoUvJ80YoD9uszO_vvGnQ02LEcRexnqjGad4"
api = AppPixivAPI()


def exitProcedures():
    print("按任意键退出")
    input()
    sys.exit(0)


def cut(obj, sec):
    return [obj[i:i + sec] for i in range(0, len(obj), sec)]


def readConfig():
    print("读取配置文件")
    global config
    global userCookie
    global userHeaders
    global proxySetting
    config.read("./PixivGifDownloader.config", encoding="utf-8")
    try:
        userCookie = str(config.get("User", "Cookie"))
        userHeaders['Cookie'] = userCookie
        proxySetting['need_proxy'] = config.getboolean("Proxy", "NeedProxy")
        proxySetting['proxy'] = config.get("Proxy", "Proxy")
    except KeyError:
        print("读取配置文件失败！")
        exitProcedures()


def downLoadGif(uid, file_path="./pixivOutput"):
    global userCookie
    global userHeaders
    global proxySetting
    proxy = {
        'http': proxySetting['proxy'],
        'https': proxySetting['proxy'],
    } if proxySetting['need_proxy'] else None
    GiFrameListRes = requests.get(f"https://www.pixiv.net/ajax/illust/{uid}/ugoira_meta?lang=zh",
                                  headers=userHeaders, proxies=proxy).json()
    originalSrc = GiFrameListRes['body']['originalSrc'].replace('i.pximg.net', 'i.pixiv.re')
    originalZip = requests.get(originalSrc).content
    file_name = uuid.uuid1()
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    if not os.path.exists(f"{file_path}/temp"):
        os.makedirs(f"{file_path}/temp")
    del_list = os.listdir(f"{file_path}/temp")
    for f in del_list:
        temp_file_path = os.path.join(f"{file_path}/temp", f)
        if os.path.isfile(temp_file_path):
            os.remove(temp_file_path)
    with open(f"{file_path}/temp/{file_name}.zip", "wb+") as fp:
        fp.write(originalZip)
    temp_file_list = []
    zipo = zipfile.ZipFile(f"{file_path}/temp/{file_name}.zip", "r")
    for file in zipo.namelist():
        temp_file_list.append(os.path.join(f"{file_path}/temp", file))
        zipo.extract(file, f"{file_path}/temp")
    zipo.close()
    image_data = []
    for file in temp_file_list:
        image_data.append(imageio.imread(file))
    imageio.mimsave(os.path.join(file_path, str(file_name) + ".gif"), image_data, "GIF",
                    duration=GiFrameListRes['body']['frames'][0]['delay'] / 1000)
    for file in temp_file_list:
        os.remove(file)
    os.remove(f"{file_path}/temp/{file_name}.zip")
    os.rmdir(f"{file_path}/temp")


def getAuthorsWorks(uid, onlyGif=True):
    global userHeaders
    global api
    api.auth(refresh_token=_REFRESH_TOKEN)
    proxy = {
        'http': proxySetting['proxy'],
        'https': proxySetting['proxy'],
    } if proxySetting['need_proxy'] else None
    worksListRes = requests.get("https://www.pixiv.net/ajax/user/" + str(uid) + "/profile/all",
                                headers=userHeaders, proxies=proxy).json()
    authorName = f"{uid}-" \
                 f"{api.user_detail(1665866)['user']['name']}"
    worksList = []
    worksDetailList = {}
    for workId in worksListRes['body']['illusts'].keys():
        worksList.append(workId)
    workPages = cut(worksList, 50)
    for worksListTemp in workPages:
        worksListStr = ''
        for workId in worksListTemp:
            worksListStr = worksListStr + 'ids%5B%5D=' + workId + '&'
        worksListStr = worksListStr.strip(
            '&') + "&work_category=illustManga&is_first_page=0&lang=zh&version=f34012b3c44270c199e863e1638c058a9865e798"
        worksDetailListRes = requests.get(
            "https://www.pixiv.net/ajax/user/" + str(uid) + "/profile/illusts?" + worksListStr,
            headers=userHeaders, proxies=proxy).json()
        worksDetailList.update(worksDetailListRes['body']['works'])
    if onlyGif:
        gifList = []
        for workId in worksDetailList:
            if worksDetailList[workId]['illustType'] == 2:
                gifList.append(workId)
        return {
            'author': authorName,
            'works': gifList
        }
    else:
        return {
            'author': authorName,
            'works': worksList
        }


def readDownloadList():
    download_list = []
    if os.path.exists("PixivDownloadList.txt"):
        with open("PixivDownloadList.txt", "r") as f:
            for line in f.readlines():
                line = line.strip('\n')
                download_list.append(line)
            f.close()
    else:
        with open("./PixivDownloadList.txt", 'w', encoding='utf-8') as f:
            f.close()
        print("未检测到下载列表，已在程序目录下创建PixivDownloadList.txt文件")
        exitProcedures()
    return download_list
