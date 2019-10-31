import os
import re
import json
import requests
from lxml import html
from datetime import datetime

base_url = 'https://www.jadwalsholat.org/adzan/monthly.php'


def strip_lower(str):

    return re.sub(r'\W+', '', str).lower()


def get_districts() :

    first_page = requests.get(base_url)
    first_page_doc = html.fromstring(first_page.content)

    district_ids = first_page_doc.xpath('//select[@name="kota"]/option/@value')
    district_names = first_page_doc.xpath('//select[@name="kota"]/option/text()')
    district_names = [strip_lower(d) for d in district_names]

    return dict(zip(district_ids, district_names))


def get_adzans(district_id, month = '', year = '') :

    if  month == '' :
        month = datetime.now().month

    if  year == '' :
        year = datetime.now().year

    url = base_url + '?id={}&m={}&y={}'.format(district_id, month, year)

    page = requests.get(url)

    doc = html.fromstring(page.content)

    rows = doc.xpath('//tr[contains(@class, "table_light") or contains(@class, "table_dark") or contains(@class, "table_highlight")]')

    result = []

    for row in rows:
        data = row.xpath('td//text()')
        result.append({
            'tanggal': '{}-{}-{}'.format(year, month, data[0]),
            'imsyak': data[1],
            'shubuh': data[2],
            'terbit': data[3],
            'dhuha': data[4],
            'dzuhur': data[5],
            'ashr': data[6],
            'magrib': data[7],
            'isya': data[8]
        })

    return result


def write_file(district, adzans):

    for adzan in adzans:
        dt = adzan['tanggal'].replace('-', '/')

        fld = 'adzan/'+district+'/'+dt[:8]
        if not os.path.exists(fld):
            os.makedirs(fld, mode=0o777)

        fl = open(fld+dt[8::]+'.json', 'w+')
        fl.write(json.dumps(adzan))
        fl.close()


def main():

    districts = get_districts()

    for id, name in districts.items():
        print('processing ' + name)
        write_file(name, get_adzans(id, '11', '2019'))


if __name__ == "__main__":
    main()