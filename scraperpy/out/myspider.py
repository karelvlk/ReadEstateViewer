import scrapy
from scrapy.exceptions import DropItem
from postgres import PostgresClient

class PostgresPipeline:
    def __init__(self, db_config):
        self.db_config = db_config

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get('DB_CONFIG'))

    def open_spider(self, spider):
        self.client = PostgresClient(self.db_config)
        self.client.create_table()

    def close_spider(self, spider):
        self.client.close_pool()

    def process_item(self, item, spider):
        if item['title'] and item['img_url']:
            self.client.insert_data(item['title'], item['img_url'])
            return item
        else:
            raise DropItem(f"Missing title or image URL in {item}")

class SrealitySpider(scrapy.Spider):
    name = 'sreality'
    allowed_domains = ['sreality.cz']
    start_urls = [f'https://www.sreality.cz/hledani/prodej/byty?strana={i}' for i in range(1, 26)]
    custom_settings = {
        'ITEM_PIPELINES': {
            'scraperpy.pipelines.PostgresPipeline': 300,
        },
        'DB_CONFIG': {
            'user': 'user1',
            'password': 'password1',
            'host': 'db',
            'port': '5432',
            'database': 'sreality_db'
        }
    }

    def parse(self, response):
        for prop in response.css('.property'):
            title = prop.css('h2 a span::text').get()
            img_url = prop.css('a img::attr(src)').get()
            yield {'title': title, 'img_url': img_url}
