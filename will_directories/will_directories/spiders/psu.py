# -*- coding: utf-8 -*-
import json
import string
import itertools
from scrapy import Spider
from scrapy.shell import inspect_response
from scrapy.http import Request, FormRequest
from scrapy.utils.response import open_in_browser


def xp(response, value):
    data_point = response.xpath('//th[contains(text(), "' + value + '")]/following-sibling::td//text()').extract()
    if data_point:
        data_point = [dp.strip() for dp in data_point]
        data_point = filter(None, data_point)
        data_point = ', '.join(data_point)
        data_point = data_point.strip()
    else:
        data_point = ''
    return data_point


class PsuSpider(Spider):
    name = 'psu'
    allowed_domains = ['work.psu.edu']

    def start_requests(self):
        alphabets = list(string.ascii_lowercase)
        permutations = itertools.product(alphabets, repeat=2)
        for permutation in permutations:
            permutation = ''.join(permutation)
            yield FormRequest('http://www.work.psu.edu/cgi-bin/ldap/ldap_query.cgi',
                              formdata={'sn': '',
                                        'cn': permutation,
                                        'uid': '',
                                        'mail': '',
                                        'full': '0',
                                        'submit': 'Search'},
                              callback=self.parse)

        # yield FormRequest('http://www.work.psu.edu/cgi-bin/ldap/ldap_query.cgi',
        #                   formdata={'sn': '',
        #                             'cn': 'smith',
        #                             'uid': '',
        #                             'mail': '',
        #                             'full': '0',
        #                             'submit': 'Search'},
        #                   callback=self.parse)

    def parse(self, response):
        # inspect_response(response, self)
        psdirids = response.xpath('//*[@name="psdirid"]/@value').extract()
        for psdirid in psdirids:
            yield FormRequest('http://www.work.psu.edu/cgi-bin/ldap/ldap_query.cgi',
                              formdata={'psdirid': psdirid,
                                        'full': '1',
                                        'submit': 'Full Result'},
                              callback=self.parse_person)

    def parse_person(self, response):
        # inspect_response(response, self)
        common_name = xp(response, 'Common Name:')
        last_name = xp(response, 'Last Name:')
        given_name = xp(response, 'Given Name:')
        name = response.xpath('//th[contains(text(), "Name")]/following-sibling::td//text()').extract_first()
        if name:
            name = name.strip()
            middle_name = name.split()[1]
        else:
            name = ''
            middle_name = ''

        email = xp(response, 'E-mail:')
        curriculum = xp(response, 'Curriculum:')
        mail_id = xp(response, 'Mail ID:')
        mailbox = xp(response, 'Mailbox:')
        userid = xp(response, 'Userid:')
        primary_affiliation = xp(response, 'EduPerson Primary Affiliation:')
        url = xp(response, 'URL:')
        address = xp(response, 'Address:')
        telephone = xp(response, 'Telephone Number:')
        title = xp(response, 'Title:')
        administrative_area = xp(response, 'Administrative Area:')
        department = xp(response, 'Department:')
        campus = xp(response, 'Campus:')
        office_address = xp(response, 'Office Address:')
        office_phone = xp(response, 'Office Phone:')

        if title:
            if 'undergrad' in title.lower():
                undergraduate = True
            else:
                undergraduate = False
        else:
            undergraduate = False

        if not undergraduate:
            yield {'common_name': common_name,
                   'middle_name': middle_name,
                   'last_name': last_name,
                   'given_name': given_name,
                   'name': name,
                   'email': email,
                   'curriculum': curriculum,
                   'mail_id': mail_id,
                   'mailbox': mailbox,
                   'userid': userid,
                   'primary_affiliation': primary_affiliation,
                   'url': url,
                   'address': address,
                   'telephone': telephone,
                   'title': title,
                   'administrative_area': administrative_area,
                   'department': department,
                   'campus': campus,
                   'office_address': office_address,
                   'office_phone': office_phone}
