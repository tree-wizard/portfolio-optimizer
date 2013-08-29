import ashiba   
from ashiba.plot import plt
import datetime as dt
from stock_data import get_NYSE_days, close_prices, portfolio_stats #, standard_devation, avg_daily_returns, sharpe_ratio, cumulative_returns

def calculate__click(dom):

    # Here we grab the equity info from the dom and perform a few conversions
    stock1 = stock2 = stock3 = stock4 = None
    stock1 = dom['stock1']['value']  
    stock2 = dom['stock2']['value']
    stock3 = dom['stock3']['value']
    stock4 = dom['stock4']['value']
    ls_symbols = [stock1, stock2, stock3, stock4]
    symbols = filter(lambda a: len(a) > 0, ls_symbols)

    stock1_ratio = dom['stock1_ratio']['value']
    stock2_ratio = dom['stock2_ratio']['value']
    stock3_ratio = dom['stock3_ratio']['value']
    stock4_ratio = dom['stock4_ratio']['value']
    ratios = [stock1_ratio, stock2_ratio, stock3_ratio, stock4_ratio]
    ls_alloc = [float(i) for i in ratios]
    allocations = filter(lambda a: a > 0, ls_alloc)

    #get the trading days in the time period
    bounds = [dom[x]['value'] if dom[x]['value'] else None
              for x in ['date_start', 'date_end']]     
    if bounds[0] != None:
        start = bounds[0].split('-')
        dt_start = dt.datetime(int(start[0]),int(start[1]), int(start[2]))
    else:
        dt_start = dt.datetime(2006, 1, 1)

    if bounds[1] != None:
        end = bounds[1].split('-')
        dt_end = dt.datetime(int(end[0]), int(end[1]), int(end[2]))
    else:
        dt_end = dt.datetime(2012, 5, 20)
    #timestamps of trading days
    timestamps = get_NYSE_days(dt_start, dt_end)


    #close prices
    normalized_close_prices = close_prices(ls_symbols, timestamps)

    portfolio_total, market_per, final_stddev, final_daily_ret, final_cum_ret, max_sharpe  = portfolio_stats(symbols, allocations, normalized_close_prices, timestamps)

    text = '''Symbols : %s \n\n
              Std. Deviation : %f
              Daily Returns  : %f
              Cum. Returns   : %f
              Sharpe Ratio   : %f  ''' % (symbols, final_stddev, final_daily_ret, final_cum_ret, max_sharpe) 


    dom['my_tabs'].add_tab('[%s]' % ', '.join(map(str, symbols)), text)


    plt.clf()
    plt.plot(timestamps, normalized_close_prices)
    plt.legend(symbols)
    plt.ylabel('Normalized Close')
    plt.xlabel('Date')
    dom['close_prices'].set_image(plt.get_svg(), 'svg') 

    plt.clf()
    plt.plot(timestamps, portfolio_total, label='Portfolio')
    plt.plot(timestamps, market_per, label='SPY')
    plt.legend()
    plt.ylabel('Returns')
    plt.xlabel('Date')
    dom['daily_returns'].set_image(plt.get_svg(), 'svg')

    return dom
