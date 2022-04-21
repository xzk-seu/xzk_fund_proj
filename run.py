# coding=utf-8
from Fund import Fund
import pandas as pd
from db_fund_io import engine


if __name__ == '__main__':
    df = pd.read_sql("code_name_map", engine)
    for _, k, v, state, topic in df.itertuples():
        if state not in ["持有", "定投"]:
            continue
        print("\n", k, v)
        fund = Fund(k, v, result_dir=state)
        fund.forecasting(step=90)
        fund.validate()
