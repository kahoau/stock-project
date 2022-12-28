import yfinance as yf

import pandas as pd
import numpy as np
from tqdm import tqdm

from vcp_helper import stock_filter
from vcp_helper import test_vcp
from vcp_helper import scanning_wrapper
from finviz.screener import Screener


def get_ticker_list():
    filters = ['cap_midover', 'sh_price_o20', 'fa_salesqoq_o5', 'sh_instown_o10', 'sh_insttrans_pos']
    stock_list = Screener(filters=filters, table='Performance', order='Price')
    ticker_table = pd.DataFrame(stock_list.data)
    default_ticker_list = ticker_table['Ticker'].to_list()
    return default_ticker_list


###
# test one stock
###
# SBLK INST
# ticker = yf.Ticker('3690.HK')
# ticker_history = ticker.history(period='max')
# data = stock_filter(ticker_history)
# print("filtered data ................", data, " test_vcp: ...............", test_vcp(data))


###
# test all stocks
###
ticker_list = get_ticker_list()
for ticker_string in tqdm(ticker_list):
    res = scanning_wrapper(ticker_string)
    if res['analysis'] is not None:
        # print("\nVCP Matched: ", ticker_string, " res: ", res)
        print("\nVCP Matched: ", ticker_string, " URL: ", 'https://finviz.com/quote.ashx?t=' + ticker_string + '&p=d')
    else:
        print("\nVCP Not Matched: ", ticker_string)
