from AER_Scrapy.spiders.plotplan import PlotPlanSpider as Spider
from db_utils import SQLiteDBHelper as DatabaseController
from utils import cprint, col_to_list, cols_to_dict
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from scrapy.utils.reactor import install_reactor


# Configuration Settings
csv_path = 'AB_2023_Polygon_with_Source_LandUnit.csv'
directory = 'scraped-data'
db_name = 'progress_tracking.db'
excel_export_path = 'web_crawl_report.xlsx'
# csv_path = 'test.csv'

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

    # Divide the list into smaller batches
    # batches = list(chunk_list(landunits, batch_size))
    
    tracking_db = DatabaseController(db_name, True, csv_path)
    tracking_db.close_connection()

    @defer.inlineCallbacks
    def crawl():
        for i, landunit in enumerate(landunits):
            yield runner.crawl(
                Spider,
                directory=directory,
                db_name = db_name,
                landunit=landunit,
            )
            cprint(
                f'LandUnits ({len(landunits)}), Index Range visited ({0},{i})', '| '
                f'remaining ({i+1},{len(landunits)}(',
            )

        reactor.stop()

    crawl()
    reactor.run()

    tracking_db = DatabaseController(db_name)
    cprint(f'Exporting Database {db_name[:-3]} to Excel as')
    tracking_db.export_to_xlsx(excel_export_path)

    cprint('Program complete')

# def chunk_list(lst, chunk_size):
#     for i in range(0, len(lst), chunk_size):
#         yield lst[i:i + chunk_size]

def testing():
    db = DatabaseController(db_name)
    res = db.query_polygon('09-10-049-07W4')

    # db.upsert_plotplan('P1')
    # db.upsert_plotplan('P2')
    # db.upsert_plotplan('P3',True)

    db.export_to_xlsx('test.xlsx')

if __name__ == '__main__':
    main()
    # testing()