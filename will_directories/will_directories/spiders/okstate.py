import re
import string
import itertools
from time import sleep
from scrapy import Spider
from selenium import webdriver
from scrapy.selector import Selector
from scrapy.shell import inspect_response
from scrapy.http import Request, FormRequest
from scrapy.utils.response import open_in_browser


class OkstateSpider(Spider):
    name = 'okstate'

    def start_requests(self):
        # alphabets = list(string.ascii_lowercase)
        # permutations = itertools.product(alphabets, repeat=1)
        # for permutation in permutations:
        #     permutation = ''.join(permutation)

        #     yield Request('https://directory.okstate.edu/index.php/module/Default/action/Index?select-campus=&searchOptions=people&search-terms=&search-first-name=' + permutation + '&search-last-name=',
        #                   callback=self.parse)

        yield Request('https://directory.okstate.edu/index.php/module/Default/action/Index?select-campus=&searchOptions=people&search-terms=&search-first-name=a&search-last-name=',
                      callback=self.parse)

    def parse(self, response):
        # inspect_response(response, self)
        # open_in_browser(response)

        persons = response.xpath('//tr/td[1]/a/@href').extract()
        for person in persons:
            yield Request(person,
                          callback=self.parse_person)

        next_page_urls = response.xpath('//*[@class="pagination"]//@href').extract()
        if next_page_urls:
            for next_page_url in next_page_urls:
                absolute_next_page_url = response.urljoin(next_page_url)
                yield Request(absolute_next_page_url,
                              callback=self.parse)

    def parse_person(self, response):
        name = response.xpath('//h1/text()').extract_first()
        if len(name.split()) == 2:
            first_name = name.split()[0]
            middle_name = ''
            last_name = name.split()[-1]

        elif len(name.split()) == 3:
            first_name = name.split()[0]
            middle_name = name.split()[1]
            last_name = name.split()[-1]

        elif len(name.split()) >= 4:
            first_name = name.split()[0]
            middle_name = name.split()[1]
            last_name = name.split()[1:-1]
            last_name = ' '.join(last_name)
        else:
            first_name = ''
            middle_name = ''
            last_name = ''

        email = response.xpath('//a[contains(@href, "mailto")]/@href').extract_first()
        if email:
            email = email.replace('mailto:', '')

        phone = response.xpath('//a[contains(@href, "tel:")]/@href').extract_first()
        if phone:
            phone = phone.replace('tel:', '')

        title = response.xpath('//*[@id="profile-title"]/text()').extract_first()

        department = response.xpath('//*[@id="profile-department"]/a/text()').extract_first()

        address = response.xpath('//address/text()').extract()
        if address:
            address = [a.strip() for a in address]
            address = [a for a in address if a != '']
            address = [a for a in address if a != 'Phone:']
            address = ', '.join(address)

        if title:
            if 'undergraduate' in title.lower() or 'freshman' in title.lower() or 'sophomore' in title.lower() or 'junior' in title.lower() or 'senior' in title.lower():
                undergraduate = True
            else:
                undergraduate = False
        else:
            undergraduate = False

        if not undergraduate:
            yield {'name': name,
                   'first_name': first_name,
                   'middle_name': middle_name,
                   'last_name': last_name,
                   'email': email,
                   'phone': phone,
                   'title': title,
                   'department': department,
                   'address': address}
