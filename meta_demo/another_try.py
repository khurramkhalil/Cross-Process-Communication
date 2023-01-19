import time
from datetime import datetime

import MetaTrader5 as mt5
import pandas as pd
import pytz

pd.set_option('display.max_columns', 500)  # number of columns to be displayed
pd.set_option('display.width', 1500)  # max table width to display

# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ", mt5.__author__)
print("MetaTrader5 package version: ", mt5.__version__)

# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# display data on MetaTrader 5 version
print(mt5.version())
# connect to the trade account without specifying a password and a server
# account = 65659936
# # the terminal database password is applied if connection data is set to be remembered
# authorized = mt5.login(account)
# if authorized:
#     print("connected to account #{}".format(account))
# else:
#     print("failed to connect at account #{}, error code: {}".format(account, mt5.last_error()))

# now connect to another trading account specifying the password
account = 65659936
authorized = mt5.login(account, password="ectlvkt3", server="MetaQuotes-Demo")
if authorized:
    # display trading account data 'as is'
    print(mt5.account_info())
    # display trading account data in the form of a list
    print("Show account_info()._asdict():")
    account_info_dict = mt5.account_info()._asdict()
    for prop in account_info_dict:
        print("  {}={}".format(prop, account_info_dict[prop]))
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

# get all symbols
symbols = mt5.symbols_get()
print('Symbols: ', len(symbols))

first_five_symbols = [j[-3] for i, j in enumerate(symbols) if i < 5]
first_five_symbols = [j.name for i, j in enumerate(symbols) if i < 5]

group = ['EURUSD', 'GBPUSD', 'USDCHF', 'USDJPY', 'USDCNH']

# Get data on the specified financial instrument
eur_usd_info = mt5.symbol_info("EURUSD")

# Get all financial instruments from the MetaTrader 5 terminal
five_symbol_info = mt5.symbols_get(group="EURUSD, GBPUSD, USDCHF, USDJPY, USDCNH")

# Get the last tick for the specified financial instrument.
last_tick = mt5.symbol_info_tick("EURUSD")
symbol_info_tick_dict = mt5.symbol_info_tick("GBPUSD")._asdict()

# Select a symbol in the MarketWatch window or remove a symbol from the window
# attempt to enable the display of the EURCAD in MarketWatch
selected = mt5.symbol_select("EURCAD", True)
if not selected:
    print("Failed to select EURCAD, error code =", mt5.last_error())
else:
    symbol_info = mt5.symbol_info("EURCAD")
    print(symbol_info)
    print("EURCAD: currency_base =", symbol_info.currency_base, "  currency_profit =", symbol_info.currency_profit,
          "  currency_margin =", symbol_info.currency_margin)
    print()

    symbol_info_dict = symbol_info._asdict()
    # convert the dictionary into DataFrame and print
    df = pd.DataFrame(list(symbol_info_dict.items()), columns=['property', 'value'])

# Subscribes the MetaTrader 5 terminal to the Market Depth change events for a specified symbol
market_depth_change = mt5.market_book_add("EURUSD")
# subscribe to market depth updates for EURUSD (Depth of Market)
if mt5.market_book_add('EURUSD'):
    # get the market depth data 10 times in a loop
    for i in range(1):
        # get the market depth content (Depth of Market)
        # Returns a tuple from BookInfo featuring Market Depth entries for the specified symbol
        items = mt5.market_book_get('EURCAD')
        # display the entire market depth 'as is' in a single string
        print(items)
        # now display each order separately for more clarity
        if items:
            for it in items:
                # order content
                print(it._asdict())
        # pause for 5 seconds before the next request of the market depth data
        time.sleep(5)
    # cancel the subscription to the market depth updates (Depth of Market)
    mt5.market_book_release('EURUSD')
else:
    print("mt5.market_book_add('EURUSD') failed, error code =", mt5.last_error())

# Cancels subscription of the MetaTrader 5 terminal to the Market Depth change events for a specified symbol.
release = mt5.market_book_release('EURCAD')
if not release:
    print("mt5.market_book_release('EURUSD') failed, error code =", mt5.last_error())

# set time zone to UTC
timezone = pytz.timezone("Etc/UTC")
# create 'datetime' object in UTC time zone to avoid the implementation of a local time zone offset (Y, M, D)
utc_from = datetime(2023, 1, 1, tzinfo=timezone)

# Get bars from the MetaTrader 5 terminal starting from the specified date.
rates = mt5.copy_rates_from("EURUSD", mt5.TIMEFRAME_H4, utc_from, 10)

# create DataFrame out of the obtained data
rates_frame = pd.DataFrame(rates)
# convert time in seconds into the datetime format
rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')

# Get bars from the MetaTrader 5 terminal starting from the specified index.
# get 10 GBPUSD D1 bars from the current day
# rates_pos = mt5.copy_rates_from_pos("GBPUSD", mt5.TIMEFRAME_D1, 0, 20)
rates_pos = mt5.copy_rates_from_pos("GBPUSD", mt5.TIMEFRAME_M1, 0, 20)

# create DataFrame out of the obtained data
rates_frame_pos = pd.DataFrame(rates_pos)
# convert time in seconds into the datetime format
rates_frame_pos['time'] = pd.to_datetime(rates_frame_pos['time'], unit='s')

# Get bars in the specified date range from the MetaTrader 5 terminal.
# copy_rates_range(
#    symbol,       // symbol name
#    timeframe,    // timeframe
#    date_from,    // date the bars are requested from
#    date_to       // date, up to which the bars are requested
#    )

# set time zone to UTC
timezone = pytz.timezone("Etc/UTC")
# create 'datetime' objects in UTC time zone to avoid the implementation of a local time zone offset
utc_from = datetime(2023, 1, 16, tzinfo=timezone)
# utc_to = datetime(2023, 1, 11, hour=13, tzinfo=timezone)
utc_to = datetime.now(timezone)

# get bars from USDJPY M5 within the interval of 2020.01.10 00:00 - 2020.01.11 13:00 in UTC time zone
rates_range = mt5.copy_rates_range("USDJPY", mt5.TIMEFRAME_M5, utc_from, utc_to)

# create DataFrame out of the obtained data
rates_frame_range = pd.DataFrame(rates_range)
# convert time in seconds into the 'datetime' format
rates_frame_range['time'] = pd.to_datetime(rates_frame_range['time'], unit='s')

# Get ticks from the MetaTrader 5 terminal starting from the specified date
utc_from = datetime(2023, 1, 15, tzinfo=timezone)
# request 100 000 EURUSD ticks starting from 10.01.2019 in UTC time zone
ticks = mt5.copy_ticks_from("EURUSD", utc_from, 1000, mt5.COPY_TICKS_ALL)
print("Ticks received:", len(ticks))

# display data on each tick on a new line
print("Display obtained ticks 'as is'")
count = 0
if ticks.size:
    for tick in ticks:
        count += 1
        print(tick)
        if count >= 10:
            break

# Get ticks for the specified date range from the MetaTrader 5 terminal
ticks = mt5.copy_ticks_range("AUDUSD", utc_from, utc_to, mt5.COPY_TICKS_ALL)
print("Ticks received:", len(ticks))

# create DataFrame out of the obtained data
ticks_frame = pd.DataFrame(ticks)
# convert time in seconds into the datetime format
ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')

# display data
print("\nDisplay dataframe with ticks")
print(ticks_frame.head(10))

# Get the number of active orders.
# check the presence of active orders
orders = mt5.orders_total()
if orders > 0:
    print("Total orders=", orders)
else:
    print("Orders not found")

# Get active orders with the ability to filter by symbol or ticket. There are three options
# 1) Call without parameters. Return active orders on all symbols.
# 2) Call specifying a symbol active orders should be received for --> orders_get(symbol="SYMBOL"      // symbol name)
# 3) Call specifying the order ticket  --> orders_get(ticket=TICKET      // ticket number)
# 4) Call specifying a symbol active orders should be received for  --> orders_get(group="GROUP")

# display data on active orders on GBPUSD
orders = mt5.orders_get(symbol="GBPUSD")
if orders is None:
    print("No orders on GBPUSD, error code={}".format(mt5.last_error()))
else:
    print("Total orders on GBPUSD:", len(orders))
    # display all active orders
    for order in orders:
        print(order)

# get the list of orders on symbols whose names contain "*GBP*"
gbp_orders = mt5.orders_get(group="*GBP*")
if all(gbp_orders):
    print("No orders with group=\"*GBP*\", error code={}".format(mt5.last_error()))
else:
    print("orders_get(group=\"*GBP*\")={}".format(len(gbp_orders)))
    # display these orders as a table using pandas.DataFrame
    df = pd.DataFrame(list(gbp_orders), columns=gbp_orders[0]._asdict().keys())
    df.drop(
        ['time_done', 'time_done_msc', 'position_id', 'position_by_id', 'reason', 'volume_initial', 'price_stoplimit'],
        axis=1, inplace=True)
    df['time_setup'] = pd.to_datetime(df['time_setup'], unit='s')
    print(df)

# Return margin in the account currency to perform a specified trading operation.
# The function allows estimating the margin necessary for a specified order type on the current account and in the
# current market environment without considering the current pending orders and open positions.

# arrange the symbol list
symbols = ("EURUSD", "GBPUSD", "USDJPY", "USDCHF", "EURJPY", "GBPJPY")
print("Symbols to check margin:", symbols)
action = mt5.ORDER_TYPE_BUY
action = mt5.ORDER_TYPE_SELL
lot = 0.1
for symbol in symbols:
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(symbol, "not found, skipped")
        continue
    if not symbol_info.visible:
        print(symbol, "is not visible, trying to switch on")
        if not mt5.symbol_select(symbol, True):
            print("symbol_select({}}) failed, skipped", symbol)
            continue
    ask = mt5.symbol_info_tick(symbol).ask
    margin = mt5.order_calc_margin(action, symbol, lot, ask)
    if margin:
        print(f"{symbol} buy {lot} lot margin: {margin} {account_currency}")
    else:
        print("order_calc_margin failed: , error code =", mt5.last_error())

# Return profit in the account currency for a specified trading operation.
# arrange the symbol list
symbols = ("EURUSD", "GBPUSD", "USDJPY")
print("Symbols to check margin:", symbols)
# estimate profit for buying and selling
lot = 1.0
distance = 300
for symbol in symbols:
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(symbol, "not found, skipped")
        continue
    if not symbol_info.visible:
        print(symbol, "is not visible, trying to switch on")
        if not mt5.symbol_select(symbol, True):
            print("symbol_select({}}) failed, skipped", symbol)
            continue
    point = mt5.symbol_info(symbol).point
    symbol_tick = mt5.symbol_info_tick(symbol)
    ask = symbol_tick.ask
    bid = symbol_tick.bid
    buy_profit = mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, symbol, lot, ask, ask + distance * point)
    if buy_profit:
        print("   buy {} {} lot: profit on {} points => {} {}".format(symbol, lot, distance, buy_profit,
                                                                      account_currency))
    else:
        print("order_calc_profit(ORDER_TYPE_BUY) failed, error code =", mt5.last_error())

    sell_profit = mt5.order_calc_profit(mt5.ORDER_TYPE_SELL, symbol, lot, bid, bid - distance * point)
    if sell_profit:
        print("   sell {} {} lots: profit on {} points => {} {}".format(symbol, lot, distance, sell_profit,
                                                                        account_currency))
    else:
        print("order_calc_profit(ORDER_TYPE_SELL) failed, error code =", mt5.last_error())

# Check funds sufficiency for performing a required trading operation.


# prepare the request structure
symbol = "USDJPY"
symbol_info = mt5.symbol_info(symbol)
if symbol_info is None:
    print(symbol, "not found, can not call order_check()")
    # quit()

# if the symbol is unavailable in MarketWatch, add it
if not symbol_info.visible:
    print(symbol, "is not visible, trying to switch on")
    if not mt5.symbol_select(symbol, True):
        print("symbol_select({}}) failed, exit", symbol)

# prepare the request
point = mt5.symbol_info(symbol).point
request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbol,
    "volume": 1.0,
    "type": mt5.ORDER_TYPE_BUY,
    "price": mt5.symbol_info_tick(symbol).ask,
    "sl": mt5.symbol_info_tick(symbol).ask - 100 * point,
    "tp": mt5.symbol_info_tick(symbol).ask + 100 * point,
    "deviation": 10,
    "magic": 234000,
    "comment": "python script",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_RETURN,
}

# perform the check and display the result 'as is'
result = mt5.order_check(request)
print(result)

# request the result as a dictionary and display it element by element
result_dict = result._asdict()
for field in result_dict.keys():
    print("   {}={}".format(field, result_dict[field]))
    # if this is a trading request structure, display it element by element as well
    if field == "request":
        traderequest_dict = result_dict[field]._asdict()
        for tradereq_filed in traderequest_dict:
            print("       traderequest: {}={}".format(tradereq_filed, traderequest_dict[tradereq_filed]))

# Send a request to perform a trading operation from the terminal to the trade server.
# A trading request passes several verification stages on the trade server. First, the validity of all the necessary
# request fields is checked. If there are no errors, the server accepts the order for further handling.

symbol = "EURUSD"
symbol_info = mt5.symbol_info(symbol)
# if the symbol is unavailable in MarketWatch, add it
if not symbol_info.visible:
    print(symbol, "is not visible, trying to switch on")
    if not mt5.symbol_select(symbol, True):
        print("symbol_select({}}) failed, exit", symbol)

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
    "magic": 234000,
    "comment": "python script open",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_RETURN,
}

