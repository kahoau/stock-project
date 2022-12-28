import yfinance as yf
import numpy as np
from scipy.stats import linregress
from futu import *
from tqdm import tqdm
import concurrent.futures
from IPython.display import Image, display
from IPython.core.display import HTML
from finvizfinance.quote import finvizfinance


def show_image(ticker_s):
    stock = finvizfinance(ticker_s)
    # print(stock.ticker_charts())
    # display(Image(url=stock.ticker_charts()))
    return stock.ticker_charts()


def slope_reg(arr):
    y = np.array(arr)
    x = np.arange(len(y))
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    return slope


def scanning_wrapper(the_ticker_string):
    ticker = yf.Ticker(the_ticker_string)
    ticker_history = ticker.history(period='max')
    data = stock_filter(ticker_history)

    if data['Fulfillment'].tail(1).iloc[0]:
        # url = show_image(the_ticker_string)
        summarise = test_vcp(data)
        # return {'stock': the_ticker_string, 'chart': url, 'analysis': summarise}
        return {'stock': the_ticker_string, 'chart': None, 'analysis': summarise}
    else:
        return {'stock': the_ticker_string, 'chart': None, 'analysis': None}


def stock_filter(df):
    df['SMA_30'] = df['Close'].rolling(window=30).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_150'] = df['Close'].rolling(window=150).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    df['SMA_slope_200'] = df['SMA_200'].rolling(window=20).apply(slope_reg)
    df['SMA_slope_30'] = df['SMA_30'].rolling(window=20).apply(slope_reg)
    df['52_week_low'] = df['Close'].rolling(window=5 * 52).min()
    df['52_week_high'] = df['Close'].rolling(window=5 * 52).max()

    # Criteria 1: The current price of the security must be greater than the 150 and 200-day SMA
    df['Criteria1'] = (df['Close'] > df['SMA_150']) & (df['Close'] > df['SMA_200'])

    # Criteria 2: The 150 day SMA must be greater than the 200 day SMA
    df['Criteria2'] = (df['SMA_150'] > df['SMA_200'])

    # Criteria 3: The 200 day SMA must be trending up for at least 1 month
    df['Criteria3'] = df['SMA_slope_200'] > 0.0

    # Criteria 4: The 50-day simple moving average must be greater than the 150 SMA and the 200 SMA
    df['Criteria4'] = (df['SMA_50'] > df['SMA_150']) & (df['SMA_150'] > df['SMA_200'])

    # Criteria 5: The current price must be greater than the 50-day simple moving average
    df['Criteria5'] = (df['Close'] > df['SMA_50'])

    # Criteria 6: The current price must be at least 30% above the 52 week low
    df['Criteria6'] = (df['Close'] - df['52_week_low']) / df['52_week_low'] > 0.3

    # Criteria 7: The current price must be within 15% of the 52 week high
    df['Criteria7'] = ((df['Close'] - df['52_week_high']) / df['52_week_high'] < 0.15) & (
            (df['Close'] - df['52_week_high']) / df['52_week_high'] > -0.15)

    # Criteria 8: an alternative of RS, stock's raising rate of last 250 days > 0.89
    # df['Criteria8'] = (df['Close'] - df['Close'].shift(periods=250)) / df['Close'].shift(periods=250) > 0.89
    df['Criteria8'] = True

    # Criteria 9: Pivot(5 day) breakout
    df['Criteria9'] = df['Close'] > ((df['Close']).rolling(window=5).mean() + df['Close'].rolling(window=5).max() + (df['Close']).rolling(
        window=5).min()) / 3

    # Criteria 10: Contraction below 10%
    df['Criteria10'] = (df['Close'].rolling(window=10).max() - df['Close'].rolling(window=10).min()) / (
        df['Close'].rolling(window=10).min()) < 0.1

    df['Criteria11'] = df['SMA_slope_30'] > 0.0

    df['Fulfillment'] = df[['Criteria1', 'Criteria2', 'Criteria3', 'Criteria4', 'Criteria5', 'Criteria6', 'Criteria7',
                            'Criteria8', 'Criteria9', 'Criteria10', 'Criteria11']].all(axis='columns')

    # print("Criteria1...........\n", df['Criteria1'],
    #       "\nCriteria2...........\n", df['Criteria2'],
    #       "\nCriteria3...........\n", df['Criteria3'],
    #       "\nCriteria4...........\n", df['Criteria4'],
    #       "\nCriteria5...........\n", df['Criteria5'],
    #       "\nCriteria6...........\n", df['Criteria6'],
    #       "\nCriteria7...........\n", df['Criteria7'],
    #       "\nCriteria8...........\n", df['Criteria8'],
    #       "\nCriteria9...........\n", df['Criteria9'],
    #       "\nCriteria10...........\n", df['Criteria10'],
    #       "\nCriteria11...........\n", df['Criteria11'])
    return df[['Close', 'Fulfillment']]


def test_vcp(df_i):
    df = pd.DataFrame()
    df['Fulfillment'] = df_i['Fulfillment']
    df['Future_Close_1'] = df_i['Close'].shift(periods=-1)
    df['Future_Close_3'] = df_i['Close'].shift(periods=-3)
    df['Future_Close_5'] = df_i['Close'].shift(periods=-5)
    df['Future_Close_7'] = df_i['Close'].shift(periods=-7)
    # df['Result_1'] = df_i['Close'].pct_change(periods=1).shift(periods=-1)
    # df['Result_3'] = df_i['Close'].pct_change(periods=3).shift(periods=-3)
    # df['Result_5'] = df_i['Close'].pct_change(periods=5).shift(periods=-5)
    # df['Result_7'] = df_i['Close'].pct_change(periods=7).shift(periods=-7)
    df['Result_1'] = (df['Future_Close_1'] - df_i['Close']) / df_i['Close']
    df['Result_3'] = (df['Future_Close_3'] - df_i['Close']) / df_i['Close']
    df['Result_5'] = (df['Future_Close_5'] - df_i['Close']) / df_i['Close']
    df['Result_7'] = (df['Future_Close_7'] - df_i['Close']) / df_i['Close']
    vcp_date = df[df['Fulfillment'] == True]
    # print(vcp_date[['Result_1', 'Result_3', 'Result_5', 'Result_7']])
    # print(vcp_date[['Result_1', 'Result_3', 'Result_5', 'Result_7']].describe())
    return vcp_date


def check_new_vcp(analysis_df):
    analysis_df['time'] = analysis_df.index
    analysis_df['prev_time'] = analysis_df['time'].shift(1)

    analysis_df['delta'] = (analysis_df['time'] - analysis_df['prev_time']).dt.days

    if analysis_df['delta'].tail(1).iloc[0] > 1:
        return True
    else:
        return False


def fast_scan(ticker_list, scanning_wrapper):
    with concurrent.futures.ProcessPoolExecutor(max_workers=12) as executor:
        data_list = list(tqdm(executor.map(scanning_wrapper, ticker_list), total=len(ticker_list)))
    return data_list
