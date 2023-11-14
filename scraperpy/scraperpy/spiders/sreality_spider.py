# The `ScraperpySpider` class is a Scrapy spider that scrapes data from a website and saves it to a
# PostgreSQL database.
import logging
import scrapy
from scrapy.exceptions import CloseSpider

DESIRED_SCRAPED_COUNT = 500
PLAYWRIGHT_TIMEOUT = 60000  # 1 min

logging.basicConfig(
    level=logging.INFO,
)


class ScraperpySpider(scrapy.Spider):
    name = "scraperpy-css"
    RETRY_LIMIT = 3  # Define a reasonable retry limit

    scraped_count = 0
    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS": 1,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1,
        "AUTOTHROTTLE_MAX_DELAY": 60,
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
        page = 0
        while True:
            page += 1
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
            retries = response.meta.get("retries", 0)
            if retries < self.RETRY_LIMIT:
                logging.warning(f"Retrying {response.url}, attempt {retries + 1}")
                yield scrapy.Request(
                    response.url,
                    meta={
                        "retries": retries + 1,
                        "playwright": True,
                        "playwright_page_methods": {
                            "wait_for_timeout": PLAYWRIGHT_TIMEOUT
                        },
                    },
                    dont_filter=True,  # Important to allow retry of the same URL
                )
            else:
                logging.error(
                    f"Failed to load page after {self.RETRY_LIMIT} retries: {response.url}, Status: {response.status}"
                )
            return

        for property_div in response.css(".property"):
            image_url = property_div.css("preact img::attr(src)").get()
            image_title = property_div.css("h2 a span::text").get()

            if image_url and image_title:
                # absolute_url = response.urljoin(image_url)
                # logging.debug(
                #     f"Scraped: Image URL: {absolute_url}, Title: {image_title.strip()}"
                # )
                self.scraped_count += 1
                logging.info(
                    f"Successfully scraped {self.scraped_count}/{DESIRED_SCRAPED_COUNT}"
                )
                if self.scraped_count >= DESIRED_SCRAPED_COUNT:
                    raise CloseSpider("Reached desired item count")
                else:
                    yield {"title": image_title, "img_url": image_url}

            # else:
            # logging.debug("No image URL or title found in this .property div.")
