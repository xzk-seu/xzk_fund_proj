# coding=utf-8
from Fund import Fund
import pandas as pd
from db_fund_io import engine

if __name__ == '__main__':
    res = {"code": list(),
           "name": list(),
           "time": list(),
           "flag": list(),
           "threshold": list(),
           "state": list()}
    df = pd.read_sql("code_name_map", engine)
    for _, k, v, state in df.itertuples():
        print("\n", k, v)
        fund = Fund(k, v, result_dir=state)
        flag, threshold = fund.boll()
        res["code"].append(k)
        res["name"].append(v)
        res["time"].append(fund.timestamp)
        res["flag"].append(flag)
        res["threshold"].append(threshold)
        res["state"].append(state)
    df = pd.DataFrame(res)
    df.sort_values(by=["state", "threshold"], ascending=[True, True], inplace=True)
    df.to_csv("boll_res.csv", index=False)
    df.to_sql("boll_res", engine, if_exists="replace", index=False)
