import scrapy
import logging
from datetime import datetime, timedelta, date
from scrapy_splash import SplashRequest
import time
import re


class proxSpider(scrapy.Spider):

    name = "proxscrap"
    http_user = '668e696bbce24c299dfc096632663ce0'

    js_source_code = '''
    function main(splash)
        assert(splash:go(splash.args.url))
        local get_dimensions = splash:jsfunc([[
            function () {
                var rect = document.getElementByXpath('.//a[@aria-controls="proxylisttable"]').getClientRects()[0];
                return {"x": rect.left, "y": rect.top}
            }
        ]])
        splash:set_viewport_full()
        splash:wait(0.1)
        local dimensions = get_dimensions()
        splash:mouse_click(dimensions.x, dimensions.y)
        -- Wait split second to allow event to propagate.
        splash:wait(0.1)
        return splash:html()
    end
    '''

    splash_args = {
        'wait': 6,
        'js_source': js_source_code
    }

    def start_requests(self):
        url = 'https://www.us-proxy.org/'

        yield SplashRequest(url=url, callback=self.parse,
                            args = self.splash_args)

    def parse(self, response):
        logging.info(u'--------------begin-------------------')

        rows = response.xpath(".//table[@id='proxylisttable']//tr")

        re_Findtd = re.compile(r'(?<=>).*(?=</td>)', flags=re.IGNORECASE)

        for row in rows:
            temp_item = {}
            if len(row.xpath(".//td").extract()) == 8:
                ip = row.xpath(".//td").extract()[0]
                port = row.xpath(".//td").extract()[1]

                if len(re_Findtd.findall(ip)) > 0:
                    ip = re_Findtd.findall(ip)[0]
                    temp_item['ip'] = ip

                if len(re_Findtd.findall(port)) > 0:
                    port = re_Findtd.findall(port)[0]
                    temp_item['port'] = port

                if len( row.xpath(".//td[@class='hx']").extract()) > 0:
                    https = row.xpath(".//td[@class='hx']").extract()[0]

                    if len(re_Findtd.findall(https)) > 0:
                        https = re_Findtd.findall(https)[0]
                        temp_item['https'] = https

                print(temp_item)
                yield temp_item

        next_page = response.xpath(".//li[@id='proxylisttable_next']//a").extract()

        print(next_page)

