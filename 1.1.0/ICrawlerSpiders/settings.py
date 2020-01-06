# -*- coding: utf-8 -*-

BOT_NAME = 'ICrawlerSpiders'
#LOG_LEVEL = 'ERROR'
#LOG_ENABLED = False


SPIDER_MODULES = ['ICrawlerSpiders.Spiders']
NEWSPIDER_MODULE = 'ICrawlerSpiders.Spiders'

LOG_LEVEL = 'ERROR'
DNS_TIMEOUT = 30
DOWNLOAD_TIMEOUT = 100
# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'PacteraSpdiers (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.5
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 4
CONCURRENT_REQUESTS_PER_IP = 4

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'PacteraSpdiers.middlewares.PacteraspdiersSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   'ICrawlerSpiders.middlewares.ProxyMiddleware': 543,
   'ICrawlerSpiders.middlewares.DLMiddleware': 544,
   'ICrawlerSpiders.middlewares.DownLoadsMiddleware': 545,
   # 'ICrawlerSpiders.middlewares.FundscrapyDownloaderMiddleware': 546,
   # 'ICrawlerSpiders.middlewares.TestMiddleware': 547,
}

EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
 }

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    'PacteraSpdiers.pipelines.PacteraspdiersPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 2
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 10
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
# 如果启用，Scrapy将记录所有在request(Cookie 请求头)发送的cookies及response接收到的cookies(Set-Cookie 接收头)。
COOKIES_DEBUG = True

CLOSESPIDER_TIMEOUT = 43200  # 设置爬虫定时关闭时间

# 直接返回页面（html）的实体
ENCRYPTION_BY_HTML_ENTITY = [
    'ZX_GWDT_PFYH_XWDT',

]
# ENTITY_CODE 使用接口请求不使用IP 代理的, 在中间件中
ENCRYPTION_BY_API_AND_NO_IP_ENTITY = [
    'ZTB_ZGCGZB',
    'CRMJPFX_WD_PFYH_CITY',
    'CRMJPFX_WD_PFYH_PROVINCE',
    'CRMJPFX_WD_PAGE',
    'CRMJPFX_WD_PFYH',
    'CRMJPFX_YXHD_PFYH',

]

# 在 pyppeteer 中也不使用代理
ENCRYPTION_NOT_IP_ENTITY = [
                            'ZTB_ZGCGZB',
                            'CRMJPFX_WD_PFYH_CITY',
                            'CRMJPFX_WD_PFYH_PROVINCE',
                            'CRMJPFX_WD_PAGE',
                            'CRMJPFX_WD_PFYH',
                            'CRMJPFX_YXHD_PFYH',
                            'CRMJPFX_WD_PFYH_CITY',
]

# 需要中间件单独处理的 且 通过 pyppeteer 获取数据的 ENTITY_CODE
ENCRYPTION_ENTITY = ['JRCP_XYK_WAK_ALL',
                     # 'ZX_ZCGG_ZGRMYH_ZYGFXWD',
                     'ZX_ZCGG_YBH_JGDT',
                     'ZX_ZCGG_YBH_GGTZ',
                     'ZX_ZCGG_BJH_ZCFG',
                     'ZX_ZCGG_YJH_GGTZ',
                     'JRCP_LCCP_PFYH_GW_ALL',
                     'B_JRCP_LCCP_PFYH_GW_ALL',
                     # 'ZX_GWDT_PFYH_XWDT',
                     # 'ZX_ZCGG_ZGRMYH_TFS',
                     'JRCP_LCCP_ZGGSYH_GW_ALL',
                     'B_JRCP_LCCP_ZGGSYH_GW_ALL',
                     'JRCP_LCCP_ZGGDYH_GW_ALL',
                     'B_JRCP_LCCP_ZGGDYH_GW_ALL',
                     'WD_TY_PFYH_PROVINCE',
                     'WD_TY_PFYH_CITY',
                     'WD_TY_ZGJSYH_GW_PAGE',
                     'WD_TY_PFYH_GW_ALL',
                     'WD_SH_SQ_DZDPSC',
                     'SPDBORGANIZE',
                     'WD_JZ_DKFZGH_DKGS',
                     'ZTB_ZGRMYHJZCGZX',
                     'ZTB_ZGCGZB',
                     'CRMJPFX_WD_PFYH_CITY',
                     'CRMJPFX_WD_JSYH_PAGE',
                     'CRMJPFX_WD_JSYH',
                     'CRMJPFX_YXHD_PFYH',
                     ]

ENCRYPTION_ENTITY.extend(ENCRYPTION_BY_API_AND_NO_IP_ENTITY)

# 通过Firefox 直接获取html
ENCRYPTION_BY_HTML_FIREFOX = [
        'ZX_ZCGG_ZGRMYH_TFS2',
        'ZX_ZCGG_ZGRMYH_ZYGFXWD',
        'ZX_ZCGG_ZGRMYH_TFS',
        'ZX_CJXW_GJJRJG_GJSWZJ_GDSW',
        'ZX_CJXW_GJJRJG_GJSWZJ_SWYW',
        'ZX_CJXW_GJJRJG_GJSWZJ_XWFBH',
        'ZX_CJXW_GJJRJG_GJSWZJ_ZBGG',
        'ZX_CJXW_GJJRJG_GJSWZJ_ZCJD',
        'ZX_CJXW_GJJRJG_GJSWZJ_ZXWJ',
        'ZTB_NXZBW'
]

# 通过Firefox 获取cookies 再获取数据
ENCRYPTION_BY_API_FIREFOX = [
                     'CCBPage',
                     'CCBPage2',
                     'CCBPage3',
                     'CCBORGANIZE',
                     'CCBORGANIZE2',
                     'CCBORGANIZE3',
]


