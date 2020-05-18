# -*- coding: utf-8 -*-
import re
import scrapy
import json
import logging
import ipdb
from selenium import webdriver
from scrapy.selector import Selector
from ..items import SongItem
from scrapy.http import Request
from scrapy import FormRequest

QUALITYS = ['flac', 'ape', '320mp3', '192aac', '192ogg', '128mp3', '96aac']
QUALITYS_FORMAT = {
    'flac': 'flac',
    'ape': 'ape',
    '192aac': 'aac',
    '192ogg': 'ogg',
    '320mp3': 'mp3',
    '128mp3': 'mp3',
    '96aac': 'aac'
} # 用于文件存储格式
SINGERS = {
    '周杰伦': '4558',
    'exo': '38578',
    '张震岳': '89',
    'aurora': '120734'
}
SINGER = 'exo' # 要爬取的歌手
SITE_URL = 'https://www.91flac.com'
SINGER_URL = SITE_URL + '/singer/{id}/song'
LOGIN_URL = SITE_URL + '/login'
EMAIL = '893298592@qq.com'
PASSWD = 'zfj893298592'

class SingerSpider(scrapy.Spider):
    '''
    下载给定歌手的所有歌曲
    '''
    name = 'singer'
    allowed_domains = ['91flac.com']
    start_url = SINGER_URL.format(id=SINGERS[SINGER])

    def start_requests(self):
        '''
        模拟登录
        '''
        logging.info('start_requests')
        yield Request(LOGIN_URL, callback=self.handle_login, meta={'cookiejar': 1})

    def handle_login(self, response):
        # ipdb.set_trace()
        token = Selector(response).xpath('//input[@name="_token"]/@value').extract()
        if len(token) == 0:
            return
        form_data = {
            '_token': token,
            'email': EMAIL,
            'password': PASSWD
        }
        logging.info('post user form')
        yield FormRequest(LOGIN_URL,
                    meta = {'cookiejar' : response.meta['cookiejar']}, 
                    formdata = form_data,
                    callback = self.after_login,
                    dont_filter = True
                )
    
    def after_login(self, response):
        logging.info('login succeed')
        yield Request(self.start_url, meta = {'cookiejar' : response.meta['cookiejar']}, callback=self.parse)

    def parse_headers(self, headers):
        new_headers = dict()
        for i in headers:
            key = i.decode('utf-8') if isinstance(i, bytes) else str(i)
            raw_value = headers[i]
            value = raw_value.decode('utf-8') if isinstance(raw_value, bytes) else str(i)
            new_headers[key] = value
        return new_headers
    
    def parse(self, response):
        '''
        爬取歌曲列表页
        '''
        logging.info('crawling {}'.format(response.request.url))
        selector = Selector(response)
        song_list = selector.xpath('//tbody/tr')
        next_page = selector.xpath('//ul[contains(@class,"pagination")]/li[2]/a/@href').extract() # 下一页的url

        if len(song_list) == 0:
            return
        # 进入每首歌曲的详情页
        for song_item in song_list:
            song = SongItem()
            raw_headers = response.request.headers
            song['cookie'] = self.parse_headers(raw_headers)
            song_name = song_item.xpath('td[1]/a/text()').extract()
            if not song_name:
                continue
            song['song'] = song_name[0]
            song['singer'] = SINGER
            # 存在歌曲没有专辑的情况
            song_album = song_item.xpath('td[2]/a/text()').extract()
            song['album'] = song_album[0] if song_album else ''
            song_page = song_item.xpath('td[1]/a/@href').extract()
            if not song_page:
                continue
            song['page'] = song_page[0]
            yield Request(song['page'], meta={'song': song, 'cookiejar' : response.meta['cookiejar']}, callback=self.parse_detail)

        # 爬取下一页
        if len(next_page) == 0:
            return
        next_url = next_page[0]
        yield Request(next_url, meta={'cookiejar' : response.meta['cookiejar']}, callback=self.parse)


    def parse_detail(self, response):
        '''
        爬取歌曲详情页爬取歌词
        '''
        song_item = response.meta['song']
        selector = Selector(response)
        csrf_token = selector.xpath('//meta[@name="csrf-token"]/@content').extract()
        if len(csrf_token) == 0:
            return
        csrf_token = csrf_token[0]
        lyrics = selector.xpath('//div[@id="lyric-original"]/text()').extract()
        song_item['lyrics'] = lyrics[0] if len(lyrics) > 0 else ''
        download_url = response.request.url + '/link'
        yield Request(
            download_url,
            callback=self.parse_download_link,
            meta={'song': song_item, 'cookiejar': response.meta['cookiejar']},
            headers={'X-CSRF-TOKEN': csrf_token},
            method='POST'
        )

    def parse_download_link(self, response):
        song_item = response.meta['song']
        quality_dict = json.loads(response.text)
        song_item['download'] = ''
        # 音质按QUALITYS中的顺序为优先级进行选择
        for quality in QUALITYS:
            try:
                size = quality_dict[quality]['size'] # 实地测试得到的格式
            except Exception:
                return
            if size == 0:
                continue
            link = quality_dict[quality]['link'] + '&from=download'
            song_item['download'] = link
            song_item['file_format'] = QUALITYS_FORMAT[quality]
            break
        logging.info("Song:{name} crawled".format(name=song_item['song']))
        yield song_item
            
