# Scrapy settings for AER_Scrapy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "AER_Scrapy"

SPIDER_MODULES = ["AER_Scrapy.spiders"]
NEWSPIDER_MODULE = "AER_Scrapy.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "AER_Scrapy (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = True
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "AER_Scrapy.middlewares.AerScrapySpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "AER_Scrapy.middlewares.AerScrapyDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    "AER_Scrapy.pipelines.AerScrapyPipeline": 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# File name to use for logging output. 
# If None, standard error will be used.
# LOG_FILE = None
# LOG_FILE = 'log_output.txt'

# If False, the log file specified with LOG_FILE will be overwritten 
# (discarding the output from previous runs, if any).
# LOG_FILE_APPEND = True

# Whether to enable logging.
# LOG_ENABLED = True

# The encoding to use for logging.
# LOG_ENCODING = 'utf-8'

# Minimum level to log. Available levels are: 
# CRITICAL, ERROR, WARNING, INFO, DEBUG. For more info see Logging.
# LOG_LEVEL = 'DEBUG'

# String for formatting log messages. Refer to the Python 
# logging documentation for the whole list of available placeholders.
# LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'

# String for formatting date/time, expansion of the 
# %(asctime)s placeholder in LOG_FORMAT. Refer to the Python 
# datetime documentation for the whole list of available directives.
# LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'

# If True, all standard output (and error) of your process will be 
# redirected to the log. For example if you print('hello') it will 
# appear in the Scrapy log.
# LOG_STDOUT = False
LOG_STDOUT = True

# If True, the logs will just contain the root path. If it is set to 
# False then it displays the component responsible for the log output
# LOG_SHORT_NAMES = False