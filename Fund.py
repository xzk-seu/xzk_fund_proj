# coding=utf-8
from spider import get_records
from datetime import date
import pandas as pd
import os
import matplotlib.pyplot as plt
from plot import plot

from kats.models.prophet import ProphetModel, ProphetParams
from kats.consts import TimeSeriesData


TODAY = str(date.today())
DATA_PATH = os.path.join(os.getcwd(), "data")
RES_PATH = os.path.join(os.getcwd(), "result")
GRAPH_PATH = os.path.join(os.getcwd(), "graph")
PATH_LIST = [DATA_PATH, RES_PATH, GRAPH_PATH]
for p in PATH_LIST:
    if not os.path.exists(p):
        os.makedirs(p)


class Fund:
    def __init__(self, code="0", description="", timestamp=TODAY):
        self.code = code
        self.description = description
        self.records = None
        self.df = pd.DataFrame()
        self.timestamp = timestamp
        self.file_name = "%s_%s_%s" % (self.code, self.description, self.timestamp)
        self.fcst = None
        self.valid = None

    def get_fund_data(self, begin="2001-01-01", end=TODAY):
        data_path = os.path.join(DATA_PATH, "%s.csv" % self.file_name)
        if os.path.exists(data_path):
            print("%s \n is already existed!" % data_path)
            self.df = pd.read_csv(data_path)
            return self.df
        self.records = get_records(self.code, begin, end)
        self.df = pd.DataFrame(self.records)
        self.df.to_csv(data_path)
        self.df = pd.read_csv(data_path)
        return self.df

    def forecasting(self, step=65):
        if self.df.empty:
            self.get_fund_data()
        df = self.df[["Date", "NetAssetValue"]]
        df.columns = ["time", "value"]
        self.fcst = self.predict(df, step=step)

    def validate(self, valid_num=65, pred_step=65):
        """

        :param pred_step:
        :param valid_num: 用来验证的数据条数
        :return:
        """
        if self.df.empty:
            self.get_fund_data()
        df = self.df[["Date", "NetAssetValue"]]
        df.columns = ["time", "value"]
        self.valid = self.predict(df, step=pred_step, valid_num=valid_num)

    def predict(self, his_data, step=65, valid_num=None):
        file_name = self.file_name + "_fcst"   # 结果保存的文件名
        if valid_num:
            file_name = file_name+"_valid"
            step += valid_num
            ts = TimeSeriesData(his_data[valid_num:])
        else:
            ts = TimeSeriesData(his_data)

        params = ProphetParams(seasonality_mode='multiplicative')  # additive mode gives worse results

        # create a prophet model instance
        m = ProphetModel(ts, params)
        m.fit()

        fcst = m.predict(steps=step, freq="B")

        res_path = os.path.join(RES_PATH, "%s.csv" % file_name)
        # graph_path = os.path.join(GRAPH_PATH, "%s.svg" % file_name)
        fcst.to_csv(res_path)

        fig = plot(his_data.head(250), fcst, include_history=True, title=file_name)
        # fig.savefig(graph_path, format='svg')

        graph_path = os.path.join(GRAPH_PATH, "%s.png" % file_name)
        fig.savefig(graph_path, format='png')

        plt.show()
        return fcst


if __name__ == '__main__':
    fund = Fund("001549", "上证50")
    d = fund.get_fund_data()
    print(d.head())
    fund.forecasting()
    fund.validate()
