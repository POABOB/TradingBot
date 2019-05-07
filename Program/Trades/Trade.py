import time

params = {'type': 'limit'}
# 下單
def place_order(exchange, order_type, buy_or_sell, symbol, price, amount):
    """
    下單
    :param exchange: 交易所
    :param order_type: limit, market
    :param buy_or_sell: buy, sell
    :param symbol: 買賣品種
    :param price: 當market訂單的時候，price無效
    :param amount: 買賣量
    :return:
    """
    for i in range(5):
        try:
            # 限價單
            if order_type == 'limit':
                # 買
                if buy_or_sell == 'buy':
                    order_info = exchange.create_limit_buy_order(symbol, amount=amount, price=price, para=params)
                # 賣
                elif buy_or_sell == 'sell':
                    order_info = exchange.create_limit_sell_order(symbol, amount=amount, price=price, para=params)
            # 市價單
            elif order_type == 'market':
                # 買
                if buy_or_sell == 'buy':
                    order_info = exchange.create_market_buy_order(symbol, amount=amount, para=params)
                # 賣
                elif buy_or_sell == 'sell':
                    order_info = exchange.create_market_sell_order(symbol, amount=amount, para=params)
            else:
                pass

            print('下單成功：', order_type, buy_or_sell, symbol, price, amount)
            print('下單訊息：', order_info, '\n')
            return order_info

        except Exception as e:
            print('下單錯誤，1s後重試', e)
            time.sleep(1)
    print('執行下單錯誤過多次，機器人停止執行')
    exit()

def Operate(exchange, email_title, email_content, operate, symbol, freeUSD, used_USD):
    #=====Sell down
    if operate == 'Sell':
        print('\n做空')
        # 获取最新的卖出价格
        price = exchange.fetch_ticker(symbol)['bid']  # 获取买一价格
        # 下单
        place_order(exchange, order_type='limit', buy_or_sell='sell', symbol=symbol, price=price * 0.99,
                    amount=(freeUSD / price * 0.99))
        # 邮件标题
        email_title += '_做空_' + symbol
        # 邮件内容
        email_content += '做空數量：' + str((freeUSD / price * 0.99)) + '\n'
        email_content += '做空價格：' + str(price) + '\n'
    # =====
    # =====Sell Filled
    if operate == 'SellFilled':
        print('\n平空')
        # 获取最新的买入价格
        price = exchange.fetch_ticker(symbol)['ask']  # 获取卖一价格
        # 获取最新的卖出价格
        place_order(exchange, order_type='limit', buy_or_sell='buy', symbol=symbol, price=price * 1.01,
                    amount=(used_USD / price * 1.01))
        # 邮件标题
        email_title += '_買入_' + symbol
        # 邮件内容
        email_content += '平空數量：' + str((freeUSD / price * 1.01)) + '\n'
        email_content += '平空價格：' + str(price) + '\n'
    # =====
    # =====Buy up
    if operate == 'Buy':
        print('\n做多')
        # 获取最新的买入价格
        price = exchange.fetch_ticker(symbol)['ask']  # 获取卖一价格

        # 获取最新的卖出价格
        place_order(exchange, order_type='limit', buy_or_sell='buy', symbol=symbol, price=price * 1.01,
                    amount=(freeUSD / price * 1.01))
        # 邮件标题
        email_title += '_做多_' + symbol
        # 邮件内容
        email_content += '做多數量：' + str((freeUSD / price * 1.01)) + '\n'
        email_content += '做多價格：' + str(price) + '\n'
    # =====
    # =====Buy Filled
    if operate == 'BuyFilled':
        print('\n平多')
        # 获取最新的卖出价格
        price = exchange.fetch_ticker(symbol)['bid']  # 获取买一价格
        # 下单
        place_order(exchange, order_type='limit', buy_or_sell='sell', symbol=symbol, price=price * 0.99,
                    amount=(used_USD / price * 0.99))
        # 邮件标题
        email_title += '_平多_' + symbol
        # 邮件内容
        email_content += '平多數量：' + str((freeUSD / price * 0.99)) + '\n'
        email_content += '平多價格：' + str(price) + '\n'


