# -*- coding: utf-8 -*-
import json
import string
import itertools
from scrapy import Spider
from scrapy.shell import inspect_response
from scrapy.http import Request, FormRequest
from scrapy.utils.response import open_in_browser


def xp(response, value):
    return response.xpath('.//td[text()="' + value + '"]/following-sibling::td//text()').extract_first()


class OsuSpider(Spider):
    name = 'osu'
    allowed_domains = ['osu.edu']

    def __init__(self):
        self.visited_listings = []

    def start_requests(self):
        alphabets = list(string.ascii_lowercase)
        permutations = itertools.product(alphabets, repeat=3)
        for permutation in permutations:
            permutation = ''.join(permutation)
            yield FormRequest('https://www.osu.edu/findpeople/',
                              formdata={'lastname': '',
                                        'firstname': permutation,
                                        'name_n': '',
                                        'filter': 'all'},
                              callback=self.parse)

        # yield FormRequest('https://www.osu.edu/findpeople/',
        #                   formdata={'lastname': 'smith',
        #                             'firstname': '',
        #                             'name_n': '',
        #                             'filter': 'all'},
        #                   callback=self.parse)

    def parse(self, response):
        # inspect_response(response, self)

        persons = response.xpath('//tr[contains(@class, " record-details")]')
        for person in persons:
            name = xp(person, ' Name:')
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

            unique_name = xp(person, 'Unique Name at OSU:')
            email = xp(person, 'Published Email Address:')
            job_title = xp(person, 'Job Title:')
            working_title = xp(person, 'Working Title: ')
            organization = xp(person, 'Organization: ')
            vp_college_name = xp(person, 'VP/College Name:')
            major = xp(person, 'Major:')
            college = xp(person, 'College:')
            if unique_name in self.visited_listings:
                self.log('Found duplicate listing, skipping.')
            else:
                self.visited_listings.append(unique_name)

                if major:
                    if 'undergraduate' in major.lower():
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
                           'unique_name': unique_name,
                           'email': email,
                           'job_title': job_title,
                           'working_title': working_title,
                           'organization': organization,
                           'vp_college_name': vp_college_name,
                           'major': major,
                           'college': college}
