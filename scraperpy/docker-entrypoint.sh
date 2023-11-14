#!/bin/sh
# Run the init-db script
python init-db.py

# Start the Scrapy spider
scrapy crawl scraperpy-css
