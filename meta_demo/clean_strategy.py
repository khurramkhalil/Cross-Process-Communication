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
account = 65659936
authorized = mt5.login(account, password="ectlvkt3", server="MetaQuotes-Demo")
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
