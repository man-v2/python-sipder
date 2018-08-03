#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
'''
Created on 2018��7��28��
@desc: 下載器 
@author: Administrator
'''
import urllib2

class HtmlDownloader(object):
    
    
    def download(self, url):
        if url is None:
            return None
        
        response = urllib2.urlopen(url)
        
        if response.getcode() != 200:
            return None
        
        return response.read()
    
    



