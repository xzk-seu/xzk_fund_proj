# coding=utf-8
from Fund import Fund

fund_info = {
    "519002": "华安安信消费服务混合",
    # "013686": "华安安信消费服务混合C",
    "001811": "中欧明睿新常态",
    "005765": "中欧明睿新常态C",
    "003095": "中欧医疗健康混合",
    "003096": "中欧医疗健康混合C",
    "163807": "中银行业优选",
    # "012631": "中银行业优选C",
    "001618": "天弘中证电子C",
    "002340": "富国价值优势混合",
    "002482": "宝盈互联网",
}


if __name__ == '__main__':
    for k, v in fund_info.items():
        print("\n", k, v)
        fund = Fund(k, v, result_dir="短期观望")
        fund.forecasting(step=90)
        fund.validate()
