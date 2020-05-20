# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import logging
import requests
from scrapy.pipelines.files import FilesPipeline
from scrapy import Request

class DownloadPipeline(object):
    '''
    自定义音乐下载
    '''
    def process_item(self, item, spider):
        # 下载音乐文件
        if not item['download']:
            logging.info('Song:{name}-{album} has no download url'.format(name=item['song'], album=item['album']))
            return item
        #下载文件
        response = requests.get(item['download'],headers=item['cookie'])
        file_content = response.content
        
        if not item.check_directory():
            return item

        file_path = item.get_song_path()
        with open(file=file_path, mode='wb') as f:
            f.write(file_content)
        logging.info('Song:{name} downloaded to {path}'.format(name=item['song'], path=file_path))
        
        # 储存歌词文件
        if not item['lyrics']:
            return item
        lyrics_file_path = item.get_lyrics_path()
        if not item.lyrics_file_existed():
            with open(file=lyrics_file_path, mode='w', encoding='utf-8') as f:
                f.write(item['lyrics'])
            logging.info('Lyrics:{name} downloaded to {path}'.format(name=item['song'], path=lyrics_file_path))

        return item
