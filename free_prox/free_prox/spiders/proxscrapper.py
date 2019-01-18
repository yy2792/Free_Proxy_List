import scrapy
import logging
from datetime import datetime, timedelta, date
import time
import re


class proxSpider(scrapy.Spider):

    name = "proxscrap"

    def start_requests(self):
        url = 'https://www.us-proxy.org/'

        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        logging.info(u'--------------begin-------------------')

        print(response.body)
