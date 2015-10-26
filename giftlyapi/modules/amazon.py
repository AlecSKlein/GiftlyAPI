#!flask/bin/python
#It is NOT this module's job to do formatting or special packaging. This module does exclusively its job
#and that job is to get the items returned by Amazon's api lookups.
__author__ = 'Alec'

from amazon.api import AmazonAPI

class GiftlyAmazonAPI:

    amazon_product_details = ['api', 'asin', 'author', 'authors',
                              'aws_associate_tag', 'binding', 'brand',
                              'browse_nodes', 'color', 'creators', 'ean',
                              'edition', 'editorial_review', 'editorial_reviews',
                              'eisbn', 'features', 'get_attribute',
                              'get_attribute_details', 'get_attributes',
                              'get_parent', 'images', 'isbn', 'label', 'languages',
                              'large_image_url', 'list_price', 'manufacturer',
                              'medium_image_url', 'model', 'mpn', 'offer_url',
                              'pages', 'parent', 'parent_asin', 'parsed_response',
                              'part_number', 'price_and_currency', 'publication_date',
                              'publisher', 'region', 'release_date', 'reviews', 'sales_rank',
                              'sku', 'small_image_url', 'tiny_image_url', 'title',
                              'to_string', 'upc']

    amazon_search_index = ['All','Apparel','Appliances','ArtsAndCrafts','Automotive', 'Baby',
                           'Beauty','Blended','Books','Classical','Collectibles','DVD',
                           'DigitalMusic','Electronics', 'GiftCards','GourmetFood','Grocery',
                           'HealthPersonalCare','HomeGarden','Industrial','Jewelry', 'KindleStore',
                           'Kitchen','LawnAndGarden','Marketplace','MP3Downloads','Magazines','Miscellaneous',
                           'Music','MusicTracks','MusicalInstruments','MobileApps','OfficeProducts','OutdoorLiving',
                           'PCHardware', 'PetSupplies','Photo','Shoes','Software','SportingGoods',
                           'Tools','Toys','UnboxVideo','VHS','Video', 'VideoGames','Watches','Wireless','WirelessAccessories']

    def __init__(self, secret_key, access_key, assoc_tag):
        self.amazon = AmazonAPI(access_key, secret_key, assoc_tag)

    #Keywords is a comma-separated string
    #Returns a dictionary of products mapped as ASIN:TITLE
    #Can Android parse for keys? We'll find out...
    def get_similar_items(self, keywords, numitems=None, category=None):
        keywords = keywords.split(',') if keywords else None
        numitems = numitems if numitems else 10
        category = category if category else 'All'

        print "%d items found with keywords %s in the %s category" % (numitems, keywords, category)

        products = self.amazon.search_n(numitems, Keywords=keywords, SearchIndex=category)
        product_dict = {}
        for product in products:
            product_dict[product.asin] = product.title
        return product_dict

    def get_item_by_asin(self, asin):
        product = self.amazon.lookup(ItemId=asin)
        return product

    #asin_list is a list of individual asin strings
    #they are joined together as one large string
    def get_items_by_asin(self, asin_list):
        products = self.amazon.lookup(ItemId=(','.join(asin_list)))
        return products

