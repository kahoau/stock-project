from futu import *
import pandas as pd
import time
from tqdm import tqdm

from vcp_helper import scanning_wrapper


def get_ticker_list(the_quote_ctx):
    default_ret, default_data = the_quote_ctx.get_plate_stock('HK.Motherboard')
    return default_data['code'].values


def to_yfinance_format(temp_ticker_string):
    return str(int(temp_ticker_string[3:])).zfill(4) + '.HK'


def to_hk_stocks_format(temp_ticker_string):
    return str(int(temp_ticker_string[3:]))


###
# main
###
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret, data = quote_ctx.get_plate_stock('HK.Motherboard')

ticker_list = get_ticker_list(quote_ctx)

for ticker_string in tqdm(ticker_list):
    formatted_ticker_string = to_yfinance_format(ticker_string)
    res = scanning_wrapper(formatted_ticker_string)
    if res['analysis'] is not None:
        print("\nVCP Matched: ", ticker_string, " URL: ", 'http://www.aastocks.com/tc/stocks/quote/detailchart.aspx?symbol=' + to_hk_stocks_format(ticker_string))
    else:
        print("\nVCP Not Matched: ", ticker_string)
    time.sleep(1)

quote_ctx.close()  # 结束后记得关闭当条连接，防止连接条数用尽


