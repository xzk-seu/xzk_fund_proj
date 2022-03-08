# coding=utf-8
from Fund import Fund
import pandas as pd
from db_fund_io import engine

if __name__ == '__main__':
    res = {"code": list(),
           "name": list(),
           "time": list(),
           "flag": list(),
           "upper_bound": list(),
           "lower_bound": list(),
           "state": list(),
           "topic": list()}
    df = pd.read_sql("code_name_map", engine)
    for _, k, v, state, topic in df.itertuples():
        print("\n", k, v)
        fund = Fund(k, v, result_dir=state)
        fund.boll()
        res["code"].append(k)
        res["name"].append(v)
        res["time"].append(fund.fund_info_table.nearest_date)
        res["flag"].append(fund.boll_band.conclusion)
        res["upper_bound"].append(fund.boll_band.upper_bound)
        res["lower_bound"].append(fund.boll_band.lower_bound)
        res["state"].append(state)
        res["topic"].append(topic)
    df = pd.DataFrame(res)
    df.sort_values(by=["state", "flag"], ascending=[True, False], inplace=True)
    df.to_csv("boll_res.csv", index=False)
    df.to_sql("boll_res", engine, if_exists="replace", index=False)
