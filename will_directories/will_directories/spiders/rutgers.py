# -*- coding: utf-8 -*-
import json
import string
import itertools
from scrapy import Spider
from scrapy.shell import inspect_response
from scrapy.http import Request, FormRequest
from scrapy.utils.response import open_in_browser


class RutgersSpider(Spider):
    name = 'rutgers'

    def start_requests(self):
        alphabets = list(string.ascii_lowercase)
        permutations = itertools.product(alphabets, repeat=3)
        for permutation in permutations:
            permutation = ''.join(permutation)
            yield Request('https://www.acs.rutgers.edu/pls/pdb_p/Pdb_Display.search_results?p_name_first=&p_name_last=' + permutation,
                          callback=self.parse)

        # yield Request('https://www.acs.rutgers.edu/pls/pdb_p/Pdb_Display.search_results?p_name_first=&p_name_last=aaa',
        #               callback=self.parse)

    def parse(self, response):
        persons = response.xpath('//td/a/@href').extract()
        for person in persons:
            yield Request(person,
                          callback=self.parse_person)

    def parse_person(self, response):
        name = response.xpath('//h3/text()').extract_first()
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

        email = response.xpath('//h4[text()="Email Address"]/following::dd/a/text()').extract_first()

        address = response.xpath('//h4[text()="Postal Address"]/following::dd[1]//text()').extract()
        if address:
            address = [a.strip() for a in address]
            address = ', '.join(address)

        location = response.xpath('//h4[text()="Location"]/following::dd[1]//text()').extract()
        if location:
            location = [l.strip() for l in location]
            location = ', '.join(location)

        phone = response.xpath('//dt[text()="Phone:"]/following-sibling::dd/text()').extract_first()

        fax = response.xpath('//dt[text()="Fax:"]/following-sibling::dd/text()').extract_first()

        title = response.xpath('//dt[text()="Title:"]/following-sibling::dd/text()').extract_first()
        if title:
            if 'undergraduate' in title.lower():
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
                   'address': address,
                   'location': location,
                   'title': title,
                   'phone': phone,
                   'fax': fax}
