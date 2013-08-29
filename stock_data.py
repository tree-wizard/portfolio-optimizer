import datetime as dt
import pandas as pd

import finance_library.QSutils.DataAccess as da

import numpy as np
import os

DATAOBJ = da.DataAccess('Yahoo')
KEYS = ['open', 'high', 'low', 'close', 'volume', 'actual_close']


def _cache_dates():
    try:
        filename = os.path.join(os.path.dirname(__file__), 'finance_library/NYSE_dates.txt')
    except KeyError:
        print "Please be sure you have NYSE_dates.txt in the directory"

    datestxt = np.loadtxt(filename, dtype=str)
    dates = []
    for i in datestxt:
        dates.append(dt.datetime.strptime(i, "%m/%d/%Y"))
    return pd.TimeSeries(index=dates, data=dates)


GTS_DATES = _cache_dates()


def get_NYSE_days(startday = dt.datetime(2006, 1, 1), endday = dt.datetime(2012, 5, 20)):
    timeofday = dt.timedelta(hours=16)

    start = startday - timeofday
    end = endday - timeofday
    dates = GTS_DATES[start:end]

    ret = [x + timeofday for x in dates]
    return(ret)

def returnize0(nds):
    if type(nds) == type(pd.DataFrame()):
        nds = (nds / nds.shift(1)) - 1.0
        nds = nds.fillna(0.0)
        return nds

    s= np.shape(nds)
    if len(s)==1:
        nds=np.expand_dims(nds,1)
    nds[1:, :] = (nds[1:, :] / nds[0:-1]) - 1
    nds[0, :] = np.zeros(nds.shape[1])
    return nds

def close_prices(symbols, ldt_timestamps):
    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = DATAOBJ.get_data(ldt_timestamps, symbols, KEYS)
    d_data = dict(zip(KEYS, ldf_data))

    # Filling the data for NAN
    for s_key in KEYS:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    # Getting the numpy ndarray of close prices.
    na_price = d_data['close'].values
    # normalize prices
    na_normalized_price = na_price / na_price[0, :]

    return na_normalized_price

def simulate(na_rets, alloc):
    # Estimate portfolio returns
    na_portrets = np.sum(na_rets * alloc, axis=1)
    cum_ret = na_portrets[-1]
    returnize0(na_portrets)

    # Statistics to calculate
    stddev = np.std(na_portrets)
    daily_ret = np.mean(na_portrets)
    sharpe = (np.sqrt(252) * daily_ret) / stddev

    return stddev, daily_ret, sharpe, cum_ret

def portfolio_stats(symbols, alloc, na_rets, timestamps):
    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = DATAOBJ.get_data(timestamps, symbols, KEYS)
    d_data = dict(zip(KEYS, ldf_data))

    # Copying close price into separate dataframe to find rets
    df_rets = d_data['close'].copy()
    # Filling the data.
    df_rets = df_rets.fillna(method='ffill')
    df_rets = df_rets.fillna(method='bfill')

    # Numpy matrix of filled data values
    na_rets = df_rets.values
    na_rets = na_rets / na_rets[0, :]

    max_sharpe = -1000
    final_stddev = -1000
    final_daily_ret = -1000
    final_cum_ret = -1000
    best_portfolio = alloc
  
    for i in range(0, 101, 10):
        left_after_i = 101 - i
        for j in range(0, left_after_i, 10):
            left_after_j = 101 - i - j
            for k in range(0, left_after_j, 10):
                left_after_k = 100 - i - j - k
                alloc = [i, j, k, left_after_k]
                alloc = [x * 0.01 for x in alloc]
                stddev, daily_ret, sharpe, cum_ret = simulate(na_rets, alloc)
                if sharpe > max_sharpe:
                    max_sharpe = sharpe
                    final_stddev = stddev
                    final_cum_ret = cum_ret
                    final_daily_ret = daily_ret
                    best_portfolio = alloc

    symbols_toread = list(set(symbols) | set(['SPY']))

    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = DATAOBJ.get_data(timestamps, symbols_toread, KEYS)
    d_data = dict(zip(KEYS, ldf_data))

    # Copying close price into separate dataframe to find rets
    df_rets = d_data['close'].copy()
    # Filling the data.
    df_rets = df_rets.fillna(method='ffill')
    df_rets = df_rets.fillna(method='bfill')

    df_rets = df_rets.reindex(columns=symbols)

    # Numpy matrix of filled data values
    na_rets = df_rets.values
    # returnize0 works on ndarray and not dataframes.
    returnize0(na_rets)

    # Estimate portfolio returns
    na_portrets = np.sum(na_rets * best_portfolio, axis=1)
    portfolio_total = np.cumprod(na_portrets + 1)

    market_performance = d_data['close']['SPY'].values
    market_performance = market_performance/market_performance[0]

    return (portfolio_total, market_performance, final_stddev, final_daily_ret, final_cum_ret, max_sharpe)
