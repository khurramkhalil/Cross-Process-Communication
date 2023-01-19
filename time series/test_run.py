from time import sleep
import pandas as pd
from binance import ThreadedWebsocketManager
from binance.client import Client

from starter_comms.secrets import api_secret, api_key

client = Client(api_key, api_secret)

# print(client.get_account())

print(client.get_asset_balance(asset='BTC'))

# get latest price from Binance API
btc_price = client.get_symbol_ticker(symbol="BTCUSDT")
# print full output (dictionary)
print(btc_price)

print(btc_price["price"])

btc_price = {'error': False}


def btc_trade_history(msg):
    """ define how to process incoming WebSocket messages """
    if msg['e'] != 'error':
        print(msg['c'])
        btc_price['last'] = msg['c']
        btc_price['bid'] = msg['b']
        btc_price['last'] = msg['a']
        btc_price['error'] = False
    else:
        btc_price['error'] = True


# init and start the WebSocket
bsm = ThreadedWebsocketManager()
bsm.start()

# subscribe to a stream
bsm.start_symbol_ticker_socket(callback=btc_trade_history, symbol='BTCUSDT')
bsm.start_symbol_ticker_socket(callback=btc_trade_history, symbol='ETHUSDT')

# stop websocket
bsm.stop()

# valid intervals - 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M

# get timestamp of earliest date data is available
timestamp = client._get_earliest_valid_timestamp('BTCUSDT', '1d')
print(timestamp)


# request historical candle (or klines) data
bars = client.get_historical_klines('BTCUSDT', '1d', timestamp, limit=1000)

# delete unwanted data - just keep date, open, high, low, close
for line in bars:
    del line[5:]

bar = [i[:5] for i in bars]

# option 4 - create a Pandas DataFrame and export to CSV
btc_df = pd.DataFrame(bar, columns=['date', 'open', 'high', 'low', 'close'])
btc_df.set_index('date', inplace=True)
print(btc_df.head())


btc_df.index = pd.to_datetime(btc_df.index, unit='ms')
# calculate 20 moving average using Pandas
btc_df['20sma'] = btc_df.close.rolling(20).mean()
print(btc_df.tail(5))


