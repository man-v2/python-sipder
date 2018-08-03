#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
'''
Created on 2018年7月29日

@author: Administrator
'''
import urllib2
import urllib
from bs4 import BeautifulSoup
import re

def test():
    url = 'https://baike.baidu.com/item/Python/407313'
    response = urllib2.urlopen(url)
    cont = response.read()
    soup = BeautifulSoup(cont, 'html.parser', from_encoding='utf-8')

    parse_html(soup)

    links = soup.find_all('a', href=re.compile(r"/item/*"))
    link_dict = dict()
    for link in links:
    #     print link    hb  
        new_url = link['href']
        link_dict['link'] = new_url
#         print new_url
#         print urllib.unquote(new_url.encode('gbk'))

def parse_html(soup):
    title_node = soup.find('dd', class_="lemmaWgt-lemmaTitle-title").find("h1")
    # print title_node.get_text().encode('gbk')

    summary_node = soup.find('div', class_="lemma-summary").find('div', class_='para')
    print (summary_node.get_text().replace('\n', '').replace(' ', ''))

def test_urldecode():
    s='/item/%E7%99%BE%E5%BA%A6%E7%99%BE%E7%A7%91%EF%BC%9A%E6%9C%AC%E4%BA%BA%E8%AF%8D%E6%9D%A1%E7%BC%96%E8%BE%91%E6%9C%8D%E5%8A%A1/22442459'
    s=urllib.unquote(s)
    print(s)
    
# test_urldecode()
test()