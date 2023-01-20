import time

import MetaTrader5 as mt5
import pandas as pd
import pytz

pd.set_option('display.max_columns', 500)  # number of columns to be displayed
pd.set_option('display.width', 1500)  # max table width to display

print("MetaTrader5 package version: ", mt5.__version__)

# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# now connect to a trading account specifying the password
account = 65724883
authorized = mt5.login(account, password="wh1qhrqk", server="MetaQuotes-Demo")
if authorized:
    print("Authorization successful")
    # display trading account data 'as is'
    # print(mt5.account_info())
    # display trading account data in the form of a list
    # print("Show account_info()._asdict():")
    # account_info_dict = mt5.account_info()._asdict()
    # for prop in account_info_dict:
    #     print("  {}={}".format(prop, account_info_dict[prop]))
else:
    print("failed to connect at account #{}, error code: {}".format(account, mt5.last_error()))

# get account currency
account_currency = mt5.account_info().currency
print("Account currency:", account_currency)

# get the total number of financial instruments
num_symbols = mt5.symbols_total()
if num_symbols > 0:
    print("Total symbols =", num_symbols)
else:
    print("symbols not found")

symbol = "EURUSD"
# attempt to enable the display of the EURCAD in MarketWatch
selected = mt5.symbol_select(symbol, True)
if not selected:
    print("Failed to select EURUSD, error code =", mt5.last_error())
else:
    symbol_info = mt5.symbol_info(symbol)
    # print(symbol_info)
    print("EURUSD: currency_base =", symbol_info.currency_base, "  currency_profit =", symbol_info.currency_profit,
          "  currency_margin =", symbol_info.currency_margin)
    print()

    symbol_info_dict = symbol_info._asdict()
    # convert the dictionary into DataFrame and print
    df = pd.DataFrame(list(symbol_info_dict.items()), columns=['property', 'value'])

# set time zone to UTC
timezone = pytz.timezone("Etc/UTC")

lot = 0.1
point = mt5.symbol_info(symbol).point
price = mt5.symbol_info_tick(symbol).ask
deviation = 20
request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbol,
    "volume": lot,
    "type": mt5.ORDER_TYPE_BUY,
    "price": price,
    "sl": price - 100 * point,
    "tp": price + 100 * point,
    "deviation": deviation,
    "magic": 2340000,
    "comment": "python script open",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_RETURN,
}

# send a trading request
result = mt5.order_send(request)
# check the execution result
print("1. order_send(): by {} {} lots at {} with deviation={} points".format(symbol, lot, price, deviation))
if result.retcode != mt5.TRADE_RETCODE_DONE:
    print("2. order_send failed, retcode={}".format(result.retcode))
    # request the result as a dictionary and display it element by element
    result_dict = result._asdict()
    for field in result_dict.keys():
        print("   {}={}".format(field, result_dict[field]))
        # if this is a trading request structure, display it element by element as well
        if field == "request":
            traderequest_dict = result_dict[field]._asdict()
            for tradereq_filed in traderequest_dict:
                print("       traderequest: {}={}".format(tradereq_filed, traderequest_dict[tradereq_filed]))
    print("shutdown() and quit")
    mt5.shutdown()
    quit()

print("2. order_send done, ", result)
print("   opened position with POSITION_TICKET={}".format(result.order))
print("   sleep 2 seconds before closing position #{}".format(result.order))
time.sleep(2)
# create a close request
position_id = result.order
price = mt5.symbol_info_tick(symbol).bid
deviation = 20
request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbol,
    "volume": lot,
    "type": mt5.ORDER_TYPE_SELL,
    "position": position_id,
    "price": price,
    "deviation": deviation,
    "magic": 234000,
    "comment": "python script close",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_RETURN,
}
# send a trading request
result = mt5.order_send(request)
# check the execution result
print("3. close position #{}: sell {} {} lots at {} with deviation={} points".format(position_id, symbol, lot, price,
                                                                                     deviation))
if result.retcode != mt5.TRADE_RETCODE_DONE:
    print("4. order_send failed, retcode={}".format(result.retcode))
    print("   result", result)
else:
    print("4. position #{} closed, {}".format(position_id, result))
    # request the result as a dictionary and display it element by element
    result_dict = result._asdict()
    for field in result_dict.keys():
        print("   {}={}".format(field, result_dict[field]))
        # if this is a trading request structure, display it element by element as well
        if field == "request":
            traderequest_dict = result_dict[field]._asdict()
            for tradereq_filed in traderequest_dict:
                print("       traderequest: {}={}".format(tradereq_filed, traderequest_dict[tradereq_filed]))

# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
