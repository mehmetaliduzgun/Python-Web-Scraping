import pandas as pd
import requests
from bs4 import BeautifulSoup


companies = ["FROTO"]
is_yatirim_url = 'https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/sirket-karti.aspx?hisse=FROTO'
r = requests.get(is_yatirim_url)
s = BeautifulSoup(r.text, 'html.parser')
s1 = s.find('select', id='ddlAddCompare')
c1 = s1.findChild('optgroup').findAll('option')
#for company in c1:  if you want to get all of the companies you can delete the hashtag and companies list will contain all of them
#   companies.append(company.string)
for i in companies:
    company = i
    dates = []
    years = []
    periods = []
    url1 = 'https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/sirket-karti.aspx?hisse=' + company
    r1 = requests.get(url1)
    soup = BeautifulSoup(r1.text, 'html.parser')
    choice1 = soup.find('select', id='ddlMaliTabloFirst')
    choice2 = soup.find('select', id='ddlMaliTabloGroup')
    try:
        children_dates = choice1.findChildren('option')
        group = choice2.find('option')['value']
        for date in children_dates:
            dates.append((date.string.rsplit('/')))
        for date in dates:
            years.append(date[0])
            periods.append(date[1])
        if len(dates) >= 4:
            parameters = (
                ('companyCode', company),
                ('exchange', 'TRY'),
                ('financialGroup', group),
                ('year1', years[0]),
                ('period1', periods[0]),
                ('year2', years[1]),
                ('period2', periods[1]),
                ('year3', years[2]),
                ('period3', periods[2]),
                ('year4', years[3]),
                ('period4', periods[3])
            )

            url2 = 'https://www.isyatirim.com.tr/_layouts/15/IsYatirim.Website/Common/Data.aspx/MaliTablo'
            r2 = requests.get(url2, params=parameters).json()["value"]
            data = pd.DataFrame.from_dict(r2)
            data.drop(columns=["itemCode", "itemDescEng"], inplace=True)
        else: continue
    except AttributeError:
        continue

    del dates[0:4]
    all_datas = [data]

    for i in range(0, int(len(dates)+1)):
        if len(dates) == len(years):
            del dates[0:4]
        else:
            years = []
            periods = []

            for date in dates:
                years.append(date[0])
                periods.append((date[1]))

            if len(dates)>=4:
                parameters2 = (
                    ('companyCode', company),
                    ('exchange', 'TRY'),
                    ('financialGroup', group),
                    ('year1', years[0]),
                    ('period1', periods[0]),
                    ('year2', years[1]),
                    ('period2', periods[1]),
                    ('year3', years[2]),
                    ('period3', periods[2]),
                    ('year4', years[3]),
                    ('period4', periods[3])
                )

                r3 = requests.get(url2, params=parameters2).json()["value"]
                data2 = pd.DataFrame.from_dict(r3)
                try:
                    data2.drop(columns=["itemCode","itemDescTr", "itemDescEng"], inplace=True)
                    all_datas.append(data2)
                except KeyError:
                    continue
    data3 = pd.concat(all_datas, axis=1)
    headers = ["Bilanço"]
    for date in children_dates:
        headers.append(date.string)
    headers_difference = len(headers)-len(data3.columns)
    if headers_difference != 0:
        del headers[-headers_difference:]
    data3.set_axis(headers, axis=1, inplace=True)
    data3.to_excel("/Users/mehmetaliduzgun/Desktop/Data Science/Financial Reports/{}.xlsx".format(company), index=False)
