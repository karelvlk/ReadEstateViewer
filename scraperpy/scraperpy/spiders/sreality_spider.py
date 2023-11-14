import scrapy
import logging

PAGE_SIZE = 20
DESIRED_SCRAPED_COUNT = 500
PLAYWRIGHT_TIMEOUT = 60000  # 1 min


class ScraperpySpider(scrapy.Spider):
    name = "scraperpy-css"
    custom_settings = {
        "ITEM_PIPELINES": {
            "scraperpy.pipelines.PostgresPipeline": 300,
        },
        "DB_CONFIG": {
            "user": "user1",
            "password": "password1",
            "host": "db",
            "port": "5432",
            "database": "sreality_db",
        },
    }

    def start_requests(self):
        for page in range(1, (DESIRED_SCRAPED_COUNT // PAGE_SIZE) + 1):
            yield scrapy.Request(
                f"https://www.sreality.cz/hledani/prodej/byty?strana={page}",
                # meta={"playwright": True},
                meta={
                    "playwright": True,
                    "playwright_page_methods": {"wait_for_timeout": PLAYWRIGHT_TIMEOUT},
                },
            )

    def parse(self, response):
        if response.status != 200:
            logging.error(
                f"Failed to load page: {response.url}, Status: {response.status}"
            )
            return

        for property_div in response.css(".property"):
            image_url = property_div.css("preact img::attr(src)").get()
            image_title = property_div.css("h2 a span::text").get()

            if image_url and image_title:
                absolute_url = response.urljoin(image_url)
                logging.debug(
                    f"Scraped: Image URL: {absolute_url}, Title: {image_title.strip()}"
                )
                yield {"title": image_title, "img_url": image_url}
            else:
                logging.debug("No image URL or title found in this .property div.")
