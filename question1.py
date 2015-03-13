'''
A. You are requested to extract data from the
`UN Iraq website <http://www.uniraq.org/index.php?option=com_k2&view=item&id=3344:un-casualty-figures-for-february-2015&Itemid=633&lang=en>_`.
Please create a table in a 
google spreadsheet that contains the casualty figures from November 2012 to 
February 2015. Your extraction should be done programmatically (coded) to respond 
to updates of the website (ie, it should be robust enough to react to changes of the 
past estimates and to incorporate new estimates (March 2015). 

B. Your resulting dataset should also contain the following metadata fields: source, 
methodology, date of dataset, location, caveats and comments.

I followed this guide.
http://thomaslevine.com/!/web-sites-to-data-tables-in-depth/
'''
import datetime

import requests, lxml.html

url = 'http://www.uniraq.org/index.php?option=com_k2&view=item&id=3344:un-casualty-figures-for-february-2015&Itemid=633&lang=en'

def download():
    response = requests.get(url)
    html = lxml.html.fromstring(response.text)
    rows = html.xpath('//table/tbody/tr')
    head, *body = [[td.text_content() for td in row.xpath('td')] for row in rows]
    if head != ['Month', 'Killed', 'Injured']:
        msg = 'The website has changed; you should update the %s scraper script.'
        raise AssertionError(msg % __file__)
    return body

def format_table(body, header = ['Date', 'Killed', 'Injured']):
    yield header
    for month, killed, injured in body:
        date = datetime.datetime.strptime('1 %s' % month, '%d %B %Y').strftime('%Y/%m')
        yield date, killed, injured

def main():
    list(format_table(download()))
