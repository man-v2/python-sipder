# -*-coding:utf8-*-
import json

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class DownloadHtml:
    def __init__(self, domain):
        self.session = requests.session()
        self.session.get(domain)
        self.new_data = set()

        self.mongo = MongoClient('127.0.0.1', 27017)
        self.mongo_db = self.mongo['lushishi']
        self.domain = domain

    def download_html(self, url):
        req = self.session.get(url)
        if req.encoding == 'ISO-8859-1':
            encodings = requests.utils.get_encodings_from_content(req.text)
            if encodings:
                encoding = encodings[0]
            else:
                encoding = req.apparent_encoding

            # encode_content = req.content.decode(encoding, 'replace').encode('utf-8', 'replace')
            global encode_content
            encode_content = req.content.decode(encoding, 'replace')  # 如果设置为replace，则会用?取代非法字符；
            return encode_content

    # 解析首页导航类别
    def parser_index_html(self, data):
        soup = BeautifulSoup(data, 'html.parser')
        links = soup.find_all('div', class_='navtop')
        types = dict()
        for link in links:
            for i in link.find_all('a'):
                cnt = i.get_text()
                print type(cnt)
                print cnt.encode('utf-8')
                # types['name'] = cnt.encode('utf-8')
                # types['url']  = 'http://www.lushishi30.com'+i.get('href')
                types[cnt.encode('utf-8')] = 'http://www.lushishi30.com'+i.get('href')
                # self.write_file('url.txt', cnt.encode('utf-8'))
        # json_data = json.dumps(types, ensure_ascii=False)
        # print json_data

        type_coll = self.mongo_db.type
        # type_coll.remove()
        type_coll.insert(types)

    def parser_detail_html(self, data, name):
        soup = BeautifulSoup(data, 'html.parser')
        # print soup.prettify()
        tags = soup.find_all('div', class_='content1 mtop')
        coll = self.mongo_db.video_detail

        for link in tags:
            for i in link.find_all('li'):
                cnt = {'type': name}
                print i.get_text
                # print i.contents[0]
                # 子标签查找： head->title
                imgs = i.find_all('img')
                for img in imgs:
                    print img.attrs['src'], img.attrs['alt']
                    cnt['name'] = img.attrs['alt'].encode('utf-8')
                    cnt['img'] = img.attrs['src']

                for p in i.find_all('p'):
                    # print p
                    content =  p.get_text()
                    if '主演' in content:
                        cnt['actor'] = content
                    elif '年份' in content:
                        cnt['year'] = content
                    elif '来源' in content:
                        cnt['source'] = content
                    elif '时间' in content:
                        cnt['time'] = content
                    elif '人气' in content:
                        cnt['popularity'] = content

                    for a in p.find_all('a'):
                        # print a['href'], a.get_text()
                        txt = a.get_text()
                        if '详情' in txt:
                            cnt['url'] = self.domain+a['href']
                        if '播放' in txt:
                            cnt['play'] = self.domain+a['href']

                coll.insert(cnt)

    # 分析页数
    def parse_page(self, data):
        soup = BeautifulSoup(data, 'html.parser')
        tags = soup.find_all('div', class_='page')
        page = None
        for link in tags:
            pages = link.find('span').get_text().split(' ')
            page = pages[1].split('/')
            page = page[1].replace('页', '')
        return page

    # 获取每个ytpe对应的页数
    def load_type(self):
        # type_coll = self.mongo_db.item
        # res = type_coll.find()
        item_coll = self.mongo_db.item
        # item_coll.remove()
        items = item_coll.find()
        for i in items:
            print i
        # return res[0]

    def update_item_download_url(self):
        video_detail = self.mongo_db.video_detail
        items = video_detail.find()
        for item in items:
            print item['name'], item['url']
            url = self.get_download_url(item['url'])
            if url is None:
                continue

            print item['_id'], url
            video_detail.update({'_id': item['_id']}, {'$set': {'down_url': url}})

    def get_download_url(self, url):
        # url = 'http://www.lushishi30.com/jr/50138'
        data = self.download_html(url)
        soup = BeautifulSoup(data, 'html.parser')
        v = soup.find(class_='down_url')
        if v is not None and len(v) > 0:
            down_url = v["value"]
            return down_url
        else:
            return None

    def write_file(self, path, data):
        with open(path, 'a') as f:
            f.write(data)

    def parse_player(self, data):
        soup = BeautifulSoup(data, 'html.parser')
        tags = soup.find_all('div', class_='listtxt')
        for link in tags:
            print link

    def download_video_detail(self):
        item_coll = self.mongo_db.item
        items = item_coll.find()
        for i in items:
            url = i['url']
            name = i['name']
            page = int(i['page'])

            print '\n spider %s' % name

            for p in range(page):
                print '爬第：%d页' % p
                if p > 1:
                    tmp_url = url + 'index' + str(p) + '.html'
                    print tmp_url
                    data = self.download_html(url)
                    self.parser_detail_html(data, name)
                elif p == 0:
                    data = self.download_html(url)
                    self.parser_detail_html(data, name)

    def download_single_type(self):
        # /sj/26777/player.html?26777-0-1
        data = self.download_html('http://www.lushishi30.com/sj/26777/player.html?26777-0-1')
        soup = BeautifulSoup(data, 'html.parser')
        print soup.prettify()
        # 详情页
        for row in soup.find_all('div', class_='contentList'):
            print row

        # 视频播放页
        for row in soup.find_all('div', class_='wrap'):
            print row

        # 视频真实地址
        for row in soup.find_all('div', id='player'):
            print row

    def run_js(self):
        resp = self.session.get('http://www.lushishi30.com/playdata/153/26777.js?11027.7')
        cnt = resp.content
        list = []

        if 'ckm3u8' in cnt:
            ckm = cnt.split(',')[1].replace('[', '').replace(']', '').replace('\'', '')
            ckm_url = ckm[ckm.find('$')+1:]
            list.append(ckm_url)
        elif 'xfplay' in cnt:
            xfplay = cnt.split(',')
            for row in xfplay:
                if '$xfplay' in row:
                    xfplay_url = row.replace('[', '').replace(']', '').replace('\'', '')
                    xf_url = xfplay_url[xfplay_url.find('$xfplay')+1:]
                    list.append(xf_url)
        print list
        return list

if __name__ == '__main__':
    obj = DownloadHtml('http://www.lushishi30.com')
    # obj.download_single_type()
    obj.run_js()