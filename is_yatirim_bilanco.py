import pandas as pd
import requests
from bs4 import BeautifulSoup
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler


def download_financials_excel(companies: list, exchange="TRY"):
    """
    Downloads all the possible annual financial reports for all quarter periods
    :param companies: A list of including the company codes that you want to create financial reports of them
    :param exchange: TRY or USD for which one you want to see the financials with currency
    :return: A report that customized for your parameters.
    """
    for company in companies:
        data3, company_statistics = process_data(company, exchange)
        create_report(company, data3, company_statistics, exchange)


def process_data(company, exchange):
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
                ('exchange', exchange),
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
        else:
            return None, None
    except AttributeError:
        return None, None

    del dates[0:4]
    all_datas = [data]

    for i in range(0, int(len(dates) + 1)):
        if len(dates) == len(years):
            del dates[0:4]
        else:
            years = []
            periods = []

            for date in dates:
                years.append(date[0])
                periods.append((date[1]))

            if len(dates) >= 4:
                parameters2 = (
                    ('companyCode', company),
                    ('exchange', exchange),
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
                    data2.drop(columns=["itemCode", "itemDescTr", "itemDescEng"], inplace=True)
                    all_datas.append(data2)
                except KeyError:
                    continue
    data3 = pd.concat(all_datas, axis=1)
    headers = ["Bilanço"]
    for date in children_dates:
        headers.append(date.string)
    headers_difference = len(headers) - len(data3.columns)
    if headers_difference != 0:
        del headers[-headers_difference:]
    data3.set_axis(headers, axis=1, inplace=True)
    data3 = data3.T
    data3.reset_index(drop=True, inplace=True)
    data3.columns = data3.iloc[0]
    data3.set_index(pd.Index(headers), drop=True, inplace=True)
    data3.drop(data3.index[0], inplace=True)
    # data3.index.name = "Bilanço Dönemleri" An interesting error, I will check it later.
    data3.to_excel("/Users/mehmetaliduzgun/Desktop/Data Science/Financial Reports/{}.xlsx".format(company), index=False)
    company_statistics = data3.describe().T
    plt.figure(figsize=(55, 10))
    scaler = MinMaxScaler()
    data3_scaled = scaler.fit_transform(data3[data3.columns[0]].values.reshape(-1, 1))
    data3_scaled_df = pd.DataFrame(data3_scaled)
    sns.scatterplot(data=data3, x=data3.index.values, y=data3_scaled_df[0], s=50)
    plt.savefig('chart_{}_{}.png'.format(company, exchange))
    return data3, company_statistics


def create_report(company, data3, company_statistics, exchange):
    page_title = "Custom Report"
    report_title = "{} Company Financial Report for {} Exchange".format(company, exchange)
    text = "Welcome to our report. For more customizable reports, you can follow us!"
    prices_text = "BIST 100 {} Company Historical Financial Reports by Periods".format(company)
    stats_text = "BIST 100 {} Company Historical Financials Summary Statistics".format(company)

    html = f"""
        <html>
            <head>
                <title>{page_title}</title>
            </head>
            <body>
                <h1>{report_title}</h1>
                <p>{text}</p>
                <img src = 'chart_{company}_{exchange}.png'>
                <h2>{prices_text}</h2>
                {data3.iloc[0:data3.shape[0]-1, 0:5].to_html()}
                <h2>{stats_text}</h2>
                {company_statistics.to_html()}
            </body>
        </html>
        """

    with open('{}_{}_report.html'.format(company, exchange), 'w') as file:
        file.write(html)



download_financials_excel(["FROTO"], "TRY")
