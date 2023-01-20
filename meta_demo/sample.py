import warnings

import MetaTrader5 as mt5

warnings.filterwarnings("ignore")
mt5.initialize()


class MT5:

    def get_data(symbol, n, timeframe=mt5.TIMEFRAME_M5):
        """ Function to import the data of the chosen symbol"""

        # Initialize the connection if there is not
        mt5.initialize()

        # Current date extract
        utc_from = datetime.now()

        # Import the data into a tuple
        rates = mt5.copy_rates_from(symbol, timeframe, utc_from, n)

        # Tuple to dataframe
        rates_frame = pd.DataFrame(rates)

        # Convert time in seconds into the datetime format
        rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')

        # Convert the column "time" in the right format
        rates_frame['time'] = pd.to_datetime(rates_frame['time'], format='%Y-%m-%d')

        # Set column time as the index of the dataframe
        rates_frame = rates_frame.set_index('time')
        return rates_frame

    def orders(symbol, lot, buy=True, id_position=None):
        """ Send the orders """

        # Initialize the connection if there is not
        if mt5.initialize() == False:
            mt5.initialize()

        # # Get filling mode
        filling_mode = mt5.symbol_info(symbol).filling_mode + 1

        # Take ask price
        ask_price = mt5.symbol_info_tick(symbol).ask

        # Take bid price
        bid_price = mt5.symbol_info_tick(symbol).bid

        # Take the point of the asset
        point = mt5.symbol_info(symbol).point

        deviation = 20  # mt5.getSlippage(symbol)
        # **************************** Open a trade *****************************
        if id_position == None:

            # Buy order Parameters
            if buy:
                type_trade = mt5.ORDER_TYPE_BUY
                sl = ask_price * (1 - 0.01)
                tp = ask_price * (1 + 0.01)
                price = ask_price

            # Sell order Parameters
            else:
                type_trade = mt5.ORDER_TYPE_SELL
                sl = bid_price * (1 + 0.01)
                tp = bid_price * (1 - 0.01)
                price = bid_price

            # Open the trade
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": type_trade,
                "price": price,
                "deviation": deviation,
                "sl": sl,
                "tp": tp,
                "magic": 234000,
                "comment": "python script order",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": filling_mode,
            }
            # send a trading request
            result = mt5.order_send(request)
            result_comment = result.comment

        # **************************** Close a trade *****************************
        else:
            # Buy order Parameters
            if buy:
                type_trade = mt5.ORDER_TYPE_SELL
                price = bid_price

            # Sell order Parameters
            else:
                type_trade = mt5.ORDER_TYPE_BUY
                price = ask_price

            # Close the trade
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": type_trade,
                "position": id_position,
                "price": price,
                "deviation": deviation,
                "magic": 234000,
                "comment": "python script order",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": filling_mode,
            }

            # send a trading request
            result = mt5.order_send(request)
            result_comment = result.comment
        return result.comment

    def resume():
        """ Return the current positions. Position=0 --> Buy """
        # Initialize the connection if there is not
        mt5.initialize()

        # Define the name of the columns that we will create
        colonnes = ["ticket", "position", "symbol", "volume"]

        # Go take the current open trades
        current = mt5.positions_get()

        # Create a empty dataframe
        summary = pd.DataFrame()

        # Loop to add each row in dataframe
        # (Can be ameliorate using of list of list)
        for element in current:
            element_pandas = pd.DataFrame([element.ticket,
                                           element.type,
                                           element.symbol,
                                           element.volume],
                                          index=colonnes).transpose()
            summary = pd.concat((summary, element_pandas), axis=0)

        return summary

    def run(symbol, long, short, lot):

        # Initialize the connection if there is not
        if mt5.initialize() == False:
            mt5.initialize()

        # Choose your  symbol
        print("------------------------------------------------------------------")
        print("Date: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("SYMBOL:", symbol)

        # Initialize the device
        current_open_positions = MT5.resume()
        # Buy or sell
        print(f"BUY: {long} \t  SHORT: {short}")

        """ Close trade eventually """
        # Extraction type trade
        try:
            position = current_open_positions.loc[current_open_positions["symbol"] == symbol].values[0][1]

            identifier = current_open_positions.loc[current_open_positions["symbol"] == symbol].values[0][0]
        except:
            position = None
            identifier = None

        print(f"POSITION: {position} \t ID: {identifier}")

        # Close trades
        if long == True and position == 0:
            long = False

        elif long == False and position == 0:
            res = MT5.orders(symbol, lot, buy=True, id_position=identifier)
            print(f"CLOSE LONG TRADE: {res}")

        elif short == True and position == 1:
            short = False

        elif short == False and position == 1:
            res = MT5.orders(symbol, lot, buy=False, id_position=identifier)
            print(f"CLOSE SHORT TRADE: {res}")

        else:
            pass

        """ Buy or short """
        if long == True:
            res = MT5.orders(symbol, lot, buy=True, id_position=None)
            print(f"OPEN LONG TRADE: {res}")

        if short == True:
            res = MT5.orders(symbol, lot, buy=False, id_position=None)
            print(f"OPEN SHORT TRADE: {res}")

        print("------------------------------------------------------------------")

    def close_all_night():
        result = MT5.resume()
        for i in range(len(result)):
            before = mt5.account_info().balance
            row = result.iloc[0 + i:1 + i, :]
            if row["position"][0] == 0:
                res = MT5.orders(row["symbol"][0], row["volume"][0], buy=True, id_position=row["ticket"][0])

            else:
                res = MT5.orders(row["symbol"][0], row["volume"][0], buy=False, id_position=row["ticket"][0])


import time
import ta
import numpy as np
import warnings
from datetime import datetime
import pandas as pd
import MetaTrader5 as mt5

warnings.filterwarnings("ignore")
mt5.initialize()
account = 65724883
authorized = mt5.login(account, password="wh1qhrqk", server="MetaQuotes-Demo")
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

def svm_reg_trading(symbol):
    def feature_engineering(df):
        """ Create new variables"""

        # We copy the dataframe to avoid interferences in the data
        df_copy = df.dropna().copy()

        # Create the returns
        df_copy["returns"] = df_copy["close"].pct_change(1)

        # Create the SMAs
        df_indicators = ta.add_all_ta_features(
            df, open="open", high="high", low="low", close="close", volume="volume", fillna=True).shift(1)

        dfc = pd.concat((df_indicators, df_copy), axis=1)

        return dfc.dropna()

    # Import the data
    df = MT5.get_data(symbol, 3500)[["open", "high", "low", "close", "tick_volume"]]

    df.columns = ["open", "high", "low", "close", "volume"]

    dfc = feature_engineering(df)

    # Percentage train set
    split = int(0.99 * len(dfc))

    # Train set creation
    X_train = dfc.iloc[:split, 6:dfc.shape[1] - 1]
    y_train = dfc[["returns"]].iloc[:split]

    # Test set creation
    X_test = dfc.iloc[split:, 6:dfc.shape[1] - 1]
    y_test = dfc[["returns"]].iloc[split:]

    # What you need to remind about this chapter
    from sklearn.preprocessing import StandardScaler
    sc = StandardScaler()

    X_train_sc = sc.fit_transform(X_train)
    X_test_sc = sc.transform(X_test)

    from sklearn.decomposition import PCA
    pca = PCA(n_components=6)
    X_train_pca = pca.fit_transform(X_train_sc)
    X_test_pca = pca.transform(X_test_sc)

    # Import the class
    from sklearn.svm import SVR

    # Initialize the class
    reg = SVR()

    # Fit the model
    reg.fit(X_train_pca, y_train)

    # Create predictions for the whole dataset
    X = np.concatenate((X_train_pca, X_test_pca), axis=0)

    dfc["prediction"] = reg.predict(X)

    buy = dfc["prediction"].iloc[-1] > 0
    sell = not buy
    return buy, sell


mt5.initialize()
# True = Live Trading and False = Screener
live = True

if live:
    current_account_info = mt5.account_info()
    print("------------------------------------------------------------------")
    print("Date: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print(f"Balance: {current_account_info.balance} USD, \t"
          f"Equity: {current_account_info.equity} USD, \t"
          f"Profit: {current_account_info.profit} USD")
    print("------------------------------------------------------------------")

info_order = {
    "EURUSD": ["EURUSD", 0.5],
    # "AUDCAD": ["AUDCAD", 0.1],
    # "GBPUSD": ["GBPUSD", 0.3]
}

start = datetime.now().strftime("%H:%M:%S")
while True:
    # Verfication for launch
    if datetime.now().weekday() not in (1, 2):
        is_time = datetime.now().strftime("%H:%M:%S") == start  # "23:59:59"
    else:
        is_time = False
        print("Time mismatch")

    # Launch the algorithm
    if True:

        # Open the trades
        for asset in info_order.keys():

            # Initialize the inputs
            symbol = info_order[asset][0]
            lot = info_order[asset][1]

            # Create the signals
            buy, sell = svm_reg_trading(symbol)

            # Run the algorithm
            if live:
                MT5.run(symbol, buy, sell, lot)

            else:
                print(f"Symbol: {symbol}\t"
                      f"Buy: {buy}\t"
                      f"Sell: {sell}")
        time.sleep(1)
