from urllib.parse import quote_plus as urlquote

import pandas as pd
import sqlalchemy
from sqlalchemy import inspect
from db_fund_io import engine


fund_info = {
    "013686": "华安安信消费服务混合C",
    "005765": "中欧明睿新常态C",
    "003096": "中欧医疗健康混合C",
    "163807": "中银行业优选",
    "012631": "中银行业优选C",
    "001618": "天弘中证电子C",
    "002340": "富国价值优势混合",
    "002482": "宝盈互联网",
    "110001": "易方达平稳增长混合",
    "450009": "国富中小盘股票",
    "450002": "国富弹性市值混合",
    "000217": "华安黄金"
}

fund_info_2 = {
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


def init_from_scratch(table_name):
    data = {"code": list(),
            "name": list(),
            "state": list(),
            "topic": list()
            }

    for k, v in fund_info.items():
        data["code"].append(k)
        data["name"].append(v)
        data["state"].append("观望")

    for k, v in fund_info_2.items():
        data["code"].append(k)
        data["name"].append(v)
        data["state"].append("持有")

    df = pd.DataFrame(data)
    df.sort_values(["state", "code"], inplace=True)
    df.to_sql(table_name, engine, if_exists="replace", index=False, dtype={
        'code': sqlalchemy.types.String(length=10),
        'name': sqlalchemy.types.Text,
        'state': sqlalchemy.types.String(length=10),
        'topic': sqlalchemy.types.String(length=10),
    })


def sort_fund_io(table_name):
    """
    对code_name_map表进行排序，排完后写回
    :return:
    :rtype:
    """
    df = pd.read_sql("code_name_map", engine)
    df.sort_values(["state", "code"], inplace=True)
    df.to_sql(table_name, engine, if_exists="replace", index=False, dtype={
        'code': sqlalchemy.types.String(length=10),
        'name': sqlalchemy.types.Text,
        'state': sqlalchemy.types.String(length=10),
        'topic': sqlalchemy.types.String(length=10),
    })
    return df


def main():
    table_name = "code_name_map"
    if not inspect(engine).has_table(table_name):
        init_from_scratch(table_name)
    else:
        sort_fund_io(table_name)


if __name__ == '__main__':
    main()


