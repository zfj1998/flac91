import re
import scrapy
import ipdb
import logging
import re
from scrapy.selector import Selector
from scrapy.http import Request

SINGER_FILE = 'singer.txt'

class SingerSpider(scrapy.Spider):
    '''
    爬取所有歌手
    '''
    name = 'singer'
    allowed_domains = ['91flac.com']
    start_url = 'https://www.91flac.com/singer_list'

    def start_requests(self):
        logging.info('start request')
        yield Request(self.start_url, callback=self.parse)

    def save(self, singers_dict):
        logging.info('saving')
        with open(SINGER_FILE, mode='a', encoding='utf-8') as f:
            lines = []
            for key in singers_dict:
                value = singers_dict[key]
                lines.append('\'{}\': \'{}\',\n'.format(key, value))
            f.writelines(lines)

    def parse(self, response):
        logging.info('crawling {}'.format(response.request.url))
        selector = Selector(response)
        singer_list = selector.xpath('//a[@class="stretched-link"]')
        singers_dict = dict()
        for singer in singer_list:
            name = singer.xpath('text()').extract()
            if not name:
                continue
            name = name[0]
            link = singer.xpath('@href').extract()
            if not link:
                continue
            link = link[0]
            code = link.split('/')[-1]
            singers_dict[name] = code
        self.save(singers_dict)

        # 爬取下一页
        next_page = selector.xpath('//ul[contains(@class,"pagination")]/li[2]/a/@href').extract() # 下一页的url
        if len(next_page) == 0:
            return
        next_url = next_page[0]
        yield Request(next_url, callback=self.parse)
