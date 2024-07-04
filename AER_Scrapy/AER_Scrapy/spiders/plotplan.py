import scrapy
from scrapy import FormRequest
from scrapy.http import Request
from urllib.parse import urljoin
import os
from utils import cprint, splitLandUnit
from db_utils import SQLiteDBHelper as DatabaseController

from scrapy.utils.reactor import install_reactor
# Prevents wrong selector from being used
install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')

# Paths are relative to the directory from which you issue the command
class PlotPlanSpider(scrapy.Spider):
    name = "plotplan"
    url = "https://dds.aer.ca/iar_query/FindApplications.aspx"
    
    def __init__(self, directory, landunit, db_name, landunit_polyid, *args, **kwargs):
        super(PlotPlanSpider, self).__init__(*args, **kwargs)
        self.directory = directory # str
        self.landunit = landunit # str
        self.db_name = db_name # str
        self.landunit_polyid = landunit_polyid # dict {'key':[v1,...,vn]}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
            # Call Utils User-Agent rotator instead of hard code
        }

    def start_requests(self):
        cprint(f'Spider {self.name} requesting {self.url}')
        yield scrapy.Request(
            url=self.url, 
            headers=self.headers, 
            callback=self.step1,
        )

    def step1(self, response):
        landunit_arr = splitLandUnit(self.landunit)

        cprint(f'Querying landunit {self.landunit}')
        # from_response handles aspx double underscore hidden fields
        yield FormRequest.from_response(
            response=response, 
            headers=self.headers, 
            callback=self.step2,
            formdata={
                'LSD': landunit_arr[0],
                'Section': landunit_arr[1],
                'Township': landunit_arr[2],
                'Range': landunit_arr[3],
                'Meridian': landunit_arr[4],
                'btnSearch': 'Search',
                '_EubIapPageUseProgressMonitor': 'true',
            },
            meta={
                'landunit':self.landunit,
            }
        )

    def step2(self, response):
        yield FormRequest.from_response(
            response=response, 
            headers=self.headers, 
            callback=self.step3,
            formdata={
                'PageItems': '100',
                '_EubIapPageUseProgressMonitor': 'true',
            }, 
            meta=response.meta # passing meta forward
        )

    def step3(self, response):
        # Select Rows where 7th column contains substring "Facility"
        # Further Select Rows where 1st column contains an input tag where input.value="View"
        html_rows = response.xpath('//table//tr[contains(td[7], "Facility")]')
        html_rows = html_rows.xpath('td[1][input[@value="View"]]/..')
        if (len(html_rows)==0): cprint('Facility Application not found')

        # Getting meta data of html_rows
        for html_row in html_rows:
            html_row_meta = [html_row.xpath('td[1]//input[@value="View"]/@name').get()]
            html_row_meta.extend( html_row.xpath('td//text()').getall() )

            html_row_meta_dict = {
                'View_name':html_row_meta[0],
                'App#':html_row_meta[1],
                'Alt#':html_row_meta[2],
                'Status':html_row_meta[3],
                'Primary Applicant':html_row_meta[4],
                'Registered':html_row_meta[5],
                'Category':html_row_meta[6],
                'Type':html_row_meta[7],
                'Location':html_row_meta[8],
            }

            response.meta['App#']=html_row_meta_dict['App#']
            cprint(f'Visiting Application {html_row_meta_dict['App#']} of landunit {response.meta['landunit']}')
            yield FormRequest.from_response(
                response=response,
                headers=self.headers,
                callback=self.step4,
                formdata={
                    'PageItems':'100',
                    html_row_meta_dict['View_name']:'View',
                    '_EubIapPageUseProgressMonitor':'true',
                },
                meta=response.meta,
            )

    def step4(self, response):
        url = f'https://dds.aer.ca/iar_query/{response.xpath('//a[text()="View Attachments"]/@href').get()}'
        yield scrapy.Request(
            url=url,
            headers=self.headers,
            callback=self.step5,
            meta=response.meta,
        )

    def step5(self, response):
        # Extract all rows where the 2nd column contains an anchor tag containing "Plot Plan"
        html_rows = response.xpath('//table//tr[td[2]//a[contains(text(), "Plot Plan")]]')
        cprint(f'({len(html_rows)}) plotplan link found in View Attachments of landunit {response.meta['landunit']}')
            
        for html_row in html_rows:
            tracking_db = DatabaseController(self.db_name)

            relative_url = html_row.xpath('td[2]//a/@href').get()
            file_url = urljoin(response.url, relative_url)

            response.meta['date'] = html_row.xpath('td[4]/text()').get()

            PolyID = tracking_db.query_polygon(response.meta['landunit'])
            if PolyID:
                response.meta['PolyID'] = PolyID
            else:
                response.meta['PolyID'] = 'Failed_To_Get_PolyID'
                

            plotplan_name = file_url.split('?DOCNUM=')[-1]
            cprint(f'Requesting plotplan {plotplan_name} of landunit {response.meta['landunit']}')

            tracking_db.upsert_plotplan(plotplan_name)
            tracking_db.upsert_landunit_plotplan(response.meta['landunit'], plotplan_name)
            tracking_db.close_connection()

            yield Request(
                url=file_url,
                headers=self.headers,
                callback=self.step6,
                meta=response.meta,
            )

    # Downloads plotplans into a directory
    def step6(self, response):
        plotplan_name = response.url.split('?DOCNUM=')[-1]

        # PolyID + Date in View Attachments + Doc Number
        filename = f"{response.meta['PolyID']}___{response.meta['date']}_{plotplan_name}.pdf"
        
        # Create the directory if it does not exist
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        
        # Handle filename conflicts
        file_path = os.path.join(self.directory, filename)
        counter = 1
        while os.path.exists(file_path):
            file_path = os.path.join(self.directory, f"{filename[:-4]}_({counter}).pdf")
            counter += 1
        
        # Save the file
        with open(file_path, 'wb') as f:
            f.write(response.body)
        
        cprint(f"File saved as {file_path}")

        tracking_db = DatabaseController(self.db_name)
        tracking_db.upsert_plotplan(plotplan_name, True)
        tracking_db.close_connection()

    
