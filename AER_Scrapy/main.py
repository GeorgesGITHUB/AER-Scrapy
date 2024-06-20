import pandas as pd
from AER_Scrapy.spiders.plotplan import PlotPlanSpider as Spider
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from scrapy.utils.reactor import install_reactor

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

def csv_to_list(file_path):
    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(file_path)

    # Get unique values from the "LandUnit" column
    return df['LandUnit'].unique()

def chunk_list(lst, chunk_size):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def main():
    dprint('AER_Scrapy by Georges Atallah')
    
    # Prevents wrong selector from being used
    install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')

    # Initialize Scrapy settings
    settings = get_project_settings()
    configure_logging(settings)
    runner = CrawlerRunner(settings)

    csv_path = 'AB_2023_Polygon_with_Source_LandUnit.csv'
    large_list = csv_to_list(csv_path)
    batch_size = 1

    # Divide the list into smaller batches
    batches = list(chunk_list(large_list, batch_size))

    @defer.inlineCallbacks
    def crawl():
        # yield runner.crawl(Spider, landunits=list(batches[0]))
        # reactor.stop()
        
        for i, batch in enumerate(batches):
            dprint(f'Running batch {i + 1}/{len(batches)}...')
            yield runner.crawl(Spider, landunits=list(batch))
            dprint(f'Batch {i + 1} completed.')
        reactor.stop()
        

    crawl()
    reactor.run()

if __name__ == '__main__':
    main()