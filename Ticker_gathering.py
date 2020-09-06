import pandas as pd
import numpy as np
from datetime import datetime
import bs4 as bs
import pickle
import requests
from yahoo_earnings_calendar import YahooEarningsCalendar


def sp500_constituents():
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    companies = []
    sectors = []
    subindustries = []
    next_earnings = []
    
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        tickers.append(ticker.rstrip())
        company = row.findAll('td')[1].text
        companies.append(company.rstrip())
        sector = row.findAll('td')[3].text
        sectors.append(sector.rstrip())
        subindustry = row.findAll('td')[4].text
        subindustries.append(subindustry.rstrip())
        
    with open("sp500tickers.pickle","wb") as f:
        pickle.dump(tickers,f)
    
    yec = YahooEarningsCalendar()
    for i in range(len(tickers)):
        
        try:
            next_earnings.append(datetime.fromtimestamp(yec.get_next_earnings_date(tickers[i])))
        except:
            print("Problem with: {t}".format(t=tickers[i]))
            next_earnings.append(0)
    
    return tickers, companies, sectors, subindustries, next_earnings

tickers, companies, sectors, subindustries, next_earnings = sp500_constituents()

ticker_data = {'tickers': tickers, 'companies': companies, 'sectors': sectors, 'subindustries': subindustries, 'next earnings': next_earnings}
ticker_lookup = pd.DataFrame(data=ticker_data)
ticker_lookup = ticker_lookup.set_index('tickers')


ticker_lookup.to_excel('ticker_lookup.xlsx')