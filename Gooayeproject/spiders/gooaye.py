import scrapy
import datetime
import configparser
import argparse
import requests
import re
from scrapy.http import Request
from pathlib import Path
from scrapy.exceptions import CloseSpider


class GooayeSpider(scrapy.Spider):
    name = 'gooaye'
    allowed_domains = ['gooaye.com']
    start_urls = ['https://gooaye.com/']
    def __init__(self):
        # super().__init__(is_notify)
        self.count_news = 0

    def get_date(self):
        date = datetime.date.today().strftime("%Y/%m/%d")
        return date

    def get_line_notify_token(self):
        settings = configparser.ConfigParser()
        settings.read('config.ini')
        line_notify_token = settings["DEFAULT"]["LINE_NOTIFY_TOKEN"]
        return line_notify_token

    def line_notify_message(self, token, msg):
        headers = {
            "Authorization": "Bearer " + token, 
            "Content-Type" : "application/x-www-form-urlencoded"
        }

        payload = {
            "message": msg
        }
        
        r = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=payload)
        return r.status_code

    def fetch_min_date(self):
        lastweek = datetime.datetime.now().replace(hour=0, minute=0, second=0,
                                                    microsecond=0) \
                    - datetime.timedelta(days=7)
        return lastweek

    def parse_timestamp(self, timestamp):
        return datetime.datetime.strptime(timestamp, '%Y%m%d')

    def parse(self, response):
        self.logger.info('A response from %s just arrived!', response.url)
        filterlist = []
        for news in response.xpath("*//a[contains(text(),'運鈔車')]").extract():           
            regex = re.compile(r'(".*")')
            regex_date = re.compile(r'[0-9]+')
            match = regex.search(news)
            news_url = match.group(1)[1:-1]
            match_date = regex_date.search(news_url)
            if news_url != "":
                time = match_date.group(0) if len(match_date.group(0)) > 4 else '2021' + match_date.group(0)
                print(f"time : {time}")
                if self.parse_timestamp(time) >= self.fetch_min_date():
                    print('here')

                    if not news_url in filterlist:
                        filterlist.append(news_url)
                        token = self.get_line_notify_token()
                        message = f"{self.get_date()} gooaye news weekly broadcast \n{news_url}"
                        res = self.line_notify_message(token, message)
                    #...if add extra function
                    # yield Request(news_url, dont_filter=True)

            