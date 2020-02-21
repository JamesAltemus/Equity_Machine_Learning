# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 14:56:10 2020

@author: James Altemus
"""
import os
import pandas as pd

from pandas_datareader.data import DataReader
from datetime import datetime
from numpy import nan

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
            
            prices['yr_ret'] = yr_ret
            prices['outperformance'] = ((prices['yr_ret'] > idx.loc[prices.index]).astype(int)
                                        -(prices['yr_ret'] < -idx.loc[prices.index]).astype(int))
            
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


def download_index(index = '^GSPC', start = datetime(1993, 1, 1), end = datetime(2019, 7, 9)):
    prices = DataReader(index,  'yahoo', start = datetime(1993, 1, 1), end = datetime(2019, 7, 9))
    yr_ret = list(prices['Close'].pct_change(252).dropna())
    length = len(prices)
    for i in range(length-len(yr_ret)):
        yr_ret.append(nan)
    prices['yr_ret'] = yr_ret
    return prices['yr_ret']
    

tickers = pd.read_csv('company_info.csv')
tickers = list(tickers['ticker'].dropna())
os.chdir('Outperformance Directory Path')

idx = download_index()
error = get_outperformance(tickers, idx)
print(error)