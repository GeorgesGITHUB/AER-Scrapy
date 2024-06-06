# debug print
def dprint(*texts):
        print('****************************************')
        string=''
        for text in texts:
             string+=str(text)+' '
        print(string)
        print('****************************************')

import scrapy
from scrapy.utils.response import open_in_browser
from scrapy import FormRequest

class PlotPlanSpider(scrapy.Spider):
    name = "plotplan"

    def start_requests(self):
        dprint('start_requests')
        urls = [
            "https://dds.aer.ca/iar_query/FindApplications.aspx",
        ]

        headers = {
            # 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            # 'Accept-Encoding':'gzip, deflate, br, zstd',
            # 'Accept-Language':'en-CA,en;q=0.9,fr;q=0.8',
            # 'Cache-Control':'no-cache',
            # # 'Cookie':'ApplicationGatewayAffinityCORS=cdd4d7efe17b7ee004905df3f26c25d0; ApplicationGatewayAffinity=cdd4d7efe17b7ee004905df3f26c25d0; ASP.NET_SessionId=umtjobvfbq14yvjve1msdtar; ASLBSA=0003c515ff7a1f7e7618fdb6e230a6fae1ec5f3175921df43dde080333c2fb64c619; ASLBSACORS=0003c515ff7a1f7e7618fdb6e230a6fae1ec5f3175921df43dde080333c2fb64c619',
            # 'Pragma':'no-cache',
            # 'Priority':'u=0, i',
            # 'Sec-Ch-Ua':'"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            # 'Sec-Ch-Ua-Mobile':'?0',
            # 'Sec-Ch-Ua-Platform':'"macOS"',
            # 'Sec-Fetch-Dest':'document',
            # 'Sec-Fetch-Mode':'navigate',
            # 'Sec-Fetch-Site':'none',
            # 'Sec-Fetch-User':'?1',
            # 'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        }

        for url in urls:
            yield scrapy.Request(url=url, headers=headers, callback=self.parse)
            # yield scrapy.Request(url=url, headers={
            #      'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
            # }, callback=self.parse)

    def parse(self, response):
        dprint('parse')

        # viewstate = response.xpath('//input[@name="__VIEWSTATE"]/@value').get()
        # viewstategenerator = response.xpath('//input[@name="__VIEWSTATEGENERATOR"]/@value').get()
        # eventvalidation = response.xpath('//input[@name="__EVENTVALIDATION"]/@value').get()

        formData = {
            'LSD': '13',
            'Section': '24',
            'Township': '50',
            'Range': '09',
            'Meridian': '4',
            'btnSearch': 'Search',
            # '__VIEWSTATE': viewstate,
            # '__VIEWSTATEGENERATOR': viewstategenerator,
            # '__EVENTVALIDATION': eventvalidation,
            '_EubIapPageUseProgressMonitor': 'true',
        }

        headers = {
            # 'Referer': response.url,
            # 'Origin': 'https://dds.aer.ca',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        }

        # handles aspx double underscore hidden fields
        yield FormRequest.from_response(response=response, formdata=formData, headers=headers, callback=self.step2)
        
    def step2(self, response):
        dprint('step2')
        # open_in_browser(response)

        formData = {
            # '__VIEWSTATE': viewstate,
            # '__VIEWSTATEGENERATOR': viewstategenerator,
            # '__EVENTVALIDATION': eventvalidation,
            'PageItems': '100',
            '_EubIapPageUseProgressMonitor': 'true',
        }

        headers = {
            # 'Referer': response.url,
            # 'Origin': 'https://dds.aer.ca',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        }

        # handles aspx double underscore hidden fields
        yield FormRequest.from_response(response=response, formdata=formData, headers=headers, callback=self.step3)

    def step3(self, response):
        dprint('step3')
        open_in_browser(response)
        