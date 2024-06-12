# debug print
def dprint(*texts):
        print('****************************************')
        string=''
        for text in texts:
             string+=str(text)+' '+'\n'
        print(string)
        # print('****************************************')
        print()

import scrapy
from scrapy.utils.response import open_in_browser
from scrapy import FormRequest
from scrapy.http import Request
from urllib.parse import urljoin
import os



class PlotPlanSpider(scrapy.Spider):
    name = "plotplan"

    # Add user-agent rotator function triggered on init

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
        # open_in_browser(response)

        # Rows where 7th column contains substring "Facility"
        rows = response.xpath('//table//tr[contains(td[7], "Facility")]')
        # dprint('row after 1st filtering', rows)

        # Rows where 1st column contains an input tag where input.value="View"
        rows = rows.xpath('td[1][input[@value="View"]]/..')
        # dprint('row after 2nd filtering', rows)

        # Saving meta data for matched rows
        rowsMeta=[]
        for row in rows:
            columns = []
            columns.append( row.xpath('td[1]//input[@value="View"]/@name').get() )
            # dprint('columns after 1st append', columns)
            columns.extend( row.xpath('td//text()').getall() )
            # dprint('columns after 2nd append', columns)

            rowMeta = {
                'View_name':columns[0],
                'App#':columns[1],
                'Alt#':columns[2],
                'Status':columns[3],
                'Primary Applicant':columns[4],
                'Registered':columns[5],
                'Category':columns[6],
                'Type':columns[7],
                'Location':columns[8],
            }

            rowsMeta.append(rowMeta)
            dprint('Saved Row\' Meta Data', rowMeta)

        

        headers = {
            # 'Referer': response.url,
            # 'Origin': 'https://dds.aer.ca',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        }

        formData = {
            'PageItems':'100',
            'ApplicationGrid$ctl09$ctl00':'View',
            '_EubIapPageUseProgressMonitor':'true',
        }

        for rowMeta in rowsMeta:
            # handles aspx double underscore hidden fields
            yield FormRequest.from_response(
                response=response,
                formdata=formData,
                headers=headers,
                callback=self.step4,
                meta=rowMeta
            )

    def step4(self, response):
        dprint('step4')
        # open_in_browser(response)

        url = 'https://dds.aer.ca/iar_query/'
        url += response.xpath('//a[text()="View Attachments"]/@href').get()
        dprint('url of View Attachments', url)

        headers = {
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        }

        yield scrapy.Request(
            url=url,
            headers=headers,
            callback=self.step5,
            meta=response.meta # passing the meta data
        )

    def step5(self, response):
        dprint('step5')
        
        # Extract the href value of the anchor tag with the text "Plot Plan"
        relative_url = response.xpath('//a[text()="Plot Plan"]/@href').get()
        dprint('relative_url:', relative_url)
        
        # fileUrl = response.url + relative_url
        # fileUrl = 'https://dds.aer.ca/iar_query/ShowAttachment.aspx?DOCNUM=12007348'
        # fileUrl = 'https://dds.aer.ca/iar_query/ShowAttachment.aspx?'

        file_url = urljoin(response.url, relative_url)

        headers = {
            # 'Referer': response.url,
            # 'Origin': 'https://dds.aer.ca',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        }

        yield Request(
            url=file_url,
            headers= headers,
            callback=self.step6)

    def step6(self, response):
        # open_in_browser(response)

        # Using query part as filename and adding .pdf extension
        original_filename = response.url.split('?')[-1] + '.pdf'
        modified_filename = f"modified_{original_filename}"
        
        # Create the directory if it does not exist
        directory = 'scraped-data'
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Handle filename conflicts
        file_path = os.path.join(directory, modified_filename)
        counter = 1
        while os.path.exists(file_path):
            file_path = os.path.join(directory, f"modified_{counter}_{original_filename}")
            counter += 1
        
        # Save the file
        with open(file_path, 'wb') as f:
            f.write(response.body)
        
        self.log(f"File saved as {file_path}")
    
