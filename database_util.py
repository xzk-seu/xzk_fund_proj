import datetime
from datetime import date
from urllib.parse import quote_plus as urlquote

import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, select, func, MetaData, Table, Column, inspect

from spider import get_records

user = "root"
password = "his@9000"
address = "localhost"
port = "3306"
database = "fund"
engine = create_engine(f'mysql+pymysql://{user}:{urlquote(password)}@{address}:{port}/{database}')


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

    def get_nearest_date(self):
        """
        获取数据库中最近的一天
        :return:
        :rtype:
        """
        if not inspect(engine).has_table(self.table_name):
            return
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
        if not inspect(engine).has_table(self.table_name) or self.get_nearest_date() != date.today():
            nearest_date = self.get_nearest_date()
            start = str(nearest_date+datetime.timedelta(1)) if nearest_date else "2001-01-01"
            records = get_records(self.code, start=start, end=str(date.today()))
            df = pd.DataFrame(records)
            if df.shape[1] > 1:  # 当前日期为空时会插入只有code列的空值
                df.to_sql(self.table_name, engine, if_exists="append", index=False, dtype=self.dtype)
        stmt = select(self.table_schema).order_by(self.table_schema.c.Date.desc())
        data = pd.read_sql(stmt, engine)
        return data

    def re_rank(self):
        data = self.get_data_from_sql()
        data.to_sql(self.table_name, engine, if_exists="replace", index=False, dtype=self.dtype)

    def run(self):
        if inspect(engine).has_table(self.code):
            self.nearest_date = self.get_nearest_date()
            if self.nearest_date != date.today():
                records = get_records(self.code, start=str(self.nearest_date), end=str(date.today()))
                df = pd.DataFrame(records)
                df.to_sql(self.table_name, engine, if_exists="append", index=False, dtype=self.dtype)
                print(df)


if __name__ == '__main__':
    f = FundInfoTable("001811")
    d = f.get_data_from_sql()
    print(d)
