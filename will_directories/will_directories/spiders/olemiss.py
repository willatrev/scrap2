# -*- coding: utf-8 -*-
import re
import json
import string
import itertools
from time import sleep
from scrapy import Spider
from selenium import webdriver
from scrapy.selector import Selector
from scrapy.shell import inspect_response
from scrapy.http import Request, FormRequest
from scrapy.utils.response import open_in_browser


class OlemissSpider(Spider):
    name = 'olemiss'

    def start_requests(self):
        # alphabets = list(string.ascii_lowercase)
        # permutations = itertools.product(alphabets, repeat=1)
        # for permutation in permutations:
        #     permutation = ''.join(permutation)

        #     yield Request('http://olemiss.edu/search/index.php?r=all%2F' + permutation.upper() + '.json'
        #                   callback=self.parse)

        yield Request('http://olemiss.edu/search/index.php?r=all%2FJ.json',
                      callback=self.parse)

    def parse(self, response):
        # open_in_browser(response)
        # inspect_response(response, self)

        jsonresponse = json.loads(response.body.decode('utf-8'))
        peoples = jsonresponse['people']
        for people in peoples:
            people_json = json.loads(people)

            person_page = people_json['webpage']
            yield Request('http://' + person_page,
                          callback=self.parse_person)

    def parse_person(self, response):
        name = response.xpath('//h2/text()').extract_first()
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

        try:
            department = response.xpath('//*[@class="title"]/text()').extract()[0]
        except:
            department = ''

        try:
            title = response.xpath('//*[@class="title"]/text()').extract()[1]
        except:
            title = ''

        address = response.xpath('//*[@class="street"]/text()|//*[@class="postalcode"]/text()').extract()
        if address:
            address = ', '.join(address)

        phone = response.xpath('//*[@class="telephonenumber"]/text()').extract_first()

        email = response.xpath('//*[@class="mail"]/a/text()').extract_first()

        url = response.url

        if title:
            if 'undergraduate' in title.lower() or 'freshman' in title.lower() or 'sophomore' in title.lower() or 'junior' in title.lower():
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
                   'department': department,
                   'title': title,
                   'address': address,
                   'phone': phone,
                   'email': email}
