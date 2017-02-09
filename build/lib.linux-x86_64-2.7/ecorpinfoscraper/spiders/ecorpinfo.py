# -*- coding: utf-8 -*-
import scrapy
from ecorpinfoscraper.items import EcorpinfoscraperItem
import re
from scrapy.http import Request

class EcorpinfoSpider(scrapy.Spider):
    name = "ecorpinfo"
    allowed_domains = ["ecorpinfo.com"]
    start_urls = (
        'http://ecorpinfo.com/search/page/1?st%5B%5D=Delhi',
        'http://ecorpinfo.com/search/page/1?st%5B%5D=Haryana',
        'http://ecorpinfo.com/search/page/1?st%5B%5D=Uttar+Pradesh',
        'http://ecorpinfo.com/search/page/1?st%5B%5D=Punjab',
        'http://ecorpinfo.com/search/page/1?st%5B%5D=Maharashtra',
        'http://ecorpinfo.com/search/page/1?st%5B%5D=Karnataka',
        'http://ecorpinfo.com/search/page/1?st%5B%5D=West+Bengal',
        'http://ecorpinfo.com/search/page/1?st%5B%5D=Gujarat',
    )

    index = []
    error_cnt = 0
    target_url = ""

    def parse(self, response):
        home_url = response.url.split("=")[1]

        exist = 0
        for row in self.index:
            if row["name"] == home_url:
                exist = 1

        if exist == 0:
            obj = {}
            obj["name"] = home_url
            obj["value"] = 0
            self.index.append(obj)

        container_div = response.xpath('//div[@class="row m-top-5"]')

        for row in container_div:
            content_a = row.xpath('.//h4/strong/a')
            a_href = content_a.xpath('@href').extract()

            if len(a_href) == 1:
                url = response.urljoin(a_href[0])
                req = Request(url=url, callback=self.parse_detail)
                req.meta['state'] = home_url
                yield req

        k = 0
        for row in self.index:
            if row["name"] == home_url:
                self.index[k]["value"] = self.index[k]["value"] + 1
                self.target_url = "http://ecorpinfo.com/search/page/" + str(self.index[k]["value"]) + "?st%5B%5D=" + home_url
                yield Request(url=self.target_url, callback=self.parse, headers={"X-Requested-With":"XMLHttpRequest"}, dont_filter=True)

            k = k + 1

    def parse_detail(self, response):
        item = EcorpinfoscraperItem()
        page_url = response.url

        company_info_p = response.xpath('//div[@id="company-content"]/p')

        for row in company_info_p:
            content = row.xpath('text()').extract()

            emails = re.findall('[^\.][\w\.]+\@[\w\.]+', content[0])

            if len(emails) > 0 :
                item["page_url"] = page_url
                item["state"] = response.meta['state']
                item["email"] = emails

        yield item
