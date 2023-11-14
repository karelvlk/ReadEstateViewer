import logging
from scrapy.exceptions import DropItem
from postgres import PostgresClient


class PostgresPipeline:
    def __init__(self, db_config):
        self.db_config = db_config

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get("DB_CONFIG"))

    def open_spider(self, spider):
        self.client = PostgresClient(self.db_config)

    def close_spider(self, spider):
        self.client.close_pool()

    def process_item(self, item, spider):
        logging.debug(f"Processing scraped data in postgres pipeline: {item}")
        if item["title"] and item["img_url"]:
            self.client.insert_data(item["title"], item["img_url"])
            return item
        else:
            raise DropItem(f"Missing title or image URL in {item}")
