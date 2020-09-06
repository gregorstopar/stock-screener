# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 12:24:04 2020

@author: grego
"""

from pandas_datareader import data
from pandas_datareader._utils import RemoteDataError
import pandas as pd
import numpy as np
from datetime import datetime
import bs4 as bs
import pickle
import requests




START_DATE = '2015-01-01'
END_DATE = str(datetime.now().strftime('%Y-%m-%d'))

EMPTY = 1

def adjust_data(stock_data):
    
    stock_data['Adj Open'] = stock_data['Open'] * (stock_data['Adj Close'] / stock_data['Close'])
    stock_data['Adj High'] = stock_data['High'] * (stock_data['Adj Close'] / stock_data['Close'])
    stock_data['Adj Low'] = stock_data['Low'] * (stock_data['Adj Close'] / stock_data['Close'])
    stock_data.drop(['Open', 'High', 'Low', 'Close'], axis=1, inplace=True)
    return stock_data

def calculate_atr(stock_data):
    
    stock_data['x'] = stock_data['Adj High'] - stock_data['Adj Low']
    stock_data['Previous Close'] = stock_data['Adj Close'].shift(1)
    stock_data['y'] = abs(stock_data['Adj High'] - stock_data['Previous Close'])
    stock_data['z'] = abs(stock_data['Adj Low'] - stock_data['Previous Close'])
    
    stock_data['TR'] = stock_data[["x","y","z"]].max(axis=1)
    
    stock_data.drop(['x', 'y', 'z', 'Previous Close'], axis=1, inplace=True)
    
    stock_data['ATR'] = stock_data['TR'].ewm(span=21).mean()
    stock_data['ATR+1'] = stock_data['ema21'] + stock_data['ATR']
    stock_data['ATR+2'] = stock_data['ema21'] + 2*stock_data['ATR']
    stock_data['ATR+3'] = stock_data['ema21'] + 3*stock_data['ATR']
    stock_data['ATR-1'] = stock_data['ema21'] - stock_data['ATR']
    stock_data['ATR-2'] = stock_data['ema21'] - 2*stock_data['ATR']
    stock_data['ATR-3'] = stock_data['ema21'] - 3*stock_data['ATR']

    return stock_data


def get_indicators(stock_data):
    
    stock_data['sma50'] = stock_data['Adj Close'].rolling(window=50).mean()
    stock_data['sma200'] = stock_data['Adj Close'].rolling(window=200).mean()
    stock_data['sma100'] = stock_data['Adj Close'].rolling(window=100).mean()
    stock_data['ema8'] = stock_data['Adj Close'].ewm(span=8).mean()
    stock_data['ema21'] = stock_data['Adj Close'].ewm(span=21).mean()
    stock_data['ema34'] = stock_data['Adj Close'].ewm(span=34).mean()
    stock_data['ema55'] = stock_data['Adj Close'].ewm(span=55).mean()
    stock_data['ema89'] = stock_data['Adj Close'].ewm(span=89).mean()
    
    stock_data = calculate_atr(stock_data)
    
    return stock_data
        

def clean_data(stock_data):
    weekdays = pd.date_range(START_DATE, end=END_DATE)
    clean_data = stock_data.reindex(weekdays)
    return clean_data.fillna(method='ffill')


def evaluate(stock_data):
    global EMPTY
    EMPTY = 0
    
    for x in range(N): # Check first for uptrend
        if stock_data['ema8'][x-N] > stock_data['ema21'][x-N] > stock_data['ema34'][x-N] > stock_data['ema55'][x-N] > stock_data['ema89'][x-N]:
            if x == (N-1):
                if stock_data['Adj Close'][-1] < stock_data['ATR+1'][-1]:
                    ticker_lookup['included'][stock_data['ticker'][1]]="UPTREND"
                    return stock_data
                else:
                    EMPTY = 1
                    return []
            else:
                pass
        elif x > 0:
            EMPTY = 1
            return []
        else: # Check for downtrend
            for x in range(N):
                if stock_data['ema8'][x-N] < stock_data['ema21'][x-N] < stock_data['ema34'][x-N] < stock_data['ema55'][x-N] < stock_data['ema89'][x-N]:
                    if x == (N-1):
                        if stock_data['Adj Close'][-1] > stock_data['ATR-1'][-1]:
                            ticker_lookup['included'][stock_data['ticker'][1]]="DOWNTREND"
                            return stock_data
                        else:
                            EMPTY = 1
                            return []
                    else:
                        pass
                else:
                    EMPTY = 1
                    return []

    return stock_data    
    

def get_data(ticker):
    try:
        stock_data = data.DataReader(ticker,'yahoo',START_DATE,END_DATE)
        stock_data['ticker'] = ticker
        
        stock_data = clean_data(stock_data) # replace NaNs
        
        stock_data = adjust_data(stock_data) # Adjust High, Low and Open
        
        stock_data = get_indicators(stock_data) # SMAs, EMAs, ATRs
        
        
        
        stock_data = evaluate(stock_data) 
        
        return stock_data
        #stock_data.to_excel('stocks.xlsx')
        
    
    except RemoteDataError:
        print('No data found for {t}'.format(t=ticker))
        
    except KeyError:
        print('KeyError for ticker {t}'.format(t=ticker))
        
    except:
        print('Other error for ticker {t}'.format(t=ticker))

ticker_lookup = pd.read_excel('ticker_lookup.xlsx', sheet_name=0)
tickers = ticker_lookup['tickers'].tolist()
ticker_lookup = ticker_lookup.set_index('tickers')
ticker_lookup['included'] = "NO"

print(ticker_lookup)

     
stock_data = []

N = 30 #set N days for lookback evaluation period

number_of_candidates = 0

for i in range(len(tickers)):
           
    new_data = get_data(tickers[i])
    
    if EMPTY == 0:
        if number_of_candidates == 0:
            stock_data = new_data
            number_of_candidates += 1
        else:
            stock_data = stock_data.append(new_data)
    else: 
        pass
        

stock_data.to_excel('stocks.xlsx')
ticker_lookup.to_excel('ticker_lookup.xlsx')


    