# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os
import logging
import requests
from scrapy.pipelines.files import FilesPipeline
from scrapy import Request

DOWNLOAD_ROOT_PATH = r'C:\Users\Jven\Desktop\Music'


class DownloadPipeline(object):
    '''
    自定义音乐下载
    '''
    # def get_media_requests(self, item, info):
    #     logging.info('{}-{}'.format(item['song'],item['download']))
    #     if item['download']:
    #         yield Request(item['download'], meta={'item': item})
    
    # def file_path(self, request, response=None, info=None):
    #     item = response.meta['item']
    #     if not item:
    #         return
    #     directory = os.path.join(DOWNLOAD_ROOT_PATH, item['singer'], item['album'])
    #     if not os.path.isdir(directory):
    #         os.makedirs(directory)
    #     file_name = '{name}.{form}'.format(name=item['song'], form=item['file_format'])
    #     file_path = os.path.join(directory, file_name)
    #     logging.info('Song:{name} downloaded to {path}'.format(name=item['song'], path=file_path))
    #     return file_path

    def process_item(self, item, spider):
        # 下载音乐文件
        if not item['download']:
            logging.info('Song:{name} has no download url'.format(name=item['song']))
            return item
        # logging.info('Song:{name} download_url:{url}'.format(name=item['song'], url=item['download']))
        response = requests.get(item['download'],headers=item['cookie'])
        file_content = response.content
        directory = os.path.join(DOWNLOAD_ROOT_PATH, item['singer'], item['album'])
        if not os.path.isdir(directory):
            os.makedirs(directory)
        file_name = '{name}.{form}'.format(name=item['song'], form=item['file_format'])
        file_path = os.path.join(directory, file_name)
        with open(file=file_path, mode='wb') as f:
            f.write(file_content)
        logging.info('Song:{name} downloaded to {path}'.format(name=item['song'], path=file_path))
        
        # 储存歌词文件
        if not item['lyrics']:
            return item
        lyrics_file_name = '{name}.txt'.format(name=item['song'])
        lyrics_file_path = os.path.join(directory, lyrics_file_name)
        with open(file=lyrics_file_path, mode='w', encoding='utf-8') as f:
            f.write(item['lyrics'])
        logging.info('Lyrics:{name} downloaded to {path}'.format(name=item['song'], path=lyrics_file_path))

        return item
