# -*- coding: utf-8 -*-
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


class KstateSpider(Spider):
    name = 'kstate'
    start_urls = ('http://search.k-state.edu/',)

    def __init__(self):
        self.driver = webdriver.Chrome('/home/lazar/Dropbox/chromedriver')

    def parse(self, response):
        alphabets = list(string.ascii_lowercase)
        permutations = itertools.product(alphabets, repeat=2)
        for permutation in permutations:
            permutation = ''.join(permutation)

            self.driver.get('http://search.k-state.edu/')
            sleep(5)

            search_input = self.driver.find_element_by_xpath('//*[@class="text"]')
            sleep(1)

            search_input.send_keys(permutation)
            sleep(1)

            # click on Search button
            self.driver.find_element_by_xpath('//*[@class="searchButton"]').click()
            sleep(5)

            sel = Selector(text=self.driver.page_source)

            persons = sel.xpath('//*[@id="people-results"]/div')
            for person in persons:
                name = person.xpath('.//*[@class="student name"]/text()|'
                                    './/*[@class="employee name"]/text()|'
                                    './/*[@class="person name"]/text()').extract_first()
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

                title = person.xpath('.//*[@class="stuPlan"]/text()|'
                                     './/*[@class="empPos"]/text()').extract_first()

                email = person.xpath('.//a[contains(@href, "mailto:")]/text()').extract_first()

                office_phone = person.xpath(
                    './/dt[text()="Office phone:"]/following-sibling::dd/text()').extract_first()

                if title:
                    if 'undergraduate' in title.lower() or 'freshman' in title.lower() or 'sophomore' in title.lower() or 'junior' in title.lower() or 'senior' in title.lower():
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
                           'title': title,
                           'email': email,
                           'office_phone': office_phone}

    def close(self, reason):
        self.driver.quit()
