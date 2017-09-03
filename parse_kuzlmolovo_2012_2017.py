#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import traceback
from functools import lru_cache

from pandas import DataFrame
from bs4 import BeautifulSoup
from requests import get


@lru_cache()
def get_html(url):
    for retry in range(1, 10):
        print('try %d get %s' % (retry, url))
        response = get(url)
        if response.status_code == 200 and response.text:
            soup = BeautifulSoup(response.text, 'html.parser')
            if soup.find('tbody', id='test'):
                return soup
    print('Max reties exceeded')
    sys.exit(1)


def get_cells(tr):
    return [x.text.strip() for x in tr.find_all('td')]


def parse_candidates(first_page):
    soup = get_html(first_page)
    page2_link = soup.find('a', text='2')
    if page2_link:
        page_urls = [first_page] + [x['href'] for x in page2_link.parent.find_all('a')]
    else:
        page_urls = [first_page]
    print('%d pages' % len(page_urls))

    data = []

    for page_url in page_urls:
        soup = get_html(page_url)
        try:
            new_data = [get_cells(x)[:7] for x in soup.find('tbody', id='test').find_all('tr')]
        except:
            traceback.print_exc()

        if new_data:
            print('... %s' % '\t'.join(new_data[-1]))
            data += new_data

    return DataFrame(data, columns=['ord', 'fio', 'bday', 'party', 'okrug', 'vidvinut', 'registr'])


kuz_2012 = 'http://www.leningrad-reg.vybory.izbirkom.ru/region/region/leningrad-reg?action=show&root=1&tvd=4474004224220&vrn=4474004224216&region=47&global=&sub_region=0&prver=0&pronetvd=null&vibid=4474004224216&type=220'
kuz_2017 = 'http://www.leningrad-reg.vybory.izbirkom.ru/region/region/leningrad-reg?action=show&root=1&tvd=4474004394931&vrn=4474004394927&region=47&global=&sub_region=0&prver=0&pronetvd=null&vibid=4474004394927&type=220'


dataframe = parse_candidates(kuz_2012)

with open('candidates-kuz-2012.csv', 'w+') as filee:
    filee.write(dataframe.set_index('ord').to_csv())

dataframe = parse_candidates(kuz_2017)

with open('candidates-kuz-2017.csv', 'w+') as filee:
    filee.write(dataframe.set_index('ord').to_csv())
