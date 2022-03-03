# coding=utf-8
import os
from datetime import date
from pandas.api.indexers import FixedForwardWindowIndexer
import matplotlib.pyplot as plt
import pandas as pd
from kats.consts import TimeSeriesData
from kats.models.prophet import ProphetModel, ProphetParams

from plot import plot
from spider import get_records
TODAY = str(date.today())


def reset_path(result_dir):
    data_path = os.path.join(os.getcwd(), result_dir, TODAY, "data")
    res_path = os.path.join(os.getcwd(), result_dir, TODAY, "result")
    graph_path = os.path.join(os.getcwd(), result_dir, TODAY, "graph")
    path_list = [data_path, res_path, graph_path]
    for p in path_list:
        if not os.path.exists(p):
            os.makedirs(p)
    return data_path, res_path, graph_path


class Fund:
    def __init__(self, code="0", description="", timestamp=TODAY,
                 result_dir=None):
        self.data_path, self.res_path, self.graph_path = reset_path(result_dir)
        self.code = code
        self.description = description
        self.records = None
        self.df = pd.DataFrame()
        self.timestamp = timestamp
        self.file_name = "%s_%s_%s" % (self.code, self.description, self.timestamp)
        self.fcst = None
        self.valid = None
        if self.df.empty:
            self.get_fund_data()

    def get_fund_data(self, begin="2001-01-01", end=TODAY):
        data_path = os.path.join(self.data_path, "%s.csv" % self.file_name)
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
        file_name = self.file_name + "_fcst"  # 结果保存的文件名
        if valid_num:
            file_name = file_name + "_valid"
            step += valid_num
            ts = TimeSeriesData(his_data[valid_num:])
        else:
            ts = TimeSeriesData(his_data)

        params = ProphetParams(seasonality_mode='multiplicative')  # additive mode gives worse results

        # create a prophet model instance
        m = ProphetModel(ts, params)
        m.fit()

        fcst = m.predict(steps=step, freq="B")

        res_path = os.path.join(self.res_path, "%s.csv" % file_name)
        """
        # graph_path = os.path.join(GRAPH_PATH, "%s.svg" % file_name)
        """
        fcst.to_csv(res_path)

        fig = plot(his_data.head(250), fcst, include_history=True, title=file_name)
        # fig.savefig(graph_path, format='svg')

        graph_path = os.path.join(self.graph_path, "%s.png" % file_name)
        fig.savefig(graph_path, format='png')

        plt.show()
        return fcst

    def boll(self, window=20):
        data = self.df[["Date", "NetAssetValue"]]
        data.columns = ["time", "value"]
        data = data.head(100)
        roll = data["value"].rolling(FixedForwardWindowIndexer(window_size=window))
        std = roll.std()
        mean = roll.mean()
        data["std"] = std
        data["mean"] = mean
        data["high"] = mean + 2 * std
        data["low"] = mean - 2 * std
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        fig = plt.figure(facecolor="w", figsize=(10, 6))
        # plt.title(title)
        title = self.file_name
        fig.suptitle(title)
        ax = fig.add_subplot(111)
        ax.plot(pd.to_datetime(data.time), data.value, "k")
        ax.plot(pd.to_datetime(data.time), data['mean'], )
        ax.plot(pd.to_datetime(data.time), data["high"], )
        ax.plot(pd.to_datetime(data.time), data["low"], )

        ax.grid(True, which="major", c="gray", ls="-", lw=1, alpha=0.2)
        ax.set_xlabel(xlabel="time")

        flag = "None"
        res = data.iloc[0]
        if res["value"] > res["high"]:
            flag = "high"
        elif res["value"] < res["low"]:
            flag = "low"

        ax.text(res["time"], res["value"], flag, size=24)

        fig.tight_layout()
        plt.show()


if __name__ == '__main__':
    fund = Fund("001549", "上证50", result_dir="持有")
    d = fund.get_fund_data()
    print(d.head())
    fund.boll()
    fund.forecasting()
    fund.validate()
