# -*- coding: utf-8 -*-
import re
import json
from time import sleep
from scrapy import Spider
from selenium import webdriver
from scrapy.selector import Selector
from scrapy.shell import inspect_response
from scrapy.http import Request, FormRequest
from scrapy.utils.response import open_in_browser


class OuSpider(Spider):
    name = 'ou'
    # start_urls = ['https://webapps.ou.edu/common/services/searchServices.cfc?callback=jQuery112408144499212139631_1531864722002&method=person&primaryid=476413']
    # start_urls = ['https://webapps.ou.edu/common/services/searchServices.cfc?callback=jQuery112408144499212139631_1531864722002&method=person&primaryid=488385']
    start_urls = []
    for number in range(488385, 490000):
        start_urls.append('https://webapps.ou.edu/common/services/searchServices.cfc?callback=jQuery112408144499212139631_1531864722002&method=person&primaryid=' + str(number))

    def parse(self, response):
        # inspect_response(response, self)
        # open_in_browser(response)

        response_text = str(response.body)
        response_text = response_text.strip()
        response_text = response_text.replace('jQuery112408144499212139631_1531864722002 (', '')
        response_text = response_text.replace('\r', '')
        response_text = response_text.replace('\n', '')
        response_text = response_text.replace('\t', '')
        response_text = response_text.replace('\\r', '')
        response_text = response_text.replace('\\n', '')
        response_text = response_text.replace('\\t', '')
        response_text = response_text.replace(';', '')
        response_text = response_text.replace("'b\'", '')
        response_text = response_text.replace("\'", '')
        response_text = response_text.strip()
        response_text = response_text[1:-1]

        jsonresponse = json.loads(response_text)

        if jsonresponse['person'][0]['alias']:
            email = jsonresponse['person'][0]['alias'] + '@ou.edu'

        stuclass = jsonresponse['person'][0]['stuclass']
        if stuclass:
            if 'undergraduate' in stuclass.lower() or 'freshman' in stuclass.lower() or 'sophomore' in stuclass.lower() or 'junior' in stuclass.lower() or 'senior' in stuclass.lower():
                undergraduate = True
            else:
                undergraduate = False
        else:
            undergraduate = False

        if not undergraduate:
            yield {'alias': jsonresponse['person'][0]['alias'],
                   'caddr': jsonresponse['person'][0]['caddr'],
                   'col': jsonresponse['person'][0]['col'],
                   'cphone': jsonresponse['person'][0]['cphone'],
                   'dept': jsonresponse['person'][0]['dept'],
                   'deptDept': jsonresponse['person'][0]['deptDept'],
                   'deptTitle': jsonresponse['person'][0]['deptTitle'],
                   'fname': jsonresponse['person'][0]['fname'],
                   'gen': jsonresponse['person'][0]['gen'],
                   'haddr': jsonresponse['person'][0]['haddr'],
                   'hphone': jsonresponse['person'][0]['hphone'],
                   'lname': jsonresponse['person'][0]['lname'],
                   'loc': jsonresponse['person'][0]['loc'],
                   'mname': jsonresponse['person'][0]['mname'],
                   'ophone': jsonresponse['person'][0]['ophone'],
                   'stuclass': stuclass,
                   'title': jsonresponse['person'][0]['title'],
                   'url1': jsonresponse['person'][0]['url1'],
                   'email': email}
