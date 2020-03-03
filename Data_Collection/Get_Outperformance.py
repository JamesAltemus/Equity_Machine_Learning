# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 14:56:10 2020

@author: James Altemus
"""
import os
import pandas as pd

from pandas_datareader.data import DataReader
from datetime import datetime
from numpy import nan, abs

def get_outperformance(ticker_list, idx, start = datetime(1993, 1, 1), end = datetime(2019, 7, 9)):
    errors = []
    complete = len(ticker_list)
    done = 0
    for ticker in ticker_list:
        try:
            prices = DataReader(ticker,  'yahoo', start, end)
            yr_ret = list(prices['Close'].pct_change(252).dropna())
            
            length = len(prices)
            for i in range(length-len(yr_ret)):
                yr_ret.append(nan)
            
            tmp_idx = idx.loc[prices.index]
            prices['yr_ret'] = yr_ret
            prices['outperformance'] = ((prices['yr_ret'] > tmp_idx).astype(int)
                                        -(prices['yr_ret'] < -tmp_idx).astype(int))
            prices['magnitude'] = abs(prices['yr-ret']) - abs(tmp_idx)
            st = str(min(prices.index))[:-9]
            en = str(max(prices.index))[:-9]
            file = ticker + '_' + st + '_' + en + '.csv'
            prices.to_csv(file)
        except:
            errors.append(ticker)
        done+=1
        print('\r' + '|' + ((u'\u2588')*(int((done+1)/complete*100))).ljust(99) + '| {0:.2f}%'.format(
                min((done+1)/complete*100, 100)), end='')
    return errors


def download_index(index = '^GSPC', margin = 0.06, start = datetime(1993, 1, 1), end = datetime(2020, 12, 31)):
    '''
    Download the treasury data from https://fred.stlouisfed.org/series/DGS1
    Reformat the first column to be yyyy-mm-dd before running
    '''
    prices = DataReader(index,  'yahoo', start, end)
    yr_ret = prices['Close'].pct_change(252).dropna()
    yr_ret.index = yr_ret.index.astype(str)
    yr_treasury = pd.read_csv('DGS1.csv', index_col = 0)
    yr_treasury = yr_treasury['DGS1'][yr_treasury['DGS1'] != '.'].astype(float)/100+margin
    neg_ret = yr_ret[yr_ret < 0]
    yr_ret.loc[neg_ret.index] = neg_ret - yr_treasury.loc[neg_ret.index]
    yr_ret = list(yr_ret)
    length = len(prices)
    for i in range(length-len(yr_ret)):
        yr_ret.append(nan)
    prices['yr_ret'] = yr_ret
    return prices['yr_ret']


tickers = pd.read_csv('company_info.csv')
tickers = list(tickers['ticker'].dropna())
idx = download_index()

if not os.path.exists('Price_History'):
    os.mkdir('Price_History')
os.chdir('Price_History')
error = get_outperformance(tickers, idx)
print(error)
