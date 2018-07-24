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


class UtexasSpider(Spider):
    name = 'utexas'

    def start_requests(self):
        # alphabets = list(string.ascii_lowercase)
        # permutations = itertools.product(alphabets, repeat=3)
        # for permutation in permutations:
        #     permutation = ''.join(permutation)

            # yield Request('https://directory.utexas.edu/advanced.php?aq%5BName%5D=' + permutation + '&aq%5BCollege%2FDepartment%5D=&aq%5BTitle%5D=&aq%5BEmail%5D=&aq%5BHome+Phone%5D=&aq%5BOffice+Phone%5D=&scope=all',
            #               callback=self.parse)

        yield Request('https://directory.utexas.edu/advanced.php?aq%5BName%5D=aa&aq%5BCollege%2FDepartment%5D=&aq%5BTitle%5D=&aq%5BEmail%5D=&aq%5BHome+Phone%5D=&aq%5BOffice+Phone%5D=&scope=all',
                      callback=self.parse)

    def parse(self, response):
        # inspect_response(response, self)
        # open_in_browser(response)

        persons = response.xpath('//*[@id="moreinfo"]//@href').extract()
        for person in persons:
            person_url = response.urljoin(person)
            yield Request(person_url,
                          callback=self.parse_person)

    def parse_person(self, response):
        name = response.xpath('//td[contains(text(), "Name:")]/following-sibling::td/text()').extract_first()
        if name:
            name = name.strip()
            if ',' in name:
                name = name.split(',')[0:-1][0]
            else:
                pass

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

        email = response.xpath('//td[contains(text(), "Email:")]/following-sibling::td/a/text()').extract_first()
        if email:
            email = email.strip()

        job_title = response.xpath('//td[contains(text(), "Job Title:")]/following-sibling::td/text()').extract_first()
        if job_title:
            job_title = job_title.strip()

        department = response.xpath('//td[contains(text(), "Department:")]/following-sibling::td/text()').extract_first()
        if department:
            department = department.strip()

        office_phone = response.xpath('//td[contains(text(), "Office Phone:")]/following-sibling::td/text()').extract_first()
        if office_phone:
            office_phone = office_phone.strip()

        office_location = response.xpath('//td[contains(text(), "Office Location:")]/following-sibling::td//text()').extract()
        if office_location:
            office_location = [ol.strip() for ol in office_location]
            office_location = [ol for ol in office_location if ol != '']
            office_location = ', '.join(office_location)

        office_address = response.xpath('//td[contains(text(), "Office Address:")]/following-sibling::td//text()').extract()
        if office_address:
            office_address = [oa.strip() for oa in office_address]
            office_address = [oa for oa in office_address if oa != '']
            office_address = ', '.join(office_address)

        campus_mail_code = response.xpath('//td[contains(text(), "Campus Mail Code:")]/following-sibling::td/text()').extract_first()
        if campus_mail_code:
            campus_mail_code = campus_mail_code.strip()

        if job_title:
            if 'undergraduate' in job_title.lower() or 'freshman' in job_title.lower() or 'sophomore' in job_title.lower() or 'junior' in job_title.lower() or 'senior' in job_title.lower():
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
                   'job_title': job_title,
                   'department': department,
                   'office_phone': office_phone,
                   'office_location': office_location,
                   'office_address': office_address,
                   'campus_mail_code': campus_mail_code}
