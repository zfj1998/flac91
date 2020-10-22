# -*- coding: utf-8 -*-

BOT_NAME = 'flac91'

SPIDER_MODULES = ['flac91.spiders']
NEWSPIDER_MODULE = 'flac91.spiders'

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 1

DOWNLOAD_DELAY = 2

DOWNLOADER_MIDDLEWARES = {
    'flac91.middlewares.MyUserAgentMiddleware': 400,
    # 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware' : None,
    # 'scrapy_cloudflare_middleware.middlewares.CloudFlareMiddleware': 560
}

LOG_LEVEL = 'INFO'
LOG_FILE = 'spider.log'


ITEM_PIPELINES = {
    'flac91.pipelines.DownloadPipeline': 300,
}

# HTTPERROR_ALLOWED_CODES = [419]

DOWNLOAD_ROOT_PATH = r'C:\Users\Jven\Desktop\Music'

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