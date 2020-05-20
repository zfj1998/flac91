# -*- coding: utf-8 -*-
import scrapy
import os
import logging
from scrapy.utils.project import get_project_settings

settings = get_project_settings()
ROOT_PATH = settings.get('DOWNLOAD_ROOT_PATH')
QUALITYS = settings.get('QUALITYS')
QUALITYS_FORMAT = settings.get('QUALITYS_FORMAT') # 用于文件存储格式

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

    def trim_file_name(self, name):
        illegal = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
        for i in illegal:
            name = name.replace(i, '')
        if name and name[-1] == '.':
            name = name + 'et al' # windows文件夹末尾的.会自动消失
        return name

    def get_directory(self):
        directory = os.path.join(
            ROOT_PATH,
            self['singer'],
            self.trim_file_name(self['album'])
        )
        return directory

    def get_song_path(self):
        directory = self.get_directory()
        file_name = '{name}.{form}'.format(
            name=self.trim_file_name(self['song']),
            form=self['file_format']
        )
        song_path = os.path.join(directory, file_name)
        return song_path
    
    def get_lyrics_path(self):
        directory = self.get_directory()
        lyrics_file_name = '{name}.txt'.format(
            name=self.trim_file_name(self['song'])
        )
        lyrics_file_path = os.path.join(directory, lyrics_file_name)
        return lyrics_file_path

    def check_directory(self):
        directory = self.get_directory()
        if not os.path.isdir(directory):
            try:
                os.makedirs(directory)
            except Exception as e:
                logging.error('Error while create directory {}'.format(e))
                return False
        return True

    def song_file_existed(self):
        result = False
        for f in QUALITYS:
            self['file_format'] = QUALITYS_FORMAT[f]
            file_path = self.get_song_path()
            result = os.path.exists(file_path)
            if result:
                break
        if result:
            logging.info('Song:{name} already exists at {path}'.format(name=self['song'], path=file_path))
        return result
    
    def lyrics_file_existed(self):
        lyrics_path = self.get_lyrics_path()
        result = os.path.exists(lyrics_path)
        if result:
            logging.info('Lyrics:{name} already exists at {path}'.format(name=self['song'], path=lyrics_path))
        return result
    