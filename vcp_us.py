import yfinance as yf
from finviz.screener import Screener
import pandas as pd
import numpy as np
from tqdm import tqdm
from IPython.display import Image, display
from IPython.core.display import HTML
from finvizfinance.quote import finvizfinance
from vcp_helper import stock_filter
from vcp_helper import test_vcp


def show_image(ticker_s):
    stock = finvizfinance(ticker_s)
    # print(stock.ticker_charts())
    # display(Image(url=stock.ticker_charts()))
    return stock.ticker_charts()


def scanning_wrapper(the_ticker_string):
    ticker = yf.Ticker(the_ticker_string)
    ticker_history = ticker.history(period='max')
    data = stock_filter(ticker_history)

    if data['Fulfillment'].tail(1).iloc[0]:
        url = show_image(the_ticker_string)
        summarise = test_vcp(data)
        return {'stock': the_ticker_string, 'chart': url, 'analysis': summarise}
    else:
        return {'stock': the_ticker_string, 'chart': None, 'analysis': None}


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
# ticker = yf.Ticker("ARRY")
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
        print("\nVCP Matched: ", ticker_string, " res: ", res)
    else:
        print("\nVCP Not Matched: ", ticker_string)
