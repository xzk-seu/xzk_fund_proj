from Fund import Fund


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
}


if __name__ == '__main__':
    for k, v in fund_info.items():
        print(k, v, "\n\n\n")
        fund = Fund(k, v)
        fund.forecasting(step=90)
        fund.validate()
