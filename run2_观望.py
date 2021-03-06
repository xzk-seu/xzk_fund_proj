# coding=utf-8
from Fund import Fund

fund_info = {
    "002168": "嘉实智能汽车股票",
    "002340": "富国价值优势混合",
    "519002": "华安安信消费服务混合",
    "013686": "华安安信消费服务混合C",
    "001811": "中欧明睿新常态",
    "005765": "中欧明睿新常态C",
    "001166": "建信环保产业",
    "003095": "中欧医疗健康混合",
    "003096": "中欧医疗健康混合C",
    "110013": "易方达科翔混合",
    "160221": "国泰国证有色金属",
    "163807": "中银行业优选",
    "012631": "中银行业优选C",
    "002482": "宝盈互联网",
    "001018": "易方达新经济灵活配置",
    "001618": "天弘中证电子C",
}


if __name__ == '__main__':
    for k, v in fund_info.items():
        print("\n", k, v)
        fund = Fund(k, v, result_dir="观望")
        fund.forecasting(step=90)
        fund.validate()
