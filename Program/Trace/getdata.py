"""
Goal:讀取bfx的BTC所有k線資料並存置hdf檔中
Author:YingSiang Geng
Date:2019/04/26
"""
import pandas as pd
from datetime import datetime, timedelta
import ccxt
from time import sleep

pd.set_option('expand_frame_repr', False)   # 當太多行時不換行

bfx = ccxt.bitfinex2()
# p_market = input('請輸入需要撈資料的幣種和和交易幣(BTC/USD):')
p_market = 'ETH/USD'
p_interval = '15m'

df = pd.DataFrame(dtype=float)
# 2013/04/01 bfx才開始交易BTC
print('系統預設從20170701的資料到目前的時間')
p_start_date = datetime(2019, 4, 29, 9, 15)
df_last = int(p_start_date.timestamp()) * 1000
now_date = datetime.now()
end_date_unix_ts = int(now_date.timestamp()) * 1000
print('End MTS:', end_date_unix_ts)
while True:


    start_date_unix_ts = df_last

    print("Since: ", start_date_unix_ts)

    content = bfx.fetch_ohlcv(p_market,
                                     p_interval,
                                     since=start_date_unix_ts,
                                     limit=5000)
    df = df.append(content)
    df_last = df.tail(1)
    df_last = int(df_last[0])
    sleep(3.5)
    if df_last >= end_date_unix_ts:
        break
# 欄位更名
df.rename(columns={0: 'MTS', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'}, inplace=True)
df['candle_begin_time'] = pd.to_datetime(df['MTS'], unit='ms')
df['candle_begin_time_GMT8'] = df['candle_begin_time'] + timedelta(hours=8)
df = df[['candle_begin_time_GMT8', 'open', 'high', 'low', 'close', 'volume']]
df = df.reset_index(level=[0])
df=df.drop_duplicates(subset='candle_begin_time_GMT8',keep='first',inplace=False)
del df['index']
print("Rows in Market History: ",len(df))
print(df)
# print(df_last['candle_begin_time_GMT8'])
trade_coin = p_market.split('/')[0]
file_name = 'bfx_' + trade_coin + '5m' + '_data.h5'
# file_key = 'bfx_' + p_market + '_' +end_date_unix_ts
# 儲存成回測資料
df.to_hdf(
    'C:/Users/Admin/PycharmProjects/demo/Data/%s' % file_name,
    key='h5_data',
    mode='w')

print('資料已經儲存至資料夾內!')