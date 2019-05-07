import pandas as pd
from Program import *
from datetime import datetime, timedelta
pd.set_option('expand_frame_repr', False) # 當列太多時不換行
pd.set_option('display.max_rows', 1000)


# ===布林線策略
# 簡單布林線策略
def signal_bolling(df, para=[100, 2]):
    """
    布林線中軌：n天收盤價的移動平均線
    布林線上軌：n天收盤價的移動平均線 + m * n天收盤價的標準差
    布林線上軌：n天收盤價的移動平均線 - m * n天收盤價的標準差
    當收盤價由下向上穿過上軌的時候，做多；然後由上向下穿過下軌的時候，平倉。
    當收盤價由上向下穿過下軌的時候，做空；然後由下向上穿過上軌的時候，平倉。
    :param df: 原始數據
    :param para: 參數，[n, m]
    :return:
    """

    # ===计算指标
    n = para[0]
    m = para[1]

    # 计算均线
    df['median'] = df['close'].rolling(n, min_periods=1).mean()

    # 计算上轨、下轨道
    df['std'] = df['close'].rolling(n, min_periods=1).std(ddof=0)  # ddof代表标准差自由度
    df['upper'] = df['median'] + m * df['std']
    df['lower'] = df['median'] - m * df['std']

    # ===找出做多信号
    condition1 = df['close'] > df['upper']  # 当前K线的收盘价 > 上轨
    condition2 = df['close'].shift(1) <= df['upper'].shift(1)  # 之前K线的收盘价 <= 上轨
    df.loc[condition1 & condition2, 'signal_long'] = 1  # 将产生做多信号的那根K线的signal设置为1，1代表做多

    # ===找出做多平仓信号
    condition1 = df['close'] < df['median']  # 当前K线的收盘价 < 中轨
    condition2 = df['close'].shift(1) >= df['median'].shift(1)  # 之前K线的收盘价 >= 中轨
    df.loc[condition1 & condition2, 'signal_long'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓

    # ===找出做空信号
    condition1 = df['close'] < df['lower']  # 当前K线的收盘价 < 下轨
    condition2 = df['close'].shift(1) >= df['lower'].shift(1)  # 之前K线的收盘价 >= 下轨
    df.loc[condition1 & condition2, 'signal_short'] = -1  # 将产生做空信号的那根K线的signal设置为-1，-1代表做空

    # ===找出做空平仓信号
    condition1 = df['close'] > df['median']  # 当前K线的收盘价 > 中轨
    condition2 = df['close'].shift(1) <= df['median'].shift(1)  # 之前K线的收盘价 <= 中轨
    df.loc[condition1 & condition2, 'signal_short'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓
    # df.drop_duplicates(subset=['signal_long', 'signal_short'], inplace=True)

    # ===合并做多做空信号，去除重复信号
    df['signal'] = df[['signal_long', 'signal_short']].sum(axis=1, min_count=1, skipna=True)  # 若你的pandas版本是最新的，请使用下面一行代码代替本行
    # df['signal'] = df[['signal_long', 'signal_short']].sum(axis=1, min_count=1, skipna=True)  # 若你的pandas版本是最新的，请使用本行代码代替上面一行

    temp = df[df['signal'].notnull()][['signal']]
    temp = temp[temp['signal'] != temp['signal'].shift(1)]
    df['signal'] = temp['signal']
    df.drop(['median', 'std', 'upper', 'lower', 'signal_long', 'signal_short'], axis=1, inplace=True)
    df.to_csv(basedir+'signal.csv', mode='w')
    # ===由signal计算出实际的每天持有仓位
    # signal的计算运用了收盘价，是每根K线收盘之后产生的信号，到第二根开盘的时候才买入，仓位才会改变。
    df['pos'] = df['signal'].shift()
    df['pos'].fillna(method='ffill', inplace=True)
    df['pos'].fillna(value=0, inplace=True)  # 将初始行数的position补全为0

    return df


# 帶止損的布林線策略

def signal_bolling_with_stop_lose(df, para=[100, 2, 5]):
    """
    布林線中軌：n天收盤價的移動平均線
    布林線上軌：n天收盤價的移動平均線 + m * n天收盤價的標準差
    布林線上軌：n天收盤價的移動平均線 - m * n天收盤價的標準差
    當收盤價由下向上穿過上軌的時候，做多；然後由上向下穿過下軌的時候，平倉。
    當收盤價由上向下穿過下軌的時候，做空；然後由下向上穿過上軌的時候，平倉。

    另外，當價格往虧損方向超過百分之stop_lose的時候，平倉止損。
    :param df: 原始數據
    :param para: 參數，[n, m, stop_lose]
    :return:
    """

    # ===計算指標
    n = para[0]
    m = para[1]
    stop_loss_pct = para[2]

    # 計算均線
    df['median'] = df['close'].rolling(n, min_periods=1).mean()

    # 計算上軌、下軌道
    df['std'] = df['close'].rolling(n, min_periods=1).std(ddof=0) # ddof代表標準差自由度
    df['upper'] = df['median'] + m * df['std']
    df['lower'] = df['median'] - m * df['std']

    # ===找出做多信號
    condition1 = df['close'] > df['upper'] # 當前K線的收盤價 > 上軌
    condition2 = df['close'].shift(1) <= df['upper'].shift(1) # 之前K線的收盤價 <= 上軌
    df.loc[condition1 & condition2, 'signal_long'] = 1 # 將產生做多信號的那根K線的signal設置為1，1代表做多
    # ===找出做多平倉信號
    condition1 = df['close'] < df['median']  # 當前K線的收盤價 < 中軌
    condition2 = df['close'].shift(1) >= df['median'].shift(1)  # 之前K線的收盤價 >= 中軌
    df.loc[condition1 & condition2, 'signal_long'] = 0  # 將產生平倉信號當天的signal設置為0，0代表平倉

    # ===找出做空信號
    condition1 = df['close'] < df['lower']  # 當前K線的收盤價 < 下軌
    condition2 = df['close'].shift(1) >= df['lower'].shift(1)  # 之前K線的收盤價 >= 下軌
    df.loc[condition1 & condition2, 'signal_short'] = -1  # 將產生做空信號的那根K線的signal設置為-1，-1代表做空

    # ===找出做空平倉信號
    condition1 = df['close'] > df['median']  # 當前K線的收盤價 > 中軌
    condition2 = df['close'].shift(1) <= df['median'].shift(1)  # 之前K線的收盤價 <= 中軌
    df.loc[condition1 & condition2, 'signal_short'] = 0  # 將產生平倉信號當天的signal設置為0，0代表平倉

    # ===考察是否需要止盈止損
    info_dict = {'pre_signal': 0, 'stop_lose_price': None}  # 用於記錄之前交易信號，以及止損價格
    # 逐行遍歷df，考察每一行的交易信號
    for i in range(df.shape[0]):
        # 如果之前是空倉
        if info_dict['pre_signal'] == 0:
            # 當本週期有做多信號
            if df.at[i, 'signal_long'] == 1:
                df.at[i, 'signal'] = 1  # 將真實信號設置為1
                # 記錄當前狀態
                pre_signal = 1  # 信號
                stop_lose_price = df.at[i, 'close'] * (
                            1 - stop_loss_pct / 100)  # 以本週期的收盤價乘以一定比例作為止損價格。也可以用下週期的開盤價df.at[i+1, 'open']，但是此時需要注意i等於最後一個i時，取i+1會報錯
                info_dict = {'pre_signal': pre_signal, 'stop_lose_price': stop_lose_price}
            # 當本週期有做空信號
            elif df.at[i, 'signal_short'] == -1:
                df.at[i, 'signal'] = -1  # 將真實信號設置為-1
                # 記錄相關信息
                pre_signal = -1  # 信號
                stop_lose_price = df.at[i, 'close'] * (
                            1 + stop_loss_pct / 100)  # 以本週期的收盤價乘以一定比例作為止損價格，也可以用下週期的開盤價df.at[i+ 1, 'open']
                info_dict = {'pre_signal': pre_signal, 'stop_lose_price': stop_lose_price}
            # 無信號
            else:
                # 記錄相關信息
                info_dict = {'pre_signal': 0, 'stop_lose_price': None}

        # 如果之前是多頭倉位
        elif info_dict['pre_signal'] == 1:
            # 當本週期有平多倉信號，或者需要止損
            if (df.at[i, 'signal_long'] == 0) or (df.at[i, 'close'] < info_dict['stop_lose_price']):
                df.at[i, 'signal'] = 0  # 將真實信號設置為0
                # 記錄相關信息
                info_dict = {'pre_signal': 0, 'stop_lose_price': None}

            # 當本週期有平多倉並且還要開空倉
            if df.at[i, 'signal_short'] == -1:
                df.at[i, 'signal'] = -1  # 將真實信號設置為-1
                # 記錄相關信息
                pre_signal = -1  # 信號
                stop_lose_price = df.at[i, 'close'] * (
                            1 + stop_loss_pct / 100)  # 以本週期的收盤價乘以一定比例作為止損價格，也可以用下週期的開盤價df.at[i+ 1, 'open']
                info_dict = {'pre_signal': pre_signal, 'stop_lose_price': stop_lose_price}
        # 如果之前是空頭倉位
        elif info_dict['pre_signal'] == -1:
            # 當本週期有平空倉信號，或者需要止損
            if (df.at[i, 'signal_shor t'] == 0) or (df.at[i, 'close'] > info_dict['stop_lose_price']):
                df.at[i, 'signal'] = 0  # 將真實信號設置為0
                # 記錄相關信息
                info_dict = {'pre_signal': 0, 'stop_lose_price': None}

            # 當本週期有平空倉並且還要開多倉
            if df.at[i, 'signal_long'] == 1:
                df.at[i, 'signal'] = 1  # 將真實信號設置為1
                # 記錄相關信息
                pre_signal = 1  # 信號
                stop_lose_price = df.at[i, 'close'] * (
                            1 - stop_loss_pct / 100)  # 以本週期的收盤價乘以一定比例作為止損價格，也可以用下週期的開盤價df.at[i+ 1, 'open']
                info_dict = {'pre_signal': pre_signal, 'stop_lose_price': stop_lose_price}

        # 其他情況
        else:
            raise ValueError('不可能出現其他的情況，如果出現，說明代碼邏輯有誤，報錯')
    # 將無關的變量刪除
    df.drop(['median', 'std', 'upper', 'lower', 'signal_long', 'signal_short'], axis=1, inplace=True)

    # ===由signal計算出實際的每天持有倉位
    # signal的計算運用了收盤價，是每根K線收盤之後產生的信號，到第二根開盤的時候才買入，倉位才會改變。
    df['pos'] = df['signal'].shift()
    df['pos'].fillna(method='ffill', inplace=True)
    df['pos'].fillna(value=0, inplace=True)  # 將初始行數的position補全為0
    return df


# ===移動平均線策略
# 簡單移動均線策略
def signal_moving_average(df, para=[5, 60]):
    """
    簡單的移動平均線策略
    當短期均線由下向上穿過長期均線的時候，買入；然後由上向下穿過的時候，賣出。
    :param df: 原始數據
    :param para: 參數，[ma_short, ma_long]
    :return:
    """

    # ===計算指標
    ma_short = para[0]
    ma_long = para[1]

    # 計算均線
    df['ma_short'] = df['close'].rolling(ma_short, min_periods=1).mean()
    df['ma_long'] = df['close'].rolling(ma_long, min_periods=1).mean()

    # ===找出買入信號
    condition1 = df['ma_short'] > df['ma_long'] # 短期均線 > 長期均線
    condition2 = df['ma_short'].shift(1) <= df['ma_long'].shift(1) # 之前的短期均線 <= 長期均線
    df.loc[condition1 & condition2, 'signal'] = 1 # 將產生做多信號的那根K線的signal設置為1，1代表做多

    # ===找出賣出信號
    condition1 = df['ma_short'] < df['ma_long']  # 短期均線 < 長期均線
    condition2 = df['ma_short'].shift(1) >= df['ma_long'].shift(1)  # 之前的短期均線 >= 長期均線
    df.loc[condition1 & condition2, 'signal'] = 0  # 將產生平倉信號當天的signal設置為0，0代表平倉

    df.drop(['ma_short', 'ma_long'], axis=1, inplace=True)

    # ===由signal計算出實際的每天持有倉位
    # signal的計算運用了收盤價，是每根K線收盤之後產生的信號，到第二根開盤的時候才買入，倉位才會改變。
    df['pos'] = df['signal'].shift()
    df['pos'].fillna(method='ffill', inplace=True)
    df['pos'].fillna(value=0, inplace=True)  # 將初始行數的position補全為0

    return df

def Singnal_Operate(STATUS, signal):
    if signal == STATUS and STATUS == -1:
        signal = None
        print(datetime.now(),'目前已作空~')
    elif signal == STATUS and STATUS == 1:
        signal = None
        print(datetime.now(),'目前已作多~')
    elif signal == 0 and STATUS == 1:
        signal = 0
        print(datetime.now(),'要平多囉~')
    elif signal == 0 and STATUS == -1:
        signal = 0
        print(datetime.now(),'要平空囉~')
    elif signal == 1 and STATUS == 0:
        print(datetime.now(),'要做多囉~')
    elif signal == -1 and STATUS == 0:
        print(datetime.now(),'要做空囉~')
    return signal
