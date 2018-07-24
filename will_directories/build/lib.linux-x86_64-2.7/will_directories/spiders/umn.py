# -*- coding: utf-8 -*-
import json
import string
import itertools
from scrapy import Spider
from scrapy.shell import inspect_response
from scrapy.http import Request, FormRequest
from scrapy.utils.response import open_in_browser


class UmnSpider(Spider):
    name = 'umn'

    def start_requests(self):
        alphabets = list(string.ascii_lowercase)
        permutations = itertools.product(alphabets, repeat=3)
        for permutation in permutations:
            permutation = ''.join(permutation)
            # yield FormRequest('https://mcommunity.umich.edu/mcPeopleService/people/search',
            #                   formdata={'searchCriteria': permutation},
            #                   callback=self.parse)
            yield Request('https://google.umn.edu/search?expertsearch=true&proxystylesheet=campus_tc&client=campus_tc&originalquery=&expertsearchfrontend=searchumn&getfields=*&num=25&wc=200&wc_mc=1&oe=UTF-8&ie=UTF-8&ud=1&expertsearchexpand=true&sort=meta%3Aumnnamelfm&entsp=a&site=campus_tc&q=' + permutation + '&btnG=search&filter=0&numgm=5&access=p',
                          callback=self.parse)

        # yield Request('https://google.umn.edu/search?expertsearch=true&proxystylesheet=campus_tc&client=campus_tc&originalquery=&expertsearchfrontend=searchumn&getfields=*&num=25&wc=200&wc_mc=1&oe=UTF-8&ie=UTF-8&ud=1&expertsearchexpand=true&sort=meta%3Aumnnamelfm&entsp=a&site=campus_tc&q=*ada&btnG=search&filter=0&numgm=5&access=p',
        #               callback=self.parse)

    def parse(self, response):
        persons = response.xpath('//*[@class="gsa-exp-info-column-ele gsa-exp-info-row-1-col-1"]/a/@href').extract()
        for person in persons:
            yield Request(person,
                          callback=self.parse_person)

    def parse_person(self, response):
        name = response.xpath('//*[@class="gsa-exp-info-column-ele gsa-exp-info-row-1-col-1"]/a/span/text()').extract_first()
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

        internet_id = response.xpath('//*[@class="gsa-exp-info-column-ele gsa-exp-info-row-2-col-2"]/span/text()').extract_first()
        phone = response.xpath('//*[@class="gsa-exp-info-column-ele gsa-exp-info-row-8-col-1"]/span/text()').extract_first()
        email = response.xpath('//*[@class="gsa-exp-info-column-ele gsa-exp-info-row-3-col-2"]/a/span/text()').extract_first()
        affiliation = response.xpath('//*[@class="gsa-exp-info-column-ele gsa-exp-info-row-4-col-2"]/span/text()').extract_first()
        title = response.xpath('//*[@class="gsa-exp-info-column-ele gsa-exp-info-row-5-col-1"]/span/text()').extract_first()
        college_dept = response.xpath('//*[@class="gsa-exp-info-column-ele gsa-exp-info-row-6-col-1"]/span/text()').extract_first()
        campus = response.xpath('//*[@class="gsa-exp-info-column-ele gsa-exp-info-row-11-col-1"]/span/text()').extract_first()
        home_address = response.xpath('//*[@class="gsa-exp-info-column-ele gsa-exp-info-row-12-col-1"]/span/text()').extract_first()
        enrollment = response.xpath('//*[@class="gsa-exp-info-column-ele gsa-exp-info-row-13-col-1"]/span/text()').extract_first()

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
                   'phone': phone,
                   'internet_id': internet_id,
                   'email': email,
                   'affiliation': affiliation,
                   'title': title,
                   'college_dept': college_dept,
                   'campus': campus,
                   'home_address': home_address,
                   'enrollment': enrollment,
                   'url': response.url}
