"""
计算极值
"""
import numpy as np
from scipy import signal


def get_peaks(fcst):
    fcst_np = fcst.fcst.to_numpy()
    time_np = fcst.time.to_numpy()
    peak_ind_list = list()
    peak_ind = signal.argrelextrema(fcst_np, np.greater, order=5)  # 极大值点
    peak_ind_list.extend(peak_ind[0])
    peak_ind = signal.argrelextrema(fcst_np, np.less, order=5)  # 极小值点
    peak_ind_list.extend(peak_ind[0])
    peak_time = time_np[peak_ind_list]
    peak_val = fcst_np[peak_ind_list]
    return peak_time, peak_val
