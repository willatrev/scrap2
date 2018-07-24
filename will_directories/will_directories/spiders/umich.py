# -*- coding: utf-8 -*-
import json
import string
import itertools
from scrapy import Spider
from scrapy.shell import inspect_response
from scrapy.http import Request, FormRequest
from scrapy.utils.response import open_in_browser


class UmichSpider(Spider):
    name = 'umich'
    allowed_domains = ['mcommunity.umich.edu']

    def __init__(self):
        self.visited_listings = []

    def start_requests(self):
        alphabets = list(string.ascii_lowercase)
        permutations = itertools.product(alphabets, repeat=3)
        for permutation in permutations:
            permutation = ''.join(permutation)
            yield FormRequest('https://mcommunity.umich.edu/mcPeopleService/people/search',
                              formdata={'searchCriteria': permutation},
                              callback=self.parse)

        # yield FormRequest('https://mcommunity.umich.edu/mcPeopleService/people/search',
        #                   formdata={'searchCriteria': 'bob'},
        #                   callback=self.parse)

    def parse(self, response):
        # inspect_response(response, self)
        jsonresponse = json.loads(response.body)
        for person in jsonresponse['person']:
            try:
                affiliation = person['affiliation']
            except:
                affiliation = ''

            try:
                aliases = person['aliases']
            except:
                aliases = ''

            try:
                displayName = person['displayName']

                if len(displayName.split()) == 2:
                    first_name = displayName.split()[0]
                    middle_name = ''
                    last_name = displayName.split()[-1]
                elif len(displayName.split()) == 3:
                    first_name = displayName.split()[0]
                    middle_name = displayName.split()[1]
                    last_name = displayName.split()[-1]
                else:
                    first_name = displayName.split()[0]
                    middle_name = ''
                    last_name = displayName.split()[-1]
            except:
                displayName = ''
                first_name = ''
                middle_name = ''
                last_name = ''

            try:
                email = person['email']
            except:
                email = ''

            try:
                uniqname = person['uniqname']
            except:
                uniqname = ''

            try:
                workAddress = person['workAddress']
            except:
                workAddress = ''

            try:
                workPhone = person['workPhone']
            except:
                workPhone = ''

            try:
                title = person['title']
            except:
                title = ''

            if uniqname in self.visited_listings:
                self.log('Found duplicate listing, skipping.')
            else:
                self.visited_listings.append(uniqname)

                if title:
                    if 'undergraduate' in ' '.join(title).lower():
                        undergraduate = True
                    else:
                        undergraduate = False
                else:
                    undergraduate = False

                if not undergraduate:
                    yield {'affiliation': affiliation,
                           'first_name': first_name,
                           'middle_name': middle_name,
                           'last_name': last_name,
                           'aliases': aliases,
                           'displayName': displayName,
                           'email': email,
                           'uniqname': uniqname,
                           'workAddress': workAddress,
                           'workPhone': workPhone,
                           'title': title}
