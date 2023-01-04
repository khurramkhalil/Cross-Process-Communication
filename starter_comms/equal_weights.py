import math
from statistics import mean

import pandas as pd
import requests
from scipy import stats

# from secrets import IEX_CLOUD_API_TOKEN
IEX_CLOUD_API_TOKEN = 'Tpk_059b97af715d417d9f49f50b51b1c448'

stocks = pd.read_csv('sp_500_stocks.csv')
stocks = stocks
symbol = 'AAPL'
api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/stats?token={IEX_CLOUD_API_TOKEN}'
data = requests.get(api_url).json()


# Function sourced from
# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
#     print(symbol_strings[i])

my_columns = ['Ticker', 'Price', 'One-Year Price Return', 'Number of Shares to Buy']
intermediate_var = []
for symbol_string in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=stats,quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        try:
            intermediate_var.append(
                [symbol, data[symbol]['quote']['latestPrice'], data[symbol]['stats']['year1ChangePercent'], 'N/A'])

        except KeyError:
            pass

final_dataframe = pd.DataFrame(data=intermediate_var, columns=my_columns)
final_dataframe.sort_values('One-Year Price Return', ascending=False, inplace=True)


# final_dataframe = final_dataframe[:51]
# final_dataframe.reset_index(drop=True, inplace=True)


def portfolio_input():
    global portfolio_size
    portfolio_size = input("Enter the value of your portfolio:")

    try:
        val = float(portfolio_size)
    except ValueError:
        print("That's not a number! \n Try again:")
        portfolio_size = input("Enter the value of your portfolio:")


portfolio_input()
position_size = float(portfolio_size) / len(final_dataframe.index)
for i in range(0, len(final_dataframe['Ticker'])):
    final_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size / final_dataframe['Price'][i])

hqm_columns = [
    'Ticker',
    'Price',
    'Number of Shares to Buy',
    'One-Year Price Return',
    'One-Year Return Percentile',
    'Six-Month Price Return',
    'Six-Month Return Percentile',
    'Three-Month Price Return',
    'Three-Month Return Percentile',
    'One-Month Price Return',
    'One-Month Return Percentile',
    'HQM Score'
]

hqm_list = []
for symbol_string in symbol_strings:
    #     print(symbol_strings)
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=stats,quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        hqm_list.append(
            [symbol, data[symbol]['quote']['latestPrice'], 'N/A', data[symbol]['stats']['year1ChangePercent'],
             'N/A', data[symbol]['stats']['month6ChangePercent'], 'N/A', data[symbol]['stats']['month3ChangePercent'],
             'N/A', data[symbol]['stats']['month1ChangePercent'], 'N/A', 'N/A'])

hqm_dataframe = pd.DataFrame(data=hqm_list, columns=hqm_columns)

time_periods = ['One-Year', 'Six-Month', 'Three-Month', 'One-Month']

for row in hqm_dataframe.index:
    for time_period in time_periods:
        hqm_dataframe.loc[row, f'{time_period} Return Percentile'] = stats.percentileofscore(
            hqm_dataframe[f'{time_period} Price Return'], hqm_dataframe.loc[row, f'{time_period} Price Return']) / 100

# # Print each percentile score to make sure it was calculated properly
# for time_period in time_periods:
#     print(hqm_dataframe[f'{time_period} Return Percentile'])

for row in hqm_dataframe.index:
    momentum_percentiles = []
    for time_period in time_periods:
        momentum_percentiles.append(hqm_dataframe.loc[row, f'{time_period} Return Percentile'])
    hqm_dataframe.loc[row, 'HQM Score'] = mean(momentum_percentiles)

hqm_dataframe.sort_values(by='HQM Score', ascending=False, inplace=True)
hqm_dataframe = hqm_dataframe[:50]
hqm_dataframe.reset_index(inplace=True, drop=True)
# portfolio_input()

position_size = float(portfolio_size) / len(hqm_dataframe.index)
for i in range(len(hqm_dataframe)):
    hqm_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size / hqm_dataframe.loc[i, 'Price'])

print(hqm_dataframe)
