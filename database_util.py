import datetime
from datetime import date
from urllib.parse import quote_plus as urlquote

import pandas as pd
import sqlalchemy
from chinese_calendar import is_workday
from sqlalchemy import create_engine, select, func, MetaData, Table, Column, inspect

from spider import get_records

user = "root"
password = "his@9000"
address = "localhost"
port = "3306"
database = "fund"
engine = create_engine(f'mysql+pymysql://{user}:{urlquote(password)}@{address}:{port}/{database}')


def get_newest_value_date():
    """
    根据当前时间判断净值是否更新，若更新返回今天的日期，否则返回上个交易日的日期
    :return:
    :rtype:
    """

    def is_trade_day(d):
        if is_workday(d) and n_time.isoweekday() < 6:
            return True
        return False

    # 范围时间
    d_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '20:30', '%Y-%m-%d%H:%M')
    # 当前时间
    n_time = datetime.datetime.now()

    if is_trade_day(n_time) and d_time < n_time:
        print("今日基金净值已更新")
        return n_time.date()
    else:
        print("今日未更新，或今日不是交易日，以上一个交易日为净值获取截止时间\n")
        n_time += datetime.timedelta(days=-1)
        while not is_trade_day(n_time):
            n_time += datetime.timedelta(days=-1)
        return n_time.date()


newest_value_date = get_newest_value_date()


class FundInfoTable:
    def __init__(self, code):
        self.code = code
        self.table_name = 'fund_info/%s' % code
        self.nearest_date = None
        self.dtype = {
            'Code': sqlalchemy.types.String(length=10),
            'Date': sqlalchemy.types.Date,
            'NetAssetValue': sqlalchemy.types.Float,
            'ChangePercent': sqlalchemy.types.Text
        }
        metadata_obj = MetaData()
        self.table_schema = Table(self.table_name, metadata_obj,
                                  Column('Code', sqlalchemy.types.String(length=10)),
                                  Column('Date', sqlalchemy.types.Date),
                                  Column('NetAssetValue', sqlalchemy.types.Float),
                                  Column('ChangePercent', sqlalchemy.types.Text),
                                  )
        if not inspect(engine).has_table(self.table_name):
            records = get_records(self.code, start="2001-01-01", end=str(date.today()))
            df = pd.DataFrame(records)
            df.to_sql(self.table_name, engine, if_exists="replace", index=False, dtype=self.dtype)
        self.nearest_date = self.get_nearest_date()

    def get_nearest_date(self):
        """
        获取数据库中最近的一天
        :return:
        :rtype:
        """
        stmt = select(func.max(self.table_schema.columns.Date))
        df = pd.read_sql(stmt, engine)
        max_date = df.iloc[0]
        max_date = max_date[0]
        return max_date

    def get_data_from_sql(self):
        """
        由外部调用的接口
        :return:
        :rtype:
        """
        if self.nearest_date != newest_value_date:
            start = str(self.nearest_date + datetime.timedelta(1))
            records = get_records(self.code, start=start, end=str(date.today()))
            df = pd.DataFrame(records)
            if df.shape[1] > 1:  # 当前日期为空时会插入只有code列的空值
                df.to_sql(self.table_name, engine, if_exists="append", index=False, dtype=self.dtype)
                self.nearest_date = self.get_nearest_date()
        stmt = select(self.table_schema).order_by(self.table_schema.c.Date.desc())
        data = pd.read_sql(stmt, engine)
        return data

    def re_rank(self):
        data = self.get_data_from_sql()
        data.to_sql(self.table_name, engine, if_exists="replace", index=False, dtype=self.dtype)

    def run(self):
        if inspect(engine).has_table(self.code):
            self.nearest_date = self.get_nearest_date()
            if self.nearest_date != newest_value_date:
                records = get_records(self.code, start=str(self.nearest_date), end=str(date.today()))
                df = pd.DataFrame(records)
                df.to_sql(self.table_name, engine, if_exists="append", index=False, dtype=self.dtype)
                print(df)


if __name__ == '__main__':
    f = FundInfoTable("001811")
    d = f.get_data_from_sql()
    print(d)
