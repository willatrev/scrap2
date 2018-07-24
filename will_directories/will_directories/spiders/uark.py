# -*- coding: utf-8 -*-
import json
import string
import itertools
from scrapy import Spider
from scrapy.http import Request, FormRequest
from scrapy.utils.response import open_in_browser


class UarkSpider(Spider):
    name = 'uark'
    allowed_domains = ['directory.uark.edu']

    def start_requests(self):
        alphabets = list(string.ascii_lowercase)
        permutations = itertools.product(alphabets, repeat=3)
        for permutation in permutations:
            permutation = ''.join(permutation)
            yield Request('https://directory.uark.edu/?search=' + permutation)

        # yield Request('https://directory.uark.edu/?search=aaa')

    def parse(self, response):
        permutation = response.url.split('?search=')[-1]

        data = {'__RequestVerificationToken': response.xpath('//*[@name="__RequestVerificationToken"]/@value').extract()[0]}

        form_url = 'https://directory.uark.edu/people/search?query=' + permutation + '&classification=Faculty-Staff-Student-Emeritus-Affiliate-Retired'
        yield FormRequest(form_url,
                          formdata=data,
                          callback=self.parse_form_page)

    def parse_form_page(self, response):
        jsonresponse = json.loads(response.body)
        for node in jsonresponse['Data']:
            # full_name = node['DisplayName']
            # first_name = node['FirstName']
            # middle_name = node['MiddleName']
            # last_name = node['LastName']
            # email = node['Email']
            # department = node['Department']
            # title = node['Title']
            # phone_number = node['CampusPhone']
            # classification = node['PreferredClassification']

            # yield {'full_name': full_name,
            #        'first_name': first_name,
            #        'middle_name': middle_name,
            #        'last_name': last_name,
            #        'email': email,
            #        'department': department,
            #        'title': title,
            #        'phone_number': phone_number,
            #        'classification': classification}

            department = node['Department']
            displayname = node['DisplayName']
            email = node['Email']
            firstname = node['FirstName']
            lastname = node['LastName']
            level = node['Level']
            major = node['Major']
            majordepartment = node['MajorDepartment']
            middlename = node['MiddleName']
            preferredclassification = node['PreferredClassification']
            roomnumber = node['RoomNumber']
            state = node['State']
            title = node['Title']
            uid = node['Uid']
            zip = node['Zip']

            if title:
                if 'undergraduate' in title.lower():
                    undergraduate = True
                else:
                    undergraduate = False
            else:
                undergraduate = False

            if not undergraduate:
                yield {'Department': department,
                       'DisplayName': displayname,
                       'Email': email,
                       'FirstName': firstname,
                       'LastName': lastname,
                       'Level': level,
                       'Major': major,
                       'MajorDepartment': majordepartment,
                       'MiddleName': middlename,
                       'PreferredClassification': preferredclassification,
                       'RoomNumber': roomnumber,
                       'State': state,
                       'Title': title,
                       'Uid': uid,
                       'Zip': zip}
