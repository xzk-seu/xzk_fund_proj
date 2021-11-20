"""
功能：确定定投的目标收益率
"""

import os

import pandas as pd
from tqdm import tqdm

fund_info = {
    # "002979": "广发金融地产",
    # "001549": "天弘上证50",
    # "005918": "天弘沪深300",
    # "001595": "天弘中证银行",
    "001551": "天弘中证医药100",
    # "161725": "招商中证白酒",
    # "001593": "天弘创业板",
    # "001632": "天弘中证食品饮料",
    # "070039": "嘉实中证500",
}

week = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]


class FixedInvestor:
    def __init__(self, code, des, end_day="2021-09-01", unit=100, day_str="2W-WED", closed="left"):
        """

        :type unit: 单次投资的金额
        :param code: 基金代码
        :param des: 基金名称
        :param end_day: 结束时间戳，用于获取数据
        :param day_str: 如"2W-WED"这样的字符串，用于时间的采样
        :param closed: "left" or "right"，用于时间的采样
        """
        self.unit = unit
        self.closed = closed
        self.day_str = day_str
        self.des = des
        self.code = code
        self.end_day = end_day
        self.df = self.get_df()

    def get_df(self):
        file_name = "%s_%s_%s.csv" % (self.code, self.des, self.end_day)
        data_path = os.path.join(os.getcwd(), "data", file_name)
        df = pd.read_csv(data_path)
        df = df[["Date", "NetAssetValue"]]
        df.columns = ["time", "value"]
        df["time"] = pd.to_datetime(df["time"])
        df.set_index("time", inplace=True)
        buy_day = df.resample(self.day_str, closed=self.closed, label=self.closed).ffill()

        labels = list(buy_day.index)
        if pd.Timestamp(self.end_day) not in labels:
            bins = labels + [pd.Timestamp(self.end_day), ]
        else:
            bins = labels + [pd.Timestamp("2100-01-01")]
        df['buy_day'] = pd.cut(df.index, bins=bins, labels=labels, right=False)
        df = df.sort_index()

        print(df.tail(20))
        return df

    def sim_invest(self, target_rate, start_day=pd.Timestamp("2000-01-01")):
        """
        一轮模拟投资
        :param start_day: 定投开始日期
        :param target_rate: 目标收益率
        :return:
        """
        cost = 0
        share = 0
        sim_res = list()
        buy_days = list()
        for day, row in self.df.iterrows():
            if day < start_day and cost == 0 and day != row['buy_day']:  # 没有买入
                continue
            unit_net = row['value']
            hold = share * unit_net
            income = hold - cost
            if hold == 0:
                rate_of_return = 0
            else:
                rate_of_return = income / hold

            if rate_of_return >= target_rate:
                time = (day - buy_days[0]) / pd.Timedelta(1, 'D')
                time = int(time)
                if time <= 7:
                    income -= cost * 0.015  # 持有时间太短，有手续费
                sim_res.append(dict(cost=cost, income=income, sale_day=day, buy_day=buy_days[0], time_span=time))
                buy_days = list()
                cost = 0
                share = 0

            if day == row['buy_day']:
                buy_days.append(row['buy_day'])
                cost += self.unit
                share += self.unit / unit_net

        # print(sim_res)
        return sim_res

    def target_rate_analysis(self, n=50):
        """
        分析得到最优目标利率
        从已有净值表里随机选择n个时间作为投资开始时间，
        收益率从4到20
        :return:
        """
        time_sample = self.df.index.to_series().sample(n)
        temp = pd.Timestamp("1990-01-01")
        time_sample[temp] = temp
        time_sample = time_sample.sort_values()
        m_res_list = list()
        for d in tqdm(time_sample):
            d_res_list = list()
            for i in range(4, 21):
                r = i / 100
                sim_res = self.sim_invest(r, d)
                res = self.sim_res_analysis(r, sim_res)
                if not res:  # 一轮投资结果为空，说明投资没有到预期
                    continue
                d_res_list.append(res)

            if len(d_res_list) == 0:
                continue
            m = max(d_res_list, key=lambda x: x["score"])
            m["start_day"] = d
            m_res_list.append(m)
            # print(d, m)
        print("\n\n\n")
        rates = [x["rate"] for x in m_res_list]
        max_rate = max(rates, key=rates.count)
        m_res_list = [m for m in m_res_list if m["rate"] == max_rate]
        m_costs = [m["max_cost"] for m in m_res_list]
        max_cost = max(m_costs)  # 最大成本
        time_list = list()
        for m in m_res_list:
            time_list.extend(m["time_spans"])
            # print(m)

        print("最佳目标：", max_rate)
        print("最大成本：", max_cost)
        print("最长时间：", max(time_list))
        print("平均时间：", sum(time_list) / len(time_list))

        res_path = os.path.join(os.getcwd(), "target_rate_analysis")
        if not os.path.exists(res_path):
            os.makedirs(res_path)
        idx = len(os.listdir(res_path))
        res_path = os.path.join(res_path, "target_rate_analysis_%d.txt" % idx)
        with open(res_path, "at") as fw:
            print("\n\n\n", self.code, self.des, self.end_day, file=fw)
            fw.write("\n")
            for m in m_res_list:
                print(m, file=fw)
            fw.write("\n")
            print("最佳目标：", max_rate, file=fw)
            print("最大成本：", max_cost, file=fw)
            print("最长时间：", max(time_list), file=fw)
            print("平均时间：", sum(time_list) / len(time_list), file=fw)

            fw.write("*************end report**************************")

    @staticmethod
    def sim_res_analysis(rate, sim_res):
        """
        一轮模拟投资的结果分析
        :return:
        """
        if len(sim_res) == 0:  # 一轮投资结果为空，说明投资没有到预期
            return
        total_income = 0
        max_cost = 0
        for item in sim_res:
            total_income += item["income"]
            if item["cost"] > max_cost:
                max_cost = item["cost"]
        time_spans = [x['time_span'] for x in sim_res]
        ref_rate = total_income / max_cost

        # 用于评估一个定投策略的分数
        score = 10000 * total_income / max_cost / max(time_spans)
        res = dict(rate=rate, max_cost=max_cost, score=score, ref_rate=ref_rate,
                   time_spans=time_spans, total_income=total_income)  # 止盈率，最大成本，评分，参考收益率，时间长度集合，总收益
        return res


def main():
    """
    # fi = FixedInvestor("001595", "天弘中证银行", "2021-09-01", 100, "2W-WED", "left")
    # fi.target_rate_analysis(n=5)
    :return:
    :rtype:
    """
    for k, v in fund_info.items():
        fi = FixedInvestor(k, v)
        fi.target_rate_analysis()


if __name__ == '__main__':
    main()
