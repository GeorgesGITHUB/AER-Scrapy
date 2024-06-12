import scrapy
from scrapy.utils.response import open_in_browser
from scrapy import FormRequest
from scrapy.http import Request
from urllib.parse import urljoin
import os

def createRowsMetaData(htmlRows): # util function
    rowsMeta=[]
    for row in htmlRows:
        columns = []
        columns.append( row.xpath('td[1]//input[@value="View"]/@name').get() )
        columns.extend( row.xpath('td//text()').getall() )
        rowsMeta.append({
            'View_name':columns[0],
            'App#':columns[1],
            'Alt#':columns[2],
            'Status':columns[3],
            'Primary Applicant':columns[4],
            'Registered':columns[5],
            'Category':columns[6],
            'Type':columns[7],
            'Location':columns[8],
        })
    
    return rowsMeta

def dprint(*texts):
    print('*')
    print('**')
    print('***')

    string = ''
    for e in texts : string += e + ' '
    print('****',string)

    print('***')
    print('**')
    print('*')

class PlotPlanSpider(scrapy.Spider):
    name = "plotplan"
    url = "https://dds.aer.ca/iar_query/FindApplications.aspx"
    userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',

    def start_requests(self):
        dprint('AER_Scrapy by Georges Atallah')
        dprint('Spider', self.name, 'making a Request to', self.url)

        headers = {
            'User-Agent': self.userAgent
        }

        yield scrapy.Request(
            url=self.url, 
            headers=headers, 
            callback=self.step1
        )

    # Submitting a query
    def step1(self, response):
        dprint('Starting step1')

        formData = {
            'LSD': '13',
            'Section': '24',
            'Township': '50',
            'Range': '09',
            'Meridian': '4',
            'btnSearch': 'Search',
            '_EubIapPageUseProgressMonitor': 'true',
        }

        headers = {
            'User-Agent': self.userAgent,
        }

        # from_response handles aspx double underscore hidden fields
        yield FormRequest.from_response(
            response=response, 
            formdata=formData, 
            headers=headers, 
            callback=self.step2
        )
    
    # Reloads Query results to display 100 items
    def step2(self, response):
        dprint('Starting step2')

        formData = {
            'PageItems': '100',
            '_EubIapPageUseProgressMonitor': 'true',
        }

        headers = {
            'User-Agent': self.userAgent,
        }

        # handles aspx double underscore hidden fields
        yield FormRequest.from_response(
            response=response, 
            formdata=formData, 
            headers=headers, 
            callback=self.step3
        )

    # Gets row data of targetted rows then views them
    def step3(self, response):
        dprint('Starting step3')

        # Select Rows where 7th column contains substring "Facility"
        rows = response.xpath('//table//tr[contains(td[7], "Facility")]')
        # Further Select Rows where 1st column contains an input tag where input.value="View"
        rows = rows.xpath('td[1][input[@value="View"]]/..')

        # Saving meta data of rows
        rowsMeta = createRowsMetaData(rows)
        
        headers = {
            'User-Agent': self.userAgent,
        }

        for rowMeta in rowsMeta:
            formData = {
                'PageItems':'100',
                rowMeta['View_name']:'View',
                '_EubIapPageUseProgressMonitor':'true',
            }
            yield FormRequest.from_response(
                response=response,
                formdata=formData,
                headers=headers,
                callback=self.step4,
                meta=rowMeta,
            )

    # Visit the View Attachments page
    def step4(self, response):
        dprint('Starting step4 for Application Number', response.meta['App#'])

        url = 'https://dds.aer.ca/iar_query/'
        url += response.xpath('//a[text()="View Attachments"]/@href').get()

        headers = {
            'User-Agent': self.userAgent,
        }

        yield scrapy.Request(
            url=url,
            headers=headers,
            callback=self.step5,
            meta=response.meta, # passing the meta data
        )

    # Initiates a download requests for plotplan attachments
    def step5(self, response):
        dprint('Starting step5 for Application Number', response.meta['App#'])
        
        # Extract the href value of the anchor tag with the text "Plot Plan"
        relative_url = response.xpath('//a[text()="Plot Plan"]/@href').get()

        file_url = urljoin(response.url, relative_url)

        headers = {
            'User-Agent': self.userAgent,
        }

        yield Request(
            url=file_url,
            headers= headers,
            callback=self.step6,
            # meta=response.meta,
        )

    # Downloads plotplans into a directory
    def step6(self, response):
        dprint('Starting step6')

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
        
        dprint(f"File saved as {file_path}")
    
