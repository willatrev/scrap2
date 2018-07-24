# -*- coding: utf-8 -*-
import json
import string
import itertools
from scrapy import Spider
from scrapy.shell import inspect_response
from scrapy.http import Request, FormRequest
from scrapy.utils.response import open_in_browser


class PurdueSpider(Spider):
    name = 'purdue'

    def start_requests(self):
        yield Request('https://gist.githubusercontent.com/Lazar-T/8c76fadbdac8d223c403490b88f68d0d/raw/dc886cc202aa5e106d9f2edc579f42deb5cd8195/names.txt',
                      callback=self.parse_name_page)

    def parse_name_page(self, response):
        names = response.body.split('\n')
        for name in names:
            name_lower = name.lower()
            yield FormRequest('https://www.purdue.edu/directory/Advanced',
                              formdata={'SearchString': name_lower,
                                        'SelectedSearchTypeId': '0',
                                        'UsingParam': 'Search by Name',
                                        'CampusParam': 'All Campuses',
                                        'DepartmentParam': 'All Departments',
                                        'SchoolParam': 'All Schools'},
                              callback=self.parse_form_page)

        # yield FormRequest('https://www.purdue.edu/directory/Advanced',
        #                   formdata={'SearchString': 'john',
        #                             'SelectedSearchTypeId': '0',
        #                             'UsingParam': 'Search by Name',
        #                             'CampusParam': 'All Campuses',
        #                             'DepartmentParam': 'All Departments',
        #                             'SchoolParam': 'All Schools'},
        #                   callback=self.parse_form_page)

    def parse_form_page(self, response):
        # open_in_browser(response)
        # inspect_response(response, self)

        persons = response.xpath('//*[@id="results"]/ul/li')
        for person in persons:
            name = person.xpath('.//*[@class="cn-name"]/text()').extract_first().title()
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

            alias = person.xpath('.//th[contains(text(), "Alias")]/following-sibling::td/text()').extract_first()
            campus = person.xpath('.//th[contains(text(), "Campus")]/following-sibling::td/text()').extract_first()
            school = person.xpath('.//th[contains(text(), "School")]/following-sibling::td/text()').extract_first()
            qualified_name = person.xpath('.//th[contains(text(), "Qualified Name")]/following-sibling::td/text()').extract_first()
            department = person.xpath('.//th[contains(text(), "Department")]/following-sibling::td/text()').extract_first()
            title = person.xpath('.//th[contains(text(), "Title")]/following-sibling::td/text()').extract_first()
            building = person.xpath('.//th[contains(text(), "Building")]/following-sibling::td/text()').extract_first()
            email = person.xpath('.//th[contains(text(), "Email")]/following-sibling::td/a/text()').extract_first()
            phone = person.xpath('.//th[contains(text(), "Phone")]/following-sibling::td/a/text()').extract_first()

            if qualified_name:
                if 'undergraduate' in qualified_name.lower():
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
                       'alias': alias,
                       'campus': campus,
                       'school': school,
                       'qualified_name': qualified_name,
                       'department': department,
                       'title': title,
                       'building': building,
                       'email': email,
                       'phone': phone}
