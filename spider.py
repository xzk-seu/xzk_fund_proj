import pandas as pd
import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable
from tqdm import tqdm

from from_soup_get_page import from_soup_get_page


def get_url(url, params=None, proxies=None):
    rsp = requests.get(url, params=params, proxies=proxies)
    rsp.raise_for_status()
    return rsp.text


def get_fund_data(code, start='', end='', page=1):
    record = {'Code': code}
    url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx'
    params = {'type': 'lsjz', 'code': code, 'page': page, 'per': 49, 'sdate': start, 'edate': end}
    html = get_url(url, params)
    soup = BeautifulSoup(html, 'html.parser')
    records = []
    tab = soup.findAll('tbody')[0]
    for tr in tab.findAll('tr'):
        if tr.findAll('td') and len((tr.findAll('td'))) == 7:
            record['Date'] = str(tr.select('td:nth-of-type(1)')[0].getText().strip())
            record['NetAssetValue'] = str(tr.select('td:nth-of-type(2)')[0].getText().strip())
            record['ChangePercent'] = str(tr.select('td:nth-of-type(4)')[0].getText().strip())
        records.append(record.copy())
    page_num = None
    if page == 1:
        page_num = from_soup_get_page(soup)
    return page_num, records


def get_records(code, start, end):
    page_num, records = get_fund_data(code, start, end)
    for curpage in tqdm(range(2, page_num + 1)):
        _, temp = get_fund_data(code, start, end, curpage)
        records.extend(temp)
    return records


def demo(code, start, end):
    table = PrettyTable()

    table.field_names = ['Code', 'Date', 'NAV', 'Change']

    table.align['Change'] = 'r'

    records = get_records(code, start, end)

    for record in records:
        table.add_row([record['Code'], record['Date'], record['NetAssetValue'], record['ChangePercent']])

    df = pd.DataFrame(records)
    df.to_csv("shangzheng50.csv")
    return table


if __name__ == "__main__":
    # print(demo('002979', '2001-06-22', '2021-08-31')) # jinrong
    print(demo('001549', '2022-03-03', '2022-03-03'))  # shangzheng50
