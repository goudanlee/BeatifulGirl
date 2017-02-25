#-*- coding:utf-8 -*-
from bs4 import BeautifulSoup
from BeatifulGirl.Downloader import Downloader
from urllib import request
import urllib
import os
import queue
import time
import threading

class Analyzer:
    def __init__(self):
        self.basepath = 'G:\\ScrapyData\\'
        self.D = Downloader()
        self.imgurl_queue = queue.Queue()
        self.seen = set()
        self.seed_url = 'http://m.mzitu.com'
        self.max_threads = 10
        self.SLEEP_TIME = 10
        self.crawl_queue = [self.seed_url]

    def link_crawler(self):
        # 使用set集合来去重
        seen = set(self.crawl_queue)
        while True:
            try:
                url = self.crawl_queue.pop()
            except IndexError:
                # crawl_queue is empty
                break
            else:
                html = self.D.download(url)
                #获取该页面的主题链接
                title_links = self.get_title_link(html)
                for title_link in title_links:
                     self.thread_get_image(title_link)
                    # 下载完一个主题后随机暂停1至10秒，避免过高频率影响服务器以及被屏蔽
                    # time.sleep(random.randint(1,10))
                # 获取下一个有效的页面链接
                link = self.get_page_link(html)
                if link:
                    if link not in seen:
                        seen.add(link)
                        self.crawl_queue.append(link)
                else:
                    break

    def get_page_link(self, html):
        # 获取下页的分页地址
        link = ''
        bs = BeautifulSoup(html,'lxml')
        prevnext = bs.find('div', attrs={'class':'prev-next more'}).find('a', attrs={'class:','button radius'})
        if prevnext:
            link = bs.find('a', attrs={'class':'button radius'}).get('href')
            print(link)
        # 返回下页链接地址
        return link

    def get_title_link(self, html):
        # 获取所有可用的主题链接
        links = []
        bs = BeautifulSoup(html,'lxml')
        titile_links = bs.findAll('h2')
        for link in titile_links:
            link = link.find('a').get('href')
            links.append(link)
        return links

    def thread_get_image(self, url):
        # 通过主题链接读取并保存所有的图片
        html = self.D.download(url)
        bs = BeautifulSoup(html,'lxml')
        # 通过主题链接创建路径以及读取主题下的所有图片,这里采用title作为文件夹名称
        title = bs.find('h2', attrs={'class':'blog-title'}).text.replace('?','_').replace('/','_')
        path = self.basepath + title
        self.mkdir(path)
        # 获取主题下的总页数
        page_info = bs.find('span',attrs={'class':'prev-next-page'}).text
        pages = page_info[page_info.index('/')+1:page_info.index('页')]
        #创建图片链接地址队列
        for page in range(1,int(pages)):
            seed_url = url + '/' + str(page)
            html = self.D.download(seed_url)
            bs = BeautifulSoup(html,'lxml')
            img_url = bs.find('div', attrs={'id':'content'}).find('img').get('src')
            jpg_name = img_url[img_url.rfind('/') + 1:]
            req = request.Request(img_url)
            write = urllib.request.urlopen(req)
            fw = open(path+'/%s'%jpg_name,'wb')
            fw.write(write.read())
            fw.close()

    def mkdir(self, path):
        path = path.strip()
        #判断路径是否存在
        isExist = os.path.exists(path)
        if not isExist:
            os.mkdir(path)
            return True
        else:
            print('目录已存在')
            return False


a = Analyzer()
# D = Downloader()
# html = D.download('http://m.mzitu.com')
a.link_crawler()

