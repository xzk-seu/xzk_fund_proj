import pandas as pd
from sqlalchemy import create_engine
import sqlalchemy
from Fund import Fund
from urllib.parse import quote_plus as urlquote


user = "root"
password = "his@9000"
address = "localhost"
port = "3306"
database = "fund"
engine = create_engine(f'mysql+pymysql://{user}:{urlquote(password)}@{address}:{port}/{database}')


def create():
    fund = Fund("001549", "上证50",
                result_dir="unit_test")
    fund.df.to_sql("fund_info/001549", engine, if_exists="replace", index=False,
                   dtype={'Code': sqlalchemy.types.String(length=10),
                          "Date": sqlalchemy.types.Date}
                   )
    df = pd.read_sql('fund_info/001549', engine)

    return df


if __name__ == '__main__':
    create()
