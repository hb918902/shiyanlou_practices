#! usr/bin/python3
# coding:utf-8

from selenium import webdriver
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as TreadPool
import urllib.request
import re
import os


def makedir(path):
    isExists = os.path.exists(path)
    if not isExists:
        print("新建文件夹"+path)
        os.mkdir(path)
    else:
        print(path+'文件夹已经创建')


def getperMM(MMURL,MMpath):
    """MMMURL 个人链接地址  MMpath保存路径"""
    html = urllib.request.urlopen(MMURL)
    page = html.read()
    html.close()
    soup = BeautifulSoup(page,"lxml")
    MMimages = soup.find_all('img')
    cnt = 1
    for MMimage in MMimages:
        if os.path.exists(MMpath+"/"+str(cnt)+'.jpg'):
            cnt += 1
            print('*!',end='')
        else:
            try:
                urllib.request.urlretrieve("https:"+MMimage['src'].lstrip(),MMpath+"/"+str(cnt)+'.jpg')
                print(str(cnt),end=";")
                cnt += 1
            except (urllib.request.URLError,KeyError) as e:
                print(e)
                continue
            # if cnt >5:
            #     break
    print(os.linesep+MMpath+' 已完成!')


def index():
    driver = webdriver.Firefox(executable_path='/usr/bin/firefox') # 使用firefox浏览器
    driver.get("https://mm.taobao.com/search_tstar_model.htm?")
    bsobj = BeautifulSoup(driver.page_source,'lxml')
    if not os.path.exists(os.getcwd()+'/'+'mm.txt'):
        fp = open('mm.txt','w+')
        fp.write(driver.find_element_by_id('J_GirlsList').text)
        fp.close()
        print("get MM's index")
    # MMsinfoUrl链接地址  imagesUrl封面图片
    MMsinfoUrl = bsobj.findAll("a",{"href":re.compile("\/\/.*\.htm\?(userId=)\d*")})
    # imagesUrl = bsobj.findAll("img",{"data-ks-lazyload":re.compile(".*\.jpg")})
    fp = open('mm.txt')
    items = fp.readlines()
    fp.flush()
    fp.close()
    driver.close()
    # print(items)
    # 获取MM信息，存入content1
    content1 = []
    for i  in range(0,len(items),3):
        content1.append([items[i].strip(os.linesep),items[i+1].strip(os.linesep)])
    # 获取MM个人主页地址，存入content2
    content2 = []
    for MMurl in MMsinfoUrl:
        content2.append(MMurl["href"])
    # print(content2)
    contents = [[a,b] for a,b in zip(content1,content2)]
    return contents


def content_process(content):
    print("MM's name is :"+content[0][0]+" with "+content[0][1])
    perMMurl = "https:"+content[1]  # 创建链接地址path
    path = os.getcwd()+'/'+content[0][0]
    makedir(path)
    getperMM(perMMurl,path)


if __name__ == "__main__":
    tpool = TreadPool(30)
    tpool.map(content_process,index())
    tpool.close()
    print('Well Done')








