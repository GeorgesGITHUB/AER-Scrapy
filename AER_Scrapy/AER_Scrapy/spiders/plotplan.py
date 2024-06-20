import scrapy
from scrapy import FormRequest
from scrapy.http import Request
from urllib.parse import urljoin
import os
import pandas as pd

from scrapy.utils.reactor import install_reactor
# Prevents wrong selector from being used
install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')



def csv_to_dict(file_path):
    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(file_path)

    # Group by 'LandUnit' and aggregate 'PolyID' into lists
    grouped_data = df.groupby('LandUnit')['PolyID'].apply(list).reset_index()

    # Convert grouped data into a dictionary
    return dict(zip(grouped_data['LandUnit'], grouped_data['PolyID']))

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
    for e in texts : string += str(e) + ' '
    print('****',string)

    print('***')
    print('**')
    print('*')

# Paths are relative to where Scrapy crawl is used
class PlotPlanSpider(scrapy.Spider):
    name = "plotplan"
    url = "https://dds.aer.ca/iar_query/FindApplications.aspx"
    userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    LandUnit_PolyID_Dict = csv_to_dict('AB_2023_Polygon_with_Source_LandUnit.csv')
    number_of_scrapes_allowed= -1 # set to -1 to disable limit
    use_preset=False
    
    def __init__(self, landunits=None, *args, **kwargs):
        super(PlotPlanSpider, self).__init__(*args, **kwargs)
        self.landunits = landunits

    def start_requests(self):
        dprint('Spider', self.name, 'making a Request to', self.url)

        headers = {
            'User-Agent': self.userAgent
        }

        if (self.use_preset):
            yield scrapy.Request(
                url=self.url, 
                headers=headers, 
                callback=self.step1Preset,
            )
        else:
            yield scrapy.Request(
                url=self.url, 
                headers=headers, 
                callback=self.step1,
            )

    # Submitting queries with LandUnits from LandUnit_PolyID_Dict
    def step1(self, response):
        dprint('Starting step1')

        for key in self.landunits:

            landUnit = key.split('-')
            temp = landUnit[3].split('W')
            landUnit[3]=temp[0]
            landUnit.append(temp[1])
            temp=None
            
            formData = {
                'LSD': landUnit[0],
                'Section': landUnit[1],
                'Township': landUnit[2],
                'Range': landUnit[3],
                'Meridian': landUnit[4],
                'btnSearch': 'Search',
                '_EubIapPageUseProgressMonitor': 'true',
            }
            
            # print('Form Data Entered:', formData)

            headers = {
                'User-Agent': self.userAgent,
            }

            # from_response handles aspx double underscore hidden fields
            yield FormRequest.from_response(
                response=response, 
                formdata=formData, 
                headers=headers, 
                callback=self.step2,
                meta={'LandUnit':key}
            )

    # Submitting query from preset LandUnit
    # Used to targetting specific LandUnits or testing
    def step1Preset(self, response):
        dprint('Starting step1Preset')

        key = '13-24-050-09W4'
        
        landUnit = key.split('-')
        temp = landUnit[3].split('W')
        landUnit[3]=temp[0]
        landUnit.append(temp[1])
        temp=None

        formData = {
                'LSD': landUnit[0],
                'Section': landUnit[1],
                'Township': landUnit[2],
                'Range': landUnit[3],
                'Meridian': landUnit[4],
                'btnSearch': 'Search',
                '_EubIapPageUseProgressMonitor': 'true',
            }
        
        print('Form Data Entered:', formData)

        headers = {
            'User-Agent': self.userAgent,
        }

        # from_response handles aspx double underscore hidden fields
        yield FormRequest.from_response(
            response=response, 
            formdata=formData, 
            headers=headers, 
            callback=self.step2,
            meta={'LandUnit':key}
        )
    
    # Reloads Query results to display 100 items
    def step2(self, response):
        dprint('Starting step2', '|',
               'LandUnit:', response.meta['LandUnit'],'|',
               'Polygon:', self.LandUnit_PolyID_Dict[ response.meta['LandUnit'] ][0])

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
            callback=self.step3,
            meta=response.meta # passing meta forward
        )

    # Gets row data of targetted rows then views them
    def step3(self, response):
        dprint('Starting step3', '|',
               'LandUnit:', response.meta['LandUnit'],'|', 
               'Polygon:', self.LandUnit_PolyID_Dict[ response.meta['LandUnit'] ][0])

        # Select Rows where 7th column contains substring "Facility"
        rows = response.xpath('//table//tr[contains(td[7], "Facility")]')
        # Further Select Rows where 1st column contains an input tag where input.value="View"
        rows = rows.xpath('td[1][input[@value="View"]]/..')

        # Saving meta data of rows
        # Row[ View | App# | Alt# | Status | Primary Applicant | Registered | Category | Type | Location ]
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

            response.meta['App#']=rowMeta['App#']
            yield FormRequest.from_response(
                response=response,
                formdata=formData,
                headers=headers,
                callback=self.step4,
                meta=response.meta,
            )

    # Visit the View Attachments page
    def step4(self, response):
        dprint('Starting step4', '|',
               'Application Number', response.meta['App#'], '|',
               'LandUnit:', response.meta['LandUnit'],'|', 
               'Polygon:', self.LandUnit_PolyID_Dict[ response.meta['LandUnit'] ][0])

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
        dprint('Starting step5', '|',
               'Application Number', response.meta['App#'], '|',
               'LandUnit:', response.meta['LandUnit'],'|', 
               'Polygon:', self.LandUnit_PolyID_Dict[ response.meta['LandUnit'] ][0])

        # Extract all rows where the 2nd column contains an anchor tag containing "Plot Plan"
        rows = response.xpath('//table//tr[td[2]//a[contains(text(), "Plot Plan")]]')
        if len(rows) == 0: dprint('No plot plan found in View Attachments')

        for row in rows:
            # Get the relative URL from the 2nd column
            relative_url = row.xpath('td[2]//a/@href').get()
            
            # Get the date from the 4th column
            date = row.xpath('td[4]/text()').get()

            file_url = urljoin(response.url, relative_url)

            headers = {
                'User-Agent': self.userAgent,
            }

            response.meta['date']=date
            response.meta['PolyID']= self.LandUnit_PolyID_Dict[response.meta['LandUnit']][0]
            print('final response meta', response.meta)
            yield Request(
                url=file_url,
                headers= headers,
                callback=self.step6,
                meta=response.meta,
            )

    # Downloads plotplans into a directory
    def step6(self, response):
        dprint('Starting step6', '|',
               'Application Number', response.meta['App#'], '|',
               'LandUnit:', response.meta['LandUnit'],'|', 
               'Polygon:', self.LandUnit_PolyID_Dict[ response.meta['LandUnit'] ][0])

        # PolyID + Date in View Attachments + Doc Number
        filename = f"{response.meta['PolyID']}___{response.meta['date']}_{response.url.split('?DOCNUM=')[-1]}.pdf"
        
        # Create the directory if it does not exist
        directory = 'scraped-data'
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Handle filename conflicts
        file_path = os.path.join(directory, filename)
        counter = 1
        while os.path.exists(file_path):
            file_path = os.path.join(directory, f"{filename[:-4]}_({counter}).pdf")
            counter += 1
        
        # Save the file
        with open(file_path, 'wb') as f:
            f.write(response.body)
        
        dprint(f"File saved as {file_path}")
    
