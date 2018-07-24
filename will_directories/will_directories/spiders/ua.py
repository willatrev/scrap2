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


class UaSpider(Spider):
    name = 'ua'

    def start_requests(self):
        alphabets = list(string.ascii_lowercase)
        permutations = itertools.product(alphabets, repeat=3)
        for permutation in permutations:
            permutation = ''.join(permutation)

            yield Request('https://www.ua.edu/directory/?l=&f=' + permutation + '&p=&d=&t=all&_action=submit',
                          callback=self.parse)

        # yield Request('https://www.ua.edu/directory/?l=&f=aa&p=&d=&t=all&_action=submit',
        #               callback=self.parse)

    def parse(self, response):
        # inspect_response(response, self)
        # open_in_browser(response)

        persons = response.xpath('//tbody//tr/td[1]/a/@href').extract()
        for person in persons:
            person_url = response.urljoin(person)
            yield Request(person_url,
                          callback=self.parse_person)

    def parse_person(self, response):
        name = response.xpath('//*[@class="h4 padding-all-10"]/text()').extract_first()
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

        position = response.xpath('//td[text()="Position"]/following-sibling::td/text()').extract_first()
        if position:
            position = position.strip()

        department = response.xpath('//td[text()="Department"]/following-sibling::td/text()').extract_first()
        if department:
            department = department.strip()

        room_building = response.xpath('//td[text()="Room/Building"]/following-sibling::td/a/text()').extract_first()
        if room_building:
            room_building = room_building.strip()

        box_number = response.xpath('//td[text()="Box Number"]/following-sibling::td/text()').extract_first()
        if box_number:
            box_number = box_number.strip()

        phone = response.xpath('//td[text()="Phone"]/following-sibling::td//text()').extract()
        if phone:
            phone = [p.strip() for p in phone]
            phone = [p for p in phone if p != '']
            phone = phone[0]

        second_phone = response.xpath('//td[text()="Second Phone"]/following-sibling::td/text()').extract_first()
        if second_phone:
            second_phone = second_phone.strip()

        fax = response.xpath('//td[text()="Fax"]/following-sibling::td//text()').extract_first()
        if fax:
            fax = fax.strip()

        email = response.xpath('//td[text()="Email"]/following-sibling::td/a/text()').extract_first()
        if email:
            email = email.strip()

        if position:
            if 'undergraduate' in position.lower() or 'freshman' in position.lower() or 'sophomore' in position.lower() or 'junior' in position.lower() or 'senior' in position.lower():
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
                   'position': position,
                   'department': department,
                   'room_building': room_building,
                   'box_number': box_number,
                   'phone': phone,
                   'second_phone': second_phone,
                   'fax': fax,
                   'email': email}
