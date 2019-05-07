import pandas as pd
from Program.Trace.Function import transfer_to_period_data
from Program.Trace.Signal import signal_bolling
from Program.Trace.Evaluate import equity_curve_with_long_and_short
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.set_option('expand_frame_repr', False) # 當列太多時不換行
pd.set_option('display.max_rows', 1000)


# # # 導入數據
# df = pd.read_hdf('C:/Users/Admin/Desktop/coin_quant_class_1128/data/class8/eth_1min_data.h5', key='all_data')
#
# # 轉換數據周期
# rule_type = '15T'
# df = transfer_to_period_data(df, rule_type)
#
# # 計算交易信號
# para = [100, 2]
# df = signal_bolling(df, para)
#
# df = df[df['candle_begin_time'] >= pd.to_datetime('2017-01-01')]
# df.reset_index(inplace=True, drop=True)
#
# # 計算資金曲線
# df = equity_curve_with_long_and_short(df, leverage_rate=3, c_rate=2.0/1000)
#
# print('策略最終收益：', df.iloc[-1]['equity_curve'])
# exit()

# =====尋找最優參數
# 導入數據
all_data = pd.read_hdf('C:/Users/Admin/PycharmProjects/demo/Data/bfx_ETH5m_data.h5', key='h5_data')
all_data[['candle_begin_time']] = all_data[['candle_begin_time_GMT8']]
all_data = all_data[['candle_begin_time', 'open', 'high', 'low', 'close', 'volume']]

# 轉換數據周期
rule_type = '15T'
all_data = transfer_to_period_data(all_data, rule_type)
# 選取時間段
all_data = all_data[all_data['candle_begin_time'] >= pd.to_datetime('2018-08-19')]
all_data.reset_index(inplace=True, drop=True)

# 構建參數候選組合
# n_list = range(70, 400, 10)
n_list = [370]
# i = 1.0
# m_list = [i]
m_list = [2.0]
# while i <= 4.0:
#     i+=0.2
#     m_list.append(round(i, 2))


# 遍歷所有參數組合
rtn = pd.DataFrame()
for m in m_list:
    for n in n_list:
        para = [n, m]

        # 計算交易信號
        df = signal_bolling(all_data.copy(), para)

        # 計算資金曲線
        df = equity_curve_with_long_and_short(df, leverage_rate=3, c_rate=2.0 / 1000)
        print(para, '策略最終收益：', df.iloc[-1]['equity_curve'])

        # 存儲數據
        rtn.loc[str(para), '收益'] = df.iloc[-1]['equity_curve']

print(rtn.sort_values(by='收益', ascending=False))
