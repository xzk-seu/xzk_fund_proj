from urllib.parse import quote_plus as urlquote

import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, select, func, MetaData, Table, Column, inspect

user = "root"
password = "his@9000"
address = "localhost"
port = "3306"
database = "fund_io"
engine = create_engine(f'mysql+pymysql://{user}:{urlquote(password)}@{address}:{port}/{database}')


def sort_fund_io():
    """
    对code_name_map表进行排序，排完后写回
    :return:
    :rtype:
    """
    df = pd.read_sql("code_name_map", engine)
    df.sort_values(["state", "code"], inplace=True)
    df.to_sql("code_name_map", engine, if_exists="replace", index=False, dtype={
        'code': sqlalchemy.types.String(length=10),
        'name': sqlalchemy.types.Text,
        'state': sqlalchemy.types.String(length=10),
    })
    return df


def get_fund_info():
    df = pd.read_sql("code_name_map", engine)
    for _, k, v in df.itertuples():
        print(k, v)
        print(type(k), type(v))


if __name__ == '__main__':
    d = sort_fund_io()
    print(d)
