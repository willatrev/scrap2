# -*- coding: utf-8 -*-
import json
import string
import itertools
from scrapy import Spider
from scrapy.shell import inspect_response
from scrapy.http import Request, FormRequest
from scrapy.utils.response import open_in_browser


class UnlSpider(Spider):
    name = 'unl'

    def start_requests(self):
        yield Request('https://gist.githubusercontent.com/Lazar-T/8c76fadbdac8d223c403490b88f68d0d/raw/dc886cc202aa5e106d9f2edc579f42deb5cd8195/names.txt',
                      callback=self.parse_name_page)

    def parse_name_page(self, response):
        names = response.body.split('\n')
        for name in names:
            name_lower = name.lower()
            url_with_name = 'https://directory.unl.edu/?format=partial&q=' + name_lower
            yield Request(url_with_name,
                          callback=self.parse_result_page)

        # yield Request('https://directory.unl.edu/?format=partial&q=mark',
        #               callback=self.parse_result_page)

    def parse_result_page(self, response):
        persons = response.xpath('//*[@id="results_affiliate"]//@href|'
                                 '//*[@id="results_faculty"]//@href|'
                                 '//*[@id="results_staff"]//@href|'
                                 '//*[@id="results_student"]//@href').extract()
        for person in persons:
            if person.startswith('http'):
                yield Request(person,
                              callback=self.parse_person)

    def parse_person(self, response):
        name = response.xpath('//*[@itemprop="name"]/text()').extract_first()
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

        type = response.xpath('//*[@class="eppa"]/text()').extract_first()
        job_title = response.xpath('//*[@itemprop="jobTitle"]/text()').extract_first()
        organization = response.xpath('//*[@class="organization-unit"]//span/text()').extract_first()

        location = response.xpath('//*[@class="street-address"]//text()|'
                                  '//*[@itemprop="address"]//text()').extract()
        if location:
            location = [l.strip() for l in location]
            location = filter(None, location)
            location = ', '.join(location)

        phone = response.xpath('//*[@itemprop="telephone"]/text()').extract_first()
        email = response.xpath('//*[@itemprop="email"]/text()').extract_first()
        if email:
            email = email.replace('&period;', '.')
            email = email.replace('&commat;', '@')

        if job_title:
            if 'undergraduate' in job_title.lower():
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
                   'type': type,
                   'job_title': job_title,
                   'organization': organization,
                   'location': location,
                   'phone': phone,
                   'email': email,
                   'url': response.url}
