# coding=utf-8
import os
from datetime import date
from pandas.api.indexers import FixedForwardWindowIndexer
import matplotlib.pyplot as plt
import pandas as pd
from kats.consts import TimeSeriesData
from kats.models.prophet import ProphetModel, ProphetParams
from database_util import FundInfoTable

from plot import plot
from spider import get_records
TODAY = str(date.today())


class Fund:
    def __init__(self, code="0", description="", timestamp=TODAY,
                 result_dir=None):
        self.timestamp = timestamp
        self.boll_path, self.res_path, self.graph_path = self.reset_path(result_dir)
        self.code = code
        self.description = description
        self.records = None
        self.df = pd.DataFrame()
        self.file_name = "%s_%s_%s" % (self.code, self.description, self.timestamp)
        self.fcst = None
        self.valid = None
        self.init_data_from_sql()

    def reset_path(self, result_dir):
        boll_path = os.path.join(os.getcwd(), "boll")
        res_path = os.path.join(os.getcwd(), result_dir, self.timestamp, "result")
        graph_path = os.path.join(os.getcwd(), result_dir, self.timestamp, "graph")
        path_list = [boll_path, res_path, graph_path]
        for p in path_list:
            if not os.path.exists(p):
                os.makedirs(p)
        return boll_path, res_path, graph_path

    def init_data_from_sql(self):
        fund_info_table = FundInfoTable(self.code)
        self.df = fund_info_table.get_data_from_sql()

    def forecasting(self, step=65):
        df = self.df[["Date", "NetAssetValue"]]
        df.columns = ["time", "value"]
        self.fcst = self.predict(df, step=step)

    def validate(self, valid_num=65, pred_step=65):
        """

        :param pred_step:
        :param valid_num: 用来验证的数据条数
        :return:
        """
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
        fcst.to_csv(res_path, index=False)

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

        def _get_flag(last_data):
            f = "None"
            value = last_data["value"]
            high = last_data["high"]
            low = last_data["low"]
            up_bond = (high - value) / value
            low_bond = (value - low) / value
            threshold = 0.01
            r = 0
            if value > high:
                f = "high"
                r = up_bond * 100
            elif value < low:
                f = "low"
                r = low_bond * 100
            elif up_bond < threshold:
                f = "注意卖出"
                r = up_bond * 100
            elif low_bond < threshold:
                f = "注意买入"
                r = low_bond * 100
            return f, r

        last_row = data.iloc[0]
        flag, res = _get_flag(last_row)
        conclusion = "%s\n%.2f" % (flag, res)
        ax.text(last_row["time"], last_row["value"], conclusion, size=24)

        fig.tight_layout()

        file_name = "%s_%s_boll" % (self.code, self.description)  # 结果保存的文件名
        graph_path = os.path.join(self.boll_path, "%s.png" % file_name)
        fig.savefig(graph_path, format='png')

        plt.show()
        print("结论：", conclusion)
        return flag, res


if __name__ == '__main__':
    fund = Fund("001549", "上证50", result_dir="持有")
    print(fund.df.head())
    fund.boll()
    fund.forecasting()
    fund.validate()
