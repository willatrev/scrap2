# -*- coding: utf-8 -*-
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


class LsuSpider(Spider):
    name = 'lsu'

    def start_requests(self):
        # alphabets = list(string.ascii_lowercase)
        # permutations = itertools.product(alphabets, repeat=3)
        # for permutation in permutations:
        #     permutation = ''.join(permutation)

        #     data = {'%%ModDate': '862582D000758FFE',
        #             '%%Surrogate_LastOper': '1',
        #             'LastOper': 'C',
        #             'LastName': permutation,
        #             'ButtonChoice': 'Search',
        #             '%%Surrogate_FirstSelect': '1',
        #             'FirstSelect': 'F',
        #             '%%Surrogate_FirstOper': '1',
        #             'FirstOper': 'S',
        #             'FirstName': '',
        #             '%%Surrogate_MiddleOper': '1',
        #             'MiddleOper': 'S',
        #             'MiddleName': ''}
        #     yield FormRequest('http://appl103.lsu.edu/dir003.nsf/04a25a4e526cd1f986257b3b005fce11?CreateDocument',
        #                       formdata=data,
        #                       callback=self.parse)

        data = {'%%Surrogate_LastOper': '1',
                'LastOper': 'C',
                'LastName': 'smi',
                'ButtonChoice': 'Search',
                '%%Surrogate_FirstSelect': '1',
                'FirstSelect': 'F',
                '%%Surrogate_FirstOper': '1',
                'FirstOper': 'S',
                'FirstName': '',
                '%%Surrogate_MiddleOper': '1',
                'MiddleOper': 'S',
                'MiddleName': ''}
        yield FormRequest('http://appl103.lsu.edu/dir003.nsf/04a25a4e526cd1f986257b3b005fce11?CreateDocument',
                          formdata=data,
                          callback=self.parse)

    def parse(self, response):
        # inspect_response(response, self)
        # open_in_browser(response)

        persons = response.xpath('//font[@class="data"]/a/@href').extract()
        for person in persons:
            person_url = response.urljoin(person)
            yield Request(person_url,
                          callback=self.parse_person)

    def parse_person(self, response):
        # open_in_browser(response)
        # inspect_response(response, self)

        name = response.xpath('//center/b/text()').extract_first()
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
            last_name = name.split()[2:]
            last_name = ' '.join(last_name)
        else:
            first_name = ''
            middle_name = ''
            last_name = ''

        email = response.xpath('//a[contains(@href, "mailto:")]/text()').extract_first()

        title = response.xpath('//div[@align="center"]/font[1]/text()').extract_first()

        department = response.xpath('//div[@align="center"]/font[1]/text()').extract_first()

        phone = response.xpath('//div[@align="right"]/font/text()').extract_first()

        address = response.xpath('//*[@title="Campus map"]/text()').extract_first()

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
                   'title': title,
                   'department': department,
                   'phone': phone,
                   'address': address}
