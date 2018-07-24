# -*- coding: utf-8 -*-
import re
import string
import itertools
from scrapy import Spider
from scrapy.shell import inspect_response
from scrapy.http import Request, FormRequest
from scrapy.utils.response import open_in_browser


class IastateSpider(Spider):
    name = 'iastate'

    def start_requests(self):
        alphabets = list(string.ascii_lowercase)
        permutations = itertools.product(alphabets, repeat=2)
        for permutation in permutations:
            permutation = ''.join(permutation)
            yield Request('https://www.info.iastate.edu/individuals/search/' + permutation,
                          callback=self.parse)

        # yield Request('https://www.info.iastate.edu/individuals/search/aa',
        #               callback=self.parse)

    def parse(self, response):
        # open_in_browser(response)

        persons = response.xpath('//*[@class="dir-Listing-item dir-Listing-item--oddRow"]/@href|'
                                 '//*[@class="dir-Listing-item dir-Listing-item--evenRow"]/@href').extract()
        for person in persons:
            person_url = response.urljoin(person)
            yield Request(person_url,
                          callback=self.parse_person)

        next_page_urls = response.xpath('//*[@class="wd-Pagination"]//@href').extract()
        if next_page_urls:
            for next_page_url in next_page_urls:
                absolute_next_page_url = response.urljoin(next_page_url)
                yield Request(absolute_next_page_url,
                              callback=self.parse)

    def parse_person(self, response):
        name = response.xpath('//h1/text()').extract_first()
        if len(name.split()) == 2:
            first_name = name.split()[1]
            middle_name = ''
            last_name = name.split()[0].replace(',', '')

        elif len(name.split()) == 3:
            first_name = name.split()[1]
            middle_name = name.split()[-1]
            last_name = name.split()[0].replace(',', '')

        elif len(name.split()) >= 4:
            print(True)
            first_name = name.split()[1]
            middle_name = ' '.join(name.split()[2:])
            last_name = name.split()[0].replace(',', '')
        else:
            first_name = ''
            middle_name = ''
            last_name = ''

        major = response.xpath('//span[text()="Major:"]/following-sibling::text()').extract_first()

        classification = response.xpath('//span[text()="Classification:"]/following-sibling::text()').extract_first()

        department = response.xpath('//span[text()="Dept:"]/following-sibling::text()').extract_first()

        title = response.xpath('//span[text()="Title:"]/following-sibling::text()').extract_first()

        email = response.xpath('//span[text()="Email:"]/following-sibling::script').extract_first()
        if email:
            email = email.split()

            email_name = [node for node in email if "(['" in node][0]
            email_name = " ".join(re.findall("[a-zA-Z]+", email_name))

            final_email = email_name + '@iastate.edu'
        else:
            final_email = ''

        office_phone = response.xpath('//span[text()="Office:"]/following-sibling::a/text()').extract_first()
        home_phone = response.xpath('//span[text()="Home:"]/following-sibling::a/text()').extract_first()

        office_address = response.xpath('//h3[text()="Office"]/following-sibling::text()').extract()
        if office_address:
            office_address = [a.strip() for a in office_address]
            office_address = ', '.join(office_address)

        home_address = response.xpath('//h3[text()="Home"]/following-sibling::text()').extract()
        if home_address:
            home_address = [a.strip() for a in home_address]
            home_address = ', '.join(home_address)

        url = response.url

        if classification:
            if 'undergraduate' in classification.lower() or 'freshman' in classification.lower() or 'sophomore' in classification.lower() or 'junior' in classification.lower() or 'senior' in classification.lower():
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
                   'major': major,
                   'classification': classification,
                   'department': department,
                   'title': title,
                   'final_email': final_email,
                   'office_phone': office_phone,
                   'home_phone': home_phone,
                   'office_address': office_address,
                   'home_address': home_address}
