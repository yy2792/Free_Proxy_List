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

    name = "proxscrap"

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
        url = 'https://www.us-proxy.org/'

        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        logging.info(u'--------------begin-------------------')
        self.driver.get(response.url)

        rows_path = ".//table[@id='proxylisttable']//tr"

        self.is_visible(rows_path)

        rows = self.driver.find_elements_by_xpath(rows_path)

        for row in rows:
            temp_item = {}

            if len(row.find_elements_by_xpath(".//td")) == 8:
                ip = row.find_elements_by_xpath(".//td")[0].get_attribute('innerHTML')
                port = row.find_elements_by_xpath(".//td")[1].get_attribute('innerHTML')

                temp_item['ip'] = ip + ':' + port

                https = row.find_elements_by_xpath(".//td[@class='hx']")[0].get_attribute('innerHTML')
                temp_item['https'] = https

                check = row.find_elements_by_xpath(".//td[@class='hm']")[2].get_attribute('innerHTML')

                now_time = to_time(check)

                temp_item['check'] = now_time

                yield temp_item


        for i in range(2):

            button =self.driver.find_element_by_xpath(".//a[@data-dt-idx='9']")
            button.click()

            rows_path = ".//table[@id='proxylisttable']//tr"

            self.is_visible(rows_path)

            rows = self.driver.find_elements_by_xpath(rows_path)

            re_Findtd = re.compile(r'(?<=>).*(?=</td>)', flags=re.IGNORECASE)

            for row in rows:
                temp_item = {}

                if len(row.find_elements_by_xpath(".//td")) == 8:
                    ip = row.find_elements_by_xpath(".//td")[0].get_attribute('innerHTML')
                    port = row.find_elements_by_xpath(".//td")[1].get_attribute('innerHTML')

                    temp_item['ip'] = ip + ':' + port

                    https = row.find_elements_by_xpath(".//td[@class='hx']")[0].get_attribute('innerHTML')
                    temp_item['https'] = https

                    check = row.find_elements_by_xpath(".//td[@class='hm']")[2].get_attribute('innerHTML')

                    now_time = to_time(check)

                    temp_item['check'] = now_time

                    yield temp_item

                    time.sleep(2)