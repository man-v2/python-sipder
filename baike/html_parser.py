'''
Created on 2018-7-28

@author: Administrator
'''
from bs4 import BeautifulSoup
import re
import urlparse
import urllib
from lxml.html import html_parser


class HtmlParser(object):
    def _get_new_urls(self, page_url, soup):
        new_urls = set()
        links = soup.find_all('a', href=re.compile(r"/item/*"))
        for link in links:
            new_url = link['href']
            new_full_url = urlparse.urljoin(page_url, urllib.unquote(new_url.encode('gbk')))
            print new_full_url
            new_urls.add(new_full_url)
            
    def _get_new_data(self, page_url, soup):
            res_data = {'url': page_url}
            title_node = soup.find('dd', class_="lemmaWgt-lemmaTitle-title").find("h1")
            print title_node.get_text().encode('gbk')
            res_data['title'] = title_node.get_text()

            summary_node = soup.find('div', class_="lemma-summary").find('div', class_='para')
            # print (summary_node.get_text().replace('\n', '').replace(' ', ''))
            summary_txt = summary_node.get_text().replace('\n', '').replace(' ', '')
            res_data['summary'] = summary_txt
            
            return res_data
    
    def parse(self, page_url, html_cont):
        if page_url is None or html_cont is None:
            return
        
        soup = BeautifulSoup(html_cont, 'html.parser', from_encoding='utf-8')
        new_urls = self._get_new_urls(page_url, soup)
        new_data = self._get_new_data(page_url, soup)
        return new_urls, new_data