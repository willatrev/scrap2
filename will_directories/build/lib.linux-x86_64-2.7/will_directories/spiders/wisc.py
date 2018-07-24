# -*- coding: utf-8 -*-
import json
import string
import itertools
from scrapy import Spider
from scrapy.shell import inspect_response
from scrapy.http import Request, FormRequest
from scrapy.utils.response import open_in_browser


class WiscSpider(Spider):
    name = 'wisc'
    allowed_domains = ['wisc.edu']

    def __init__(self):
        self.visited_listings = []

    def start_requests(self):
        alphabets = list(string.ascii_lowercase)
        permutations = itertools.product(alphabets, repeat=3)
        for permutation in permutations:
            permutation = ''.join(permutation)
            yield Request('https://www.wisc.edu/directories/?q=' + permutation,
                          callback=self.parse)

        # yield Request('https://www.wisc.edu/directories/?q=aaa',
        #               callback=self.parse)

    def parse(self, response):
        persons = response.xpath('//*[@class="person"]')
        for person in persons:
            if u'More »' in person.extract():
                person_url = response.xpath('//*[@class="person_more"]/a/@href').extract_first()
                yield Request(response.urljoin(person_url),
                              callback=self.parse_person)
            else:
                name = response.xpath('//*[@class="person_name"]/text()').extract_first()
                email = response.xpath('//*[@class="person_email"]/a/text()').extract_first()
                phone = response.xpath('//*[@class="person_phone"]/text()').extract_first()

                if email in self.visited_listings:
                    self.log('Found duplicate listing, skipping.')
                else:
                    self.visited_listings.append(email)

                    yield {'name': name,
                           'email': email,
                           'phone': phone}

    def parse_person(self, response):
        name = response.xpath('//div[text()="Name"]/following-sibling::div/text()').extract_first()
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

        email = response.xpath('//div[text()="E-mail"]/following-sibling::div/a/text()').extract_first()
        phone = response.xpath('//div[text()="Phone"]/following-sibling::div/text()').extract_first()
        title = response.xpath('//div[text()="Title"]/following-sibling::div/text()').extract_first()
        division = response.xpath('//div[text()="Division"]/following-sibling::div/text()').extract_first()
        department = response.xpath('//div[text()="Department"]/following-sibling::div/text()').extract_first()
        unit = response.xpath('//div[text()="Unit"]/following-sibling::div/text()').extract_first()
        mailing_address = response.xpath('//div[text()="Mailing address"]/following-sibling::div//text()').extract()
        if mailing_address:
            mailing_address = [ma.strip() for ma in mailing_address]
            mailing_address = ', '.join(mailing_address)

        if title:
            if 'undergraduate' in title.lower():
                undergraduate = True
            else:
                undergraduate = False
        else:
            undergraduate = False

        if not undergraduate:
            if email in self.visited_listings:
                    self.log('Found duplicate listing, skipping.')
            else:
                self.visited_listings.append(email)

                yield {'name': name,
                       'first_name': first_name,
                       'middle_name': middle_name,
                       'last_name': last_name,
                       'email': email,
                       'phone': phone,
                       'title': title,
                       'division': division,
                       'department': department,
                       'unit': unit,
                       'mailing_address': mailing_address}
