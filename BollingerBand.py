from pandas.api.indexers import FixedForwardWindowIndexer
import matplotlib.pyplot as plt
import pandas as pd


class BollingerBand:
    def __init__(self, data, window=20):
        self.data = data
        self.window = window

        roll = self.data["value"].rolling(FixedForwardWindowIndexer(window_size=self.window))
        std = roll.std()
        mean = roll.mean()
        self.data["std"] = std
        self.data["mean"] = mean
        self.data["high"] = mean + 2 * std
        self.data["low"] = mean - 2 * std

        self.last_row = data.iloc[0]
        self.conclusion = "None"
        self.upper_bound, self.lower_bound = 0, 0
        self.init_last_state()
        self.width = self.upper_bound + self.lower_bound

    def get_fig(self, title):
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        fig = plt.figure(facecolor="w", figsize=(10, 6))

        fig.suptitle(title)
        ax = fig.add_subplot(111)
        ax.plot(pd.to_datetime(self.data.time), self.data.value, "k")
        ax.plot(pd.to_datetime(self.data.time), self.data['mean'], )
        ax.plot(pd.to_datetime(self.data.time), self.data["high"], )
        ax.plot(pd.to_datetime(self.data.time), self.data["low"], )

        ax.grid(True, which="major", c="gray", ls="-", lw=1, alpha=0.2)
        ax.set_xlabel(xlabel="time")

        ax.text(self.last_row["time"], self.last_row["value"], self.conclusion, size=24)

        fig.tight_layout()
        return fig

    def init_last_state(self):
        value = self.last_row["value"]
        high = self.last_row["high"]
        low = self.last_row["low"]
        self.upper_bound = (high - value) / value * 100
        self.lower_bound = (value - low) / value * 100
        threshold = 1

        if value > high:
            self.conclusion = "突破上界"
        elif value < low:
            self.conclusion = "突破下界"
        elif self.upper_bound < threshold:
            self.conclusion = "注意卖出"
        elif self.lower_bound < threshold:
            self.conclusion = "注意买入"
