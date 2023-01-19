import numpy as np
import pandas as pd


def risk_reward_threshold(symbol, mt5, buy=True, risk=0.01, reward=0.02):
    # Extract the leverage
    leverage = mt5.account_info().leverage

    # Compute the price
    price = mt5.symbol_info(symbol).ask

    # Extract the number of decimals
    nb_decimal = str(price)[::-1].find(".")

    # Compute the variations in percentage
    var_down = risk / leverage
    var_up = reward / leverage

    # Find the TP and SL threshold in absolute price
    if buy:
        price = mt5.symbol_info(symbol).ask

        # Compute the variations in absolute price
        price_var_down = var_down * price
        price_var_up = var_up * price

        tp = np.round(price + price_var_up, nb_decimal)
        sl = np.round(price - price_var_down, nb_decimal)

    else:

        price = mt5.symbol_info(symbol).bid

        # Compute the variations in absolute price
        price_var_down = var_down * price
        price_var_up = var_up * price

        tp = np.round(price - price_var_up, nb_decimal)
        sl = np.round(price + price_var_down, nb_decimal)

    return tp, sl


def find_filling_mode(symbol, mt5):
    for i in range(2):
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": mt5.symbol_info(symbol).volume_min,
            "type": mt5.ORDER_TYPE_BUY,
            "price": mt5.symbol_info_tick(symbol).ask,
            "type_filling": i,
            "type_time": mt5.ORDER_TIME_GTC}

        result = mt5.order_check(request)

        if result.comment == "Done":
            break

    return i


def send_order(symbol, mt5, lot, buy, sell, id_position=None, pct_tp=0.02, pct_sl=0.01, comment=" No specific comment",
               magic=0):
    # Initialize the bound between MT5 and Python
    mt5.initialize()

    # Extract filling_mode
    filling_type = mt5.find_filling_mode(symbol)

    """ OPEN A TRADE """
    if buy and id_position == None:
        tp, sl = mt5.risk_reward_threshold(symbol, buy=True, risk=pct_sl, reward=pct_tp)

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY,
            "price": mt5.symbol_info_tick(symbol).ask,
            "deviation": 10,
            "tp": tp,
            "sl": sl,
            "magic": magic,
            "comment": comment,
            "type_filling": filling_type,
            "type_time": mt5.ORDER_TIME_GTC}

        result = mt5.order_send(request)

        print(mt5.symbol_info_tick(symbol).ask, tp, sl)
        return result

    if sell and id_position == None:
        tp, sl = mt5.risk_reward_threshold(symbol, buy=False, risk=pct_sl, reward=pct_tp)
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_SELL,
            "price": mt5.symbol_info_tick(symbol).bid,
            "deviation": 10,
            "tp": tp,
            "sl": sl,
            "magic": magic,
            "comment": comment,
            "type_filling": filling_type,
            "type_time": mt5.ORDER_TIME_GTC}

        result = mt5.order_send(request)

        print(mt5.symbol_info_tick(symbol).bid, tp, sl)
        return result

    """ CLOSE A TRADE """
    if buy and id_position != None:
        request = {
            "position": id_position,
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_SELL,
            "price": mt5.symbol_info_tick(symbol).bid,
            "deviation": 10,
            "magic": magic,
            "comment": comment,
            "type_filling": filling_type,
            "type_time": mt5.ORDER_TIME_GTC}

        result = mt5.order_send(request)
        return result

    if sell and id_position != None:
        request = {
            "position": id_position,
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY,
            "price": mt5.symbol_info_tick(symbol).ask,
            "deviation": 10,
            "magic": magic,
            "comment": comment,
            "type_filling": filling_type,
            "type_time": mt5.ORDER_TIME_GTC}

        result = mt5.order_send(request)
        return result


def resume(mt5):
    """ Return the current positions. Position=0 --> Buy """
    # Define the name of the columns that we will create
    colonnes = ["ticket", "position", "symbol", "volume", "magic", "profit", "price", "tp", "sl", "trade_size"]

    # Go take the current open trades
    lists = mt5.positions_get()

    # Create a empty dataframe
    summary = pd.DataFrame()

    # Loop to add each row in dataframe
    for element in lists:
        element_pandas = pd.DataFrame([element.ticket, element.type, element.symbol, element.volume, element.magic,
                                       element.profit, element.price_open, element.tp,
                                       element.sl, mt5.symbol_info(element.symbol).trade_contract_size],
                                      index=colonnes).transpose()
        summary = pd.concat((summary, element_pandas), axis=0)

    try:
        summary["profit %"] = summary.profit / (summary.price * summary.trade_size * summary.volume)
        summary = summary.reset_index(drop=True)

    except:
        pass

    return summary


def trailing_stop_loss(mt5):
    # Extract the current open positions
    mt5.summary = mt5.resume()

    # Verification: Is there any open position?
    if mt5.summary.shape[0] > 0:
        for i in range(mt5.summary.shape[0]):

            # Extract information
            row = mt5.summary.iloc[i]
            symbol = row["symbol"]

            """ CASE 1: Change dynamicly the stop loss for a BUY ORDER """
            # Trailing stop loss for a buy order
            if row["position"] == 0:

                if symbol not in mt5.max_price.keys():
                    mt5.max_price[symbol] = row["price"]

                # Extract current price
                current_price = (mt5.symbol_info(symbol).ask + mt5.symbol_info(symbol).bid) / 2

                # Compute distance between current price an max price
                from_sl_to_curent_price = current_price - row["sl"]
                from_sl_to_max_price = mt5.max_price[symbol] - row["sl"]

                # If current price is greater than preivous max price --> new max price
                if current_price > mt5.max_price[symbol]:
                    mt5.max_price[symbol] = current_price

                # Find the difference between the current minus max
                if from_sl_to_curent_price > from_sl_to_max_price:
                    difference = from_sl_to_curent_price - from_sl_to_max_price

                    # Set filling mode
                    filling_type = mt5.symbol_info(symbol).filling_mode

                    # Set the point
                    point = mt5.symbol_info(symbol).point

                    # Change the sl
                    request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "symbol": symbol,
                        "position": row["ticket"],
                        "volume": row["volume"],
                        "type": mt5.ORDER_TYPE_BUY,
                        "price": row["price"],
                        "sl": row["sl"] + difference,
                        "type_filling": filling_type,
                        "type_time": mt5.ORDER_TIME_GTC,
                    }

                    information = mt5.order_send(request)
                    print(information)

            """ CASE 2: Change dynamicly the stop loss for a SELL ORDER """
            # Trailing stop loss for a sell order
            if row["position"] == 1:

                if symbol not in mt5.min_price.keys():
                    mt5.min_price[symbol] = row["price"]

                # Extract current price
                current_price = (mt5.symbol_info(symbol).ask + mt5.symbol_info(symbol).bid) / 2

                # Compute distance between current price an max price
                from_sl_to_curent_price = row["sl"] - current_price
                from_sl_to_min_price = row["sl"] - mt5.min_price[symbol]

                # If current price is greater than preivous max price --> new max price
                if current_price < mt5.min_price[symbol]:
                    mt5.min_price[symbol] = current_price

                # Find the difference between the current minus max
                if from_sl_to_curent_price > from_sl_to_min_price:
                    difference = from_sl_to_curent_price - from_sl_to_min_price

                    # Set filling mode
                    filling_type = mt5.symbol_info(symbol).filling_mode

                    # Set the point
                    point = mt5.symbol_info(symbol).point

                    # Change the sl
                    request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "symbol": symbol,
                        "position": row["ticket"],
                        "volume": row["volume"],
                        "type": mt5.ORDER_TYPE_SELL,
                        "price": row["price"],
                        "sl": row["sl"] - difference,
                        "type_filling": filling_type,
                        "type_time": mt5.ORDER_TIME_GTC,
                    }

                    information = mt5.order_send(request)
                    print(information)
