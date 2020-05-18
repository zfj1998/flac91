# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class SongItem(scrapy.Item):
    '''
    歌曲Item
    '''
    singer = scrapy.Field() #歌手
    album = scrapy.Field() #专辑
    song = scrapy.Field() #歌名
    page = scrapy.Field() #歌曲页面url
    lyrics = scrapy.Field() #歌词,文本格式
    download = scrapy.Field() #下载链接
    file_format = scrapy.Field() #文件格式
    cookie = scrapy.Field() # cookie jar用于pipeline下载