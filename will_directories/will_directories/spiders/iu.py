# -*- coding: utf-8 -*-
import string
import itertools
from scrapy import Spider
from scrapy.shell import inspect_response
from scrapy.http import Request, FormRequest
from scrapy.utils.response import open_in_browser


def xp(response, value):
    return response.xpath('//dt[text()="' + value + '"]/following-sibling::dd//text()').extract_first()

class IuSpider(Spider):
    name = 'iu'
    allowed_domains = ['directory.iu.edu']

    def start_requests(self):
        alphabets = list(string.ascii_lowercase)
        permutations = itertools.product(alphabets, repeat=3)
        for permutation in permutations:
            permutation = ''.join(permutation)
            yield Request('https://directory.iu.edu/',
                          meta={'permutation': permutation},
                          callback=self.parse)

        # yield Request('https://directory.iu.edu/',
        #               meta={'permutation': 'aaa'},
        #               callback=self.parse)

    def parse(self, response):
        data = {'__RequestVerificationToken': response.xpath('//*[@name="__RequestVerificationToken"]/@value').extract_first(),
                'SearchText': response.meta['permutation'],
                'Campus': 'Any',
                'Affiliation': 'Any',
                'IncludeDepartmentListings': 'true',
                'IncludeDepartmentListings': 'false',
                'ExactMatch': 'false'}

        yield FormRequest('https://directory.iu.edu/Search/Result',
                          formdata=data,
                          callback=self.parse_form_page)

    def parse_form_page(self, response):
        # open_in_browser(response)
        # inspect_response(response, self)

        rows = response.xpath('//script[@type="text/javascript"]')[0].extract().split()
        for row in rows:
            if '"URL":"' in row:
                person_url = row.split('"URL":"')[-1].split('"},')[0]
                absolute_person_url = 'https://directory.iu.edu/' + person_url.replace('"}],', '')

                yield Request(absolute_person_url,
                              callback=self.parse_person)

    def parse_person(self, response):
        name = response.xpath('//h2/text()').extract_first()

        first_name = name.split(',')[1].split()[0]

        middle_name = name.split(',')[0]

        try:
            last_name = name.split(',')[1].split()[1]
        except IndexError:
            middle_name = ''
            last_name = name.split(',')[0]

        campus = xp(response, 'Campus')
        affiliation = xp(response, 'Affiliation')
        department = xp(response, 'Department')
        email = xp(response, 'Email')
        address = xp(response, 'Address')
        url = response.url

        if affiliation:
            if 'undergraduate' in affiliation.lower():
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
                   'campus': campus,
                   'affiliation': affiliation,
                   'department': department,
                   'email': email,
                   'address': address,
                   'url': url}





