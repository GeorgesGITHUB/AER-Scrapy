from AER_Scrapy.spiders.plotplan import PlotPlanSpider as Spider
from utils import cprint, col_to_list, cols_to_dict
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from scrapy.utils.reactor import install_reactor


# Configuration Settings
csv_path = 'test.csv'
# csv_path = 'AB_2023_Polygon_with_Source_LandUnit.csv'
directory = 'scraped-data'

def main():
    # Prevents wrong selector from being used
    install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')
    # Initialize Scrapy settings
    settings = get_project_settings()
    configure_logging(settings)
    runner = CrawlerRunner(settings)

    cprint('Running AER_Scrapy by Georges Atallah')

    # Crawl strategies
        # by all landunits
        # by all polygons
        # by some landunits
        # by some polygons

    landunits = col_to_list('LandUnit', csv_path)
    landunit_polyid = cols_to_dict('LandUnit','PolyID', csv_path)

    # Divide the list into smaller batches
    # batches = list(chunk_list(landunits, batch_size))

    @defer.inlineCallbacks
    def crawl():
        for i, landunit in enumerate(landunits):
            yield runner.crawl(
                Spider,
                directory=directory,
                landunit=landunit,
                landunit_polyid=landunit_polyid,
            )
            cprint(
                f'Index of LandUnits visited ({0},{i})', '\n'
                f'Index of LandUnits remaining ({i+1},{len(landunits)}('
            )

        reactor.stop()

    crawl()
    reactor.run()
    cprint('Program complete')

# def chunk_list(lst, chunk_size):
#     for i in range(0, len(lst), chunk_size):
#         yield lst[i:i + chunk_size]

if __name__ == '__main__':
    main()