"""
Goal:讀取bfx的BTC所有k線資料並存置hdf檔中
Author:YingSiang Geng
Date:2019/04/26
"""
from Program import *
import pandas as pd
from datetime import datetime, timedelta
import ccxt
from time import sleep
pd.set_option('expand_frame_repr', False)  # 當太多行時不換行

def GetData(since, now):

    bfx = ccxt.bitfinex2()
    p_market = 'ETH/USD'
    p_interval = '15m'
    df = pd.DataFrame(dtype=float)
    df_last = since


    while True:
        content = bfx.fetch_ohlcv(p_market,
                                  p_interval,
                                  since=df_last,
                                  limit=5000)
        df = df.append(content)
        df_last = df.tail(1)
        df.drop(df_last)
        df_last = int(df_last[0])

        sleep(3.01)
        if df_last + 900000 >= now:
            break
    # 欄位更名
    df.rename(columns={0: 'MTS', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'}, inplace=True)
    df['candle_begin_time'] = pd.to_datetime(df['MTS'], unit='ms')
    df['candle_begin_time_GMT8'] = df['candle_begin_time'] + timedelta(hours=8)
    df = df[['candle_begin_time_GMT8', 'open', 'high', 'low', 'close', 'volume']]
    df = df.reset_index(level=[0])
    df = df.drop_duplicates(subset='candle_begin_time_GMT8', keep='first', inplace=False)
    del df['index']


    # 儲存成回測資料
    trade_coin = p_market.split('/')[0]
    file_name_h5 = 'bfx_' + trade_coin + '_'+p_interval + '_data.h5'
    file_key = 'temp'

    df.to_hdf(basedir+
        '/Tickers/Data/%s' % file_name_h5,
        key=file_key,
        mode='w')

    print('資料已經儲存至資料夾內!')
    return df

def AddData(since):
    bfx = ccxt.bitfinex2()
    p_market = 'ETH/USD'
    p_interval = '15m'

    while True:
        sleep(4)
        content = bfx.fetch_ohlcv(p_market,
                              p_interval,
                              since=since,
                              limit=3)

        df_temp = pd.DataFrame(content, dtype=float)
        if (len(df_temp) >= 2):

            break
            # if(((df_temp.iloc[-1]['candle_begin_time']).timestamp() * 1000) == since):
            #     break
            # else:
            #     since = ((df_temp.iloc[-1]['candle_begin_time'] + timedelta(minutes=15)).timestamp()) * 1000
        print('重需獲取數據...')


    df_temp.rename(columns={0: 'MTS', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'}, inplace=True)
    df_temp['candle_begin_time'] = pd.to_datetime(df_temp['MTS'], unit='ms')
    df_temp['candle_begin_time_GMT8'] = df_temp['candle_begin_time'] + timedelta(hours=8)
    df_temp = df_temp[['candle_begin_time_GMT8', 'open', 'high', 'low', 'close', 'volume']]

    # df = pd.concat([df, df_temp])
    # df = df.drop(df.head(1).index)
    # df.reset_index(drop=True, inplace=True)

    return df_temp
