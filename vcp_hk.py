from futu import *
import pandas as pd
import time
from tqdm import tqdm

from vcp_helper import stock_filter
from vcp_helper import test_vcp

from datetime import date
from dateutil.relativedelta import relativedelta


def scanning_wrapper(scanning_quote_ctx, scanning_ticker_string):
    # good enough to calc SMA_250 and seems like futu only supports 3 years for the history_kline api
    two_half_yrs_ago = str(date.today() - relativedelta(months=30))
    today = str(date.today())

    scanning_ret, scanning_data, page_reg_key = \
        scanning_quote_ctx.request_history_kline(scanning_ticker_string, start=two_half_yrs_ago, end=today)
    if (scanning_ret == RET_OK) & (scanning_data.shape[0] > 0):
        df = pd.DataFrame()
        df['Close'] = scanning_data['close']
        # df['Date'] = scanning_data['time_key']
        filtered_df = stock_filter(df)
        if filtered_df['Fulfillment'].tail(1).iloc[0]:
            url = 'http://www.aastocks.com/tc/stocks/quote/detailchart.aspx?symbol=' + scanning_ticker_string[3:]
            summarise = test_vcp(filtered_df)
            return {'stock': scanning_ticker_string, 'chart': url, 'analysis': summarise}
        else:
            return {'stock': scanning_ticker_string, 'chart': None, 'analysis': None}
    else:
        return {'stock': scanning_ticker_string, 'chart': None, 'analysis': None}


def get_ticker_list(the_quote_ctx):
    default_ret, default_data = the_quote_ctx.get_plate_stock('HK.Motherboard')
    return default_data['code'].values


###
# main
###
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret, data = quote_ctx.get_plate_stock('HK.Motherboard')

ticker_list = get_ticker_list(quote_ctx)
for ticker_string in tqdm(ticker_list):
    res = scanning_wrapper(quote_ctx, ticker_string)
    if res['analysis'] is not None:
        print("\nVCP Matched: ", ticker_string, " res: ", res)
    else:
        print("\nVCP Not Matched: ", ticker_string)
    time.sleep(1)

quote_ctx.close()  # 结束后记得关闭当条连接，防止连接条数用尽

