from datetime import timedelta, datetime
from email.mime.text import MIMEText
from smtplib import SMTP
import ccxt

exchange = ccxt.bitfinex2()
exchange.apiKey = 'IWCG8YwreowRMBx1B7OpY9e9IMX4XrpkTw7LWtwDwF6'
exchange.secret = 's2Ru0TWdd42rwbiQAyuna3hz9ZBIiiNYQAk0gV5gtik'
exchange_balance = ccxt.bitfinex()
exchange_balance.apiKey = 'IWCG8YwreowRMBx1B7OpY9e9IMX4XrpkTw7LWtwDwF6'
exchange_balance.secret = 's2Ru0TWdd42rwbiQAyuna3hz9ZBIiiNYQAk0gV5gtik'

def balance(email_content):
    balance = exchange_balance.fetch_balance({'type': 'trading'})
    Total_USD = 'USD餘額: ' + str(balance['USD']['total'])
    Free_USD = '可使用的USD: ' + str(balance['USD']['free'])
    Used_USD = '已使用的USD: ' + str(balance['USD']['used'])
    # print(Total_USD)
    # print(Free_USD)
    # print(Used_USD)
    email_content += '===============錢包=================\n'
    email_content += Total_USD + '\n'
    email_content += Free_USD + '\n'
    email_content += Used_USD + '\n'
    return email_content
def order(email_content):
    order_info = exchange_balance.fetch_open_orders(symbol='ETH/USD', limit=10)  # limit参数控制返回最近的几条
    for i in order_info:
        # print(i['datetime'], i['status'], i['id'], i['price'], i['amount'], i['remaining'], i['filled'])
        Datetime = '時間: ' + str(i['datetime'])
        Status = '狀態: ' + str(i['status'])
        Id = '訂單id: ' + str(i['id'])
        Price =  '訂單價格: ' + str(i['price'])
        Original_amount = '所有訂單: ' + str(i['amount'])
        Remaining_amount = '現有訂單: ' + str(i['remaining'])
        Executed_amount = '已成交訂單: ' + str(i['filled'])
        email_content += '===============訂單=================\n'
        email_content += Datetime + '\n'
        email_content += Status + '\n'
        email_content += Id + '\n'
        email_content += Price + '\n'
        email_content += Original_amount + '\n'
        email_content += Remaining_amount + '\n'
        email_content += Executed_amount + '\n'
    return email_content

def position(email_content):
    margin_info = exchange.private_post_auth_r_positions()

    if len(margin_info):
        Symbol = '交易幣種: ' + str(margin_info[0][0])
        Margin_amount = '交易數量: ' + str(margin_info[0][2])
        Margin_price = '交易金額: ' + str(margin_info[0][3])
        Margin_profit = '交易損益: ' + str(float(margin_info[0][4]))
        Margin_profit_ = '交易損益(%): ' + str(float(margin_info[0][5]))


        email_content += '===============倉位=================\n'
        email_content += Symbol + '\n'
        email_content += Margin_amount + '\n'
        email_content += Margin_price + '\n'
        email_content += Margin_profit+ '\n'
        email_content += Margin_profit_+ '\n'
    return email_content

def signal_num(email_content, signal):
    email_content += '===============訊號=================\n'
    email_content += '交易訊號: ' + str(signal) + '\n'
    return email_content
# def signal(email_content):
# sleep
def next_run_time(time_interval, ahead_time=1):

    if time_interval.endswith('m'):
        now_time = datetime.now()
        time_interval = int(time_interval.strip('m'))

        target_min = (int(now_time.minute / time_interval) + 1) * time_interval
        if target_min < 60:
            target_time = now_time.replace(minute=target_min, second=0, microsecond=0)
        else:
            if now_time.hour == 23:
                target_time = now_time.replace(hour=0, minute=0, second=0, microsecond=0)
                target_time += timedelta(days=1)
            else:
                target_time = now_time.replace(hour=now_time.hour + 1, minute=0, second=0, microsecond=0)

        # sleep直到靠近目標時間之前
        if (target_time - datetime.now()).seconds < ahead_time+1:
            print('距離target_time不足', ahead_time, '秒，下下個週期再運行')
            target_time += timedelta(minutes=time_interval)
        print('下次運行時間', target_time)
        return target_time
    else:
        exit('time_interval doesn\'t end with m')




# need modify
# 獲取bitfinex的k線數據
# def get_bitfinex_candle_data(df, symbol, time_interval, now):
#     # 抓取數據
#     exchange = ccxt.bitfinex2()
#     content = exchange.fetch_ohlcv(symbol, time_interval, since=now, limit=1)
#     _df = pd.DataFrame(content ,dtype=float)
#     print(_df)
#     if _df:
#         _df.rename(columns={0: 'MTS', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'}, inplace=True)
#         _df['candle_begin_time'] = pd.to_datetime(_df['MTS'], unit='ms')
#         _df['candle_begin_time_GMT8'] = _df['candle_begin_time'] + timedelta(hours=8)
#         _df = _df[['candle_begin_time_GMT8', 'open', 'high', 'low', 'close', 'volume']]
#         _df = _df.reset_index(level=[0])
#         # _df = _df.drop_duplicates(subset='candle_begin_time_GMT8', keep='first', inplace=False)
#         # del df['index']
#         # 整理數據
#         df.append(_df)
#
#         df_first = df.iloc[0]
#         df.drop(df_first)
#         df = df.reset_index(level=[0])
#         _df.drop()
#     print(df)
#     return df

# 獲取okex的k線數據
# def get_okex_candle_data(exchange, symbol, time_interval):
#
#     # 抓取數據
#     content = exchange.fetch_ohlcv(symbol, timeframe=time_interval, since=0)
#
#     # 整理數據
#     df = pd.DataFrame(content, dtype=float)
#     df.rename(columns={0: 'MTS', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'}, inplace=True)
#     df['candle_begin_time'] = pd.to_datetime(df['MTS'], unit='ms')
#     df['candle_begin_time_GMT8'] = df['candle_begin_time'] + timedelta(hours=8)
#     df = df[['candle_begin_time_GMT8', 'open', 'high', 'low', 'close', 'volume']]
#
#     return df

# 自動發送郵件
def auto_send_email(to_address, subject, content, from_address='nuic2019ncue@gmail.com', if_add_time=True):
    """
    :param to_address:
    :param subject:
    :param content:
    :param from_address:
    :return:
    使用foxmail發送郵件的程序
    """
    try:
        if if_add_time:
            msg = MIMEText(datetime.now().strftime("%m-%d %H:%M:%S") + '\n\n' + content)
        else:
            msg = MIMEText(content)
        msg["Subject"] = subject + ' ' + datetime.now().strftime("%m-%d %H:%M:%S")
        msg["From"] = from_address
        msg["To"] = to_address

        username = from_address
        password = 'yiwuskwnjscsumsm'

        server = SMTP('smtp.gmail.com', port=587)
        server.starttls()
        server.login(username, password)
        server.sendmail(from_address, to_address, msg.as_string())
        server.quit()

        print('郵件發送成功')
    except Exception as err:
        print('郵件發送失敗', err)






# 交易參數
# symbol = 'BTC/USD'  # XBTUSD
# price = 5000
# amount = 1
#
# # 限價市價買
# # order_buy_limit = Bitmex.create_limit_buy_order(symbol, amount, price)
# # order = Bitmex.privatePostOrder({'symbol': symbol, 'side': 'Buy', 'orderQty': amount, 'price': price})
#
# # order_buy_market = Bitmex.create_market_buy_order(symbol, amount, price)
# # 限價市價賣
# # order_sell_limit = Bitmex.create_limit_sell_order(symbol, amount, price)
# # order_sell_market = Bitmex.create_market_sell_order(symbol, amount, price)
#
# # # 返回内容的数据结构：https://github.com/ccxt/ccxt/wiki/Manual#querying-account-balance
#
# # 查詢訂單訊息
# # order_info = Bitmex.fetch_order(id, symbol)
#
# # 查詢全部訂單
# # order_infos = Bitmex.fetch_orders(symbol, limit = 10)
# # for order in order_infos:
# #     print(order['datetime'], order['status'])
#
# # 查詢未成交訂單
# order_infos_unfilled = Bitmex.fetch_open_orders(symbol, limit = 10)
# for order in order_infos_unfilled:
#     print(order['datetime'], order['id'], order['status'])
#
# # 撤單
# cancel_order = Bitmex.cancel_order(id = 'cf6d1732-d413-0405-6948-e66a425c2a3b')


