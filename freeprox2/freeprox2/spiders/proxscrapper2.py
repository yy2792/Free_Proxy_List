import scrapy
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.webdriver.support.ui as ui
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import logging
import time
import re
from datetime import datetime, timedelta
import os
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def to_time(check):
    re_Findhour = re.compile(r'\d+(?=\s+hours)', flags=re.IGNORECASE)
    re_Findminute = re.compile(r'\d+(?=\s+minutes)', flags=re.IGNORECASE)

    temp_hour = None
    temp_min = None

    if len(re_Findhour.findall(check)) >= 1:
        temp_hour = re_Findhour.findall(check)[0]

    if len(re_Findminute.findall(check)) >= 1:
        temp_min = re_Findminute.findall(check)[0]

    now_time = datetime.now()

    if temp_hour is not None:
        now_time -= timedelta(seconds=int(temp_hour) * 60 * 60)

    if temp_min is not None:
        now_time -= timedelta(seconds=int(temp_min) * 60)

    return now_time


class proxSpider(scrapy.Spider):
    name = "proxscrap2"

    pdir = os.path.abspath(__file__ + "/../../../")
    chromePath = pdir + '/chromedriver.exe'

    caps = DesiredCapabilities.CHROME
    caps['loggingPrefs'] = {'performance': 'ALL'}

    def __init__(self):

        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--incognito")

        # self.chrome_options.add_argument("--proxy-server={0}".format(self.proxy.proxy))

        self.driver = webdriver.Chrome(executable_path=self.chromePath, chrome_options=self.chrome_options,
                                       desired_capabilities=self.caps)
        self.wait = WebDriverWait(self.driver, 0.5)

    def is_visible(self, locator, timeout=20):
        try:
            time.sleep(1)
            ui.WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.XPATH, locator)))
            return True
        except TimeoutException:
            return False

    def start_requests(self):
        url = 'https://www.proxy-list.download/HTTPS'
        # url = 'https://www.sslproxies.org/'

        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        logging.info(u'--------------begin-------------------')
        self.driver.get(response.url)

        rows_path = ".//tbody[@id='tabli']//tr"

        self.is_visible(rows_path)

        rows = self.driver.find_elements_by_xpath(rows_path)


        for row in rows:
            temp_item = {}


            ip = row.find_elements_by_xpath(".//td")[0].text
            port = row.find_elements_by_xpath(".//td")[1].text
            country = row.find_elements_by_xpath(".//td")[3].text

            temp_item['ip'] = ip + ':' + port
            temp_item['https'] = 'yes'
            temp_item['country'] = country

            yield temp_item


        for i in range(200):

            button = self.driver.find_element_by_xpath(".//a[@id='btn2']")
            button.click()

            rows_path = ".//tbody[@id='tabli']//tr"

            self.is_visible(rows_path)

            rows = self.driver.find_elements_by_xpath(rows_path)

            for row in rows:

                ip = row.find_elements_by_xpath(".//td")[0].text
                port = row.find_elements_by_xpath(".//td")[1].text

                temp_item['ip'] = ip + ':' + port
                temp_item['https'] = 'yes'
                temp_item['country'] = country

                yield temp_item

            time.sleep(1)
