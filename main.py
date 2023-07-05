import os
import re
import sys

import dataSource
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

progress = Progress(
    SpinnerColumn(),
    "{task.description}",
    BarColumn(),
    MofNCompleteColumn(),
    "•[progress.percentage]{task.percentage:>3.1f}%",
    "•已用时间：",
    TimeElapsedColumn(),
    "•预计剩余时间：",
    TimeRemainingColumn(),
)


def downLoadAuthorAllWorks(uid, onlyGif=True):
    global progress
    downloadList = []
    worksList = dataSource.getAuthorsWorks(uid, onlyGif)
    authorDownloadBar = progress.add_task(description=f"[blue]作者{worksList['author']}作品下载进度：[/blue]",
                                          total=len(worksList['works']))
    progress.start()
    for i in r'\/:*?"<>|':
        worksList['author'] = worksList['author'].replace(i, ' ')
    if not os.path.exists(f"./pixivOutput/{worksList['author']}"):
        os.makedirs(f"./pixivOutput/{worksList['author']}")
    if not os.path.exists(f"./pixivOutput/{worksList['author']}/DownloadList.txt"):
        with open(f"./pixivOutput/{worksList['author']}/DownloadList.txt", 'w', encoding='utf-8') as f_txt:
            for workIDItem in worksList['works']:
                f_txt.write(workIDItem + "\n")
            f_txt.close()
    with open(f"./pixivOutput/{worksList['author']}/DownloadList.txt", "r") as f_txt:
        for line in f_txt.readlines():
            line = line.strip('\n')
            downloadList.append(line)
        f_txt.close()
    newDownloadList = downloadList
    for workDownloadIndex in range(len(downloadList)):
        workDownloadID = downloadList[workDownloadIndex]
        if workDownloadID.isdigit():
            dataSource.downLoadGif(workDownloadID, f"./pixivOutput/{worksList['author']}")
            newDownloadList[workDownloadIndex] = f"[已下载]{workDownloadID}"
            with open(f"./pixivOutput/{worksList['author']}/DownloadList.txt", "w") as f_txt:
                for i in newDownloadList:
                    f_txt.write(i + "\n")
                f_txt.close()
        progress.update(task_id=authorDownloadBar, advance=1)
    progress.remove_task(authorDownloadBar)


def writeDownloadList(download_list):
    with open("PixivDownloadList.txt", "w") as f_txt:
        f_txt.truncate()
        for i in download_list:
            f_txt.write(i + "\n")
        f_txt.close()


def downLoadByList():
    global progress
    downLoadList = dataSource.readDownloadList()
    newDownLoadList = downLoadList
    listTotalBar = progress.add_task(description="[red]列表下载进度：[/red]", total=len(downLoadList))
    progress.start()
    for authorIdIndex in range(len(downLoadList)):
        authorId = downLoadList[authorIdIndex]
        if authorId.isdigit():
            downLoadAuthorAllWorks(authorId)
            newDownLoadList[authorIdIndex] = f"[已下载]{authorId}"
        progress.update(task_id=listTotalBar, advance=1)
    # progress.remove_task(listTotalBar)
    writeDownloadList(newDownLoadList)


if __name__ == '__main__':
    if os.path.exists("./PixivGifDownloader.config"):
        dataSource.readConfig()
        print("配置文件读取成功")
    else:
        print("未检测到配置文件，正在为您创建配置文件")
        default_config_str = "[Proxy]\n#使用代理填写True，否则为False\nNeedProxy = True\n#代理地址\nProxy = " \
                             "http://localhost:10809\n[User]\nCookie =\n "
        with open("./PixivGifDownloader.config", 'w', encoding='utf-8') as f:
            f.write(default_config_str)
            f.close()
        print("配置文件创建成功，请在配置文件中填写配置，然后重新运行程序")
        print("配置文件路径：", os.path.abspath("./PixivGifDownloader.config"))
        print("按任意键退出")
        input()
        sys.exit(0)
    print("请选择要执行的能力：")
    print("1.根据下载列表下载文件")
    print("2.单独下载指定作者的作品")
    print("3.单独下载某个作品")
    print("4.退出")
    while True:
        choice = input("请输入序号：")
        if choice == "1":
            os.system("cls")
            downLoadByList()
            print("下载完成！按任意键退出")
            input()
            sys.exit(0)
        elif choice == "2":
            os.system("cls")
            print("请输入作者ID：")
            authorID = input()
            os.system("cls")
            downLoadAuthorAllWorks(authorID)
            print("下载完成！按任意键退出")
            input()
            sys.exit(0)
        elif choice == "3":
            os.system("cls")
            print("请输入作品ID：")
            workID = input()
            print("作品下载中……")
            dataSource.downLoadGif(workID)
            print("下载完成！按任意键退出")
            input()
            sys.exit(0)
        elif choice == "4":
            print("退出")
            sys.exit(0)
        else:
            print("输入错误，请重新输入")
