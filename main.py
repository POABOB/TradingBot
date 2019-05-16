import ccxt
import pandas as pd
import os
import sys
basedir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(basedir)

# 物件初始化
exchange = ccxt.bitfinex2()
exchange.apiKey = 'IWCG8YwreowRMBx1B7OpY9e9IMX4XrpkTw7LWtwDwF6'
exchange.secret = 's2Ru0TWdd42rwbiQAyuna3hz9ZBIiiNYQAk0gV5gtik'
exchange_balance = ccxt.bitfinex()
exchange_balance.apiKey = 'IWCG8YwreowRMBx1B7OpY9e9IMX4XrpkTw7LWtwDwF6'
exchange_balance.secret = 's2Ru0TWdd42rwbiQAyuna3hz9ZBIiiNYQAk0gV5gtik'
#================================================================

from Program.Tickers.Ticker import *    # 資料蒐集
from Program.Signals.Signal import *
from Program.Trades.Trade import *
from Program.Tickers.GetData import GetData, AddData
from datetime import datetime, timedelta
from time import sleep
pd.set_option('expand_frame_repr', False)   # 當太多行時不換行

"""
自動交易主要流程

# 通過while語句，不斷的循環

# 每次循環中需要做的操作步驟
    1. 更新賬戶信息
    2. 獲取實時數據
    3. 根據最新數據計算買賣信號
    4. 根據目前倉位、買賣信息，結束本次循環，或者進行交易
    5. 交易
"""

# =====參數
time_interval = '15m' # 間隔運行時間，不能低於5min

symbol = 'ETH/USD' # 交易品種
base_coin = symbol.split('/')[-1]   # 斜槓後的貨幣 => USD
trade_coin = symbol.split('/')[0]   # 斜槓前的貨幣 => ETH
STATUS = 0    # 辨識買跌買漲
para1 = [100, 2.0] # 策略參數 => 布林通道策略(天數,標準差)
para2 = [7, 2];
original_money=914
# =====
times = 1
# =====資料抓取
print('系統資料庫更新中...')
now = datetime.now() + timedelta(seconds=61)
since = int((now - timedelta(days=para[0])).timestamp()) * 1000
now = int(now.timestamp()) * 1000
df = GetData(since, now)
print('============================')
# =====

# =====主程序
while True:
    # =====開啟新信件
    if(times == 5)
        print('系統資料庫更新中...')
        now = datetime.now() + timedelta(seconds=61)
        since = int((now - timedelta(days=para[0])).timestamp()) * 1000
        now = int(now.timestamp()) * 1000
        df = GetData(since, now)
        print('============================')
        times = 1

    email_title = '耿映翔的機器人'
    email_content = ''
    # =====

    # =====get the balance from server
    email_content=balance(email_content)
    # =====

    # =====set the orders' condition
    email_content=order(email_content)
    # =====

    # =====sleep when the time's out
    run_time = next_run_time(time_interval)
    sleep(max(0, (run_time - datetime.now()).seconds))
    while True:  # When the time is close to the trading time
        if datetime.now() < run_time:
            continue
        else:
            break
    # =====

    # =====update the newest data
    df = df[df['candle_begin_time_GMT8'] < (run_time - timedelta(minutes=15))]
    while True:
        _df = AddData((run_time- timedelta(minutes=30)).timestamp() * 1000)
        i = 0
        while True:
            if _df.iloc[i]['candle_begin_time_GMT8']  == (run_time - timedelta(minutes=15)):
                break
            if i > 1:
                break
            i += 1
        if(i > 1):
            continue
        break
    print(_df)
    df = pd.concat([df, _df.tail(1)], sort=True)
    df = df.drop(df.head(1).index)
    df.reset_index(drop=True, inplace=True)
    
    # =====

    # =====Signals
    df = df[df['candle_begin_time_GMT8'] < (run_time)]
    df = signal_bolling(df, para=para)
    signal = df.iloc[-1]['signal']
    print(df)
    # ====
    print(df.iloc[-1])
    # =====Signal judge
    signal = Singnal_Operate(STATUS, signal)
    print('\n交易訊號', signal)
    # =====

    # =====獲取可用餘額
    USD_balance= exchange_balance.fetch_balance({'type': 'trading'})
    USD = float(USD_balance['USD']['free'])
    used_USD=float(USD_balance['USD']['used'])
    # =====

    # =====Trade
    #空
    if STATUS == 0 and signal == -1:
        email_content = Operate(exchange, email_title, email_content,'Sell', symbol, USD, used_USD)
        STATUS = -1
    #平空
    elif STATUS == -1 and signal == 0:
        email_content = Operate(exchange, email_title, email_content,'SellFilled', symbol, USD, used_USD)
        STATUS = 0
    #多
    elif STATUS == 0 and signal == 1:
        email_content = Operate(exchange, email_title, email_content,'Buy', symbol, USD, used_USD)
        STATUS = 1
    #平多
    elif STATUS == 1 and signal == 0:
        email_content = Operate(exchange, email_title, email_content,'BuyFilled', symbol, USD, used_USD)
        STATUS = 0
    #平空做多
    elif signal == -0.5 and STATUS == 1:
        email_content = Operate(exchange, email_title, email_content,'SellFilled', symbol, USD, used_USD)
        email_content = Operate(exchange, email_title, email_content,'Buy', symbol, USD, used_USD)
    #平多做空
    elif signal == 0.5 and STATUS == -1:
        email_content = Operate(exchange, email_title, email_content,'BuyFilled', symbol, USD, used_USD)
        email_content = Operate(exchange, email_title, email_content,'Sell', symbol, USD, used_USD)
        
    # =====
    
    # =====倉位
    email_content=position(email_content)
    print(STATUS)
    Profit_USD = '已獲利: ' + str(1 - (USD_balance['USD']['total'] / original_money)) + '\n'
    email_content += Profit_USD
    # =====

    # =====信號
    email_content=signal_num(email_content, signal)
    # =====

    # =====Send Email per half hour
    if run_time.minute % 15 == 0:
        # 发送邮件
        auto_send_email('zxc752166@gmail.com', email_title, email_content, 'nuic2019ncue@gmail.com',False)
    # =====

    # =====本次交易结束
    print(email_title)
    print(email_content)
    print('=====本次運行完畢，30秒後繼續運行=====\n')
    times++
    sleep(30 * 1)
# =====

# =====取消order
# order_info = exchange_balance.cancel_order(id=24687365656)