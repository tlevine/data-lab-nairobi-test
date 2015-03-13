#!/usr/bin/env python2
'''
I followed this guide.
http://thomaslevine.com/!/web-sites-to-data-tables-in-depth/
'''
import os, sys
import datetime, argparse
from collections import OrderedDict

import requests, lxml.html
import googlesheets

url = 'http://www.uniraq.org/index.php?option=com_k2&view=item&id=3344:un-casualty-figures-for-february-2015&Itemid=633&lang=en'

def download():
    response = requests.get(url)
    html = lxml.html.fromstring(response.text)
    rows = html.xpath('//table/tbody/tr')
    data = [[td.text_content() for td in row.xpath('td')] for row in rows]
    head = data.pop(0)
    if head != ['Month', 'Killed', 'Injured']:
        msg = 'The website has changed; you should update the %s scraper script.'
        raise AssertionError(msg % __file__)

    metadata = OrderedDict([
        ('source', url),
        ('date of dataset', html.xpath('//span[@class="itemDateCreated"]/text()')[0].strip()),
        ('location', html.xpath('//div[@class="itemIntroText"]/p/text()')[0].partition(',')[0]),
        ('caveats', '\n'.join(html.xpath('//p[strong[contains(text(), "CAVEATS")]]/text()'))),
        ('comments', '')])
    return metadata, data


def upload(metadata, data, header = ['Date', 'Killed', 'Injured']):
    s = googlesheets.Spreadsheet.create('Casualty Figures')

    # Delete everything.
    while len(s.sheets) > 1:
        s.sheets[-1].delete()
    s.sheets[0].remove()
    
    data_sheet = s.sheets[0]
    data_sheet.title = 'Data'
    for month, killed, injured in data:
        date = datetime.datetime.strptime('1 %s' % month, '%d %B %Y')
        formatted_date = date.strftime('\'%Y/%m')
        data_sheet.insert(OrderedDict(zip(header, (month, killed, injured))))
        print('Data for %s has been written.' % month)

    metadata_sheet = s.create_sheet('Metadata')
    metadata_sheet.title = 'Metadata'
    metadata_sheet.insert(metadata)
    print('Metadata has been written.')

    return 'https://docs.google.com/spreadsheets/d/' + s.id

var_note = '''
You must set the "GOOGLE_USER" and "GOOGLE_PASSWORD" environment variables.
For example,

$ export GOOGLE_USER=thomas.levine@gmail.com
$ export GOOGLE_PASSWORD=0h23.uhrlcoe09u23b,rec,.e8hu23gde,..rhuoaruh2,rh.

You must also turn on support for less-secure apps.
https://www.google.com/settings/security/lesssecureapps
'''
def main():
    if not {'GOOGLE_USER', 'GOOGLE_PASSWORD'}.issubset(os.environ.keys()):
        sys.stderr.write(var_note)
        sys.exit(1)
    sys.stdout.write('Result is at %s.\n' % upload(*download()))

if __name__ == '__main__':
    try:
        main()
    except ImportError:
        sys.stderr.write('Install requirements from requirements.txt\n.')
