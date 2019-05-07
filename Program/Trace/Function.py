import pandas as pd
pd.set_option('expand_frame_repr', False) # 當列太多時不換行
pd.set_option('display.max_rows', 1000)


def transfer_to_period_data(df, rule_type='15T'):
    """
    將數據轉換為其他週期的數據
    :param df:
    :param rule_type:
    :return:
    """

    # =====轉換為其他分鐘數據
    period_df = df.resample(rule=rule_type, on='candle_begin_time', label='left', closed='left').agg(
        {'open': 'first',
         'high': 'max',
         'low': 'min',
         'close': 'last',
         'volume': 'sum',
         })
    period_df.dropna(subset=['open'], inplace=True) # 去除一天都沒有交易的周期
    period_df = period_df[period_df['volume'] > 0] # 去除成交量為0的交易週期
    period_df.reset_index(inplace=True)
    df = period_df[['candle_begin_time', 'open', 'high', 'low', 'close', 'volume']]

    return df
