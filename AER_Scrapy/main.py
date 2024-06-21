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

def poly_landunit_dict_from(file_path):
    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(file_path)

    # Group by 'PolyID' and aggregate 'LandUnit' into lists
    grouped_data = df.groupby('PolyID')['LandUnit'].apply(list).reset_index()

    # Convert grouped data into a dictionary
    return dict(zip(grouped_data['PolyID'], grouped_data['LandUnit']))

def print_polygon_coverage_board(poly_ld_dict, validation_poly_ld_dict):
    print('*************** Polygon coverage board ***************')
    
    # For every polygon
    for poly in validation_poly_ld_dict:
        v_landunits = validation_poly_ld_dict[poly]
        landunits = poly_ld_dict[poly]
        
        covered=''
        covered_count=0
        not_covered=''
        not_covered_count=0
        # for each landunit
        for v_ld in v_landunits:
            # append to a coverage and not coverage list
            if (v_ld in landunits):
                covered += v_ld + ' ; '
                covered_count += 1
            else: 
                not_covered += v_ld + ' ; '
                not_covered_count += 1

        print(poly)
        print(f'Covered Land Units ({covered_count}): {covered}')
        print(f'Missing Land Units ({not_covered_count}): {not_covered}')



    print('*************************************************')

def main(start_i=None):
    # Prevents wrong selector from being used
    install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')
    # Initialize Scrapy settings
    settings = get_project_settings()
    configure_logging(settings)
    runner = CrawlerRunner(settings)

    dprint('AER_Scrapy by Georges Atallah')

    csv_path = 'AB_2023_Polygon_with_Source_LandUnit.csv'
    large_list = csv_to_list(csv_path)

    if (start_i != None): 
        dprint('slicing landunit list')
        large_list = large_list[start_i:]

    validation_poly_ld_dict = poly_landunit_dict_from(csv_path)

    poly_ld_dict = dict() # used for stat tracking
    for key in validation_poly_ld_dict: poly_ld_dict[key]=[]

    batch_size = 1

    # Divide the list into smaller batches
    batches = list(chunk_list(large_list, batch_size))

    @defer.inlineCallbacks
    def crawl():
        
        for i, batch in enumerate(batches):

            dprint(f'Running batch {i + 1}/{len(batches)}...')
            yield runner.crawl(
                Spider, 
                landunits=list(batch), 
                poly_ld_dict= poly_ld_dict,
            )
            dprint(f'Batch {i + 1} completed.')
            
            dprint(
                (i+1),'LandUnits scrapes complete, from indexes',
                f'(0,{i}(',
                '\n',
                large_list[ : (i+1)*batch_size ],
            )
            dprint(
                'LandUnits scrapes remaining, from indexes',
                f'({(i+1)*batch_size},{len(large_list)-1}(',
                '\n',
                # large_list[ (i+1)*batch_size : ],
            )

            if (i%5==0 and i!=0):
                print_polygon_coverage_board(poly_ld_dict, validation_poly_ld_dict)

        # Printing at completion
        print_polygon_coverage_board(poly_ld_dict, validation_poly_ld_dict)

        reactor.stop()
        

    crawl()
    reactor.run()

if __name__ == '__main__':
    main()