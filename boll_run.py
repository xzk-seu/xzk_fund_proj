# coding=utf-8
from Fund import Fund
import pandas as pd

fund_info = {
    "002979": "广发金融地产",
    "001549": "天弘上证50",
    "005918": "天弘沪深300",
    "001595": "天弘中证银行",
    "001551": "天弘中证医药100",
    "161725": "招商中证白酒",
    "001593": "天弘创业板",
    "001632": "天弘中证食品饮料",
    "070039": "嘉实中证500",
    "002903": "广发中证500",
    "002987": "广发沪深300"
}

if __name__ == '__main__':
    res = {"code": list(),
           "name": list(),
           "time": list(),
           "flag": list(),
           "threshold": list()}
    for k, v in fund_info.items():
        print("\n", k, v)
        fund = Fund(k, v, result_dir="持有")
        flag, threshold = fund.boll()
        res["code"].append(k)
        res["name"].append(v)
        res["time"].append(fund.timestamp)
        res["flag"].append(flag)
        res["threshold"].append(threshold)
        df = pd.DataFrame(res)
        df.to_csv("boll.csv", index=False)
