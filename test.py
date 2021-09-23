import pandas as pd 
from alpha_vantage.timeseries import TimeSeries
import time
import datetime as dt


api_key='3N5AMZY0IQSLSX68'



ts =TimeSeries(key=api_key,output_format='pandas')
data,meta_data=ts.get_intraday(symbol='TSLA', interval='1min', outputsize='full')
#print(data)


close_data=data['4. close']


print(close_data[-1])


import pandas_datareader as web

crypto='GOOG'

start=dt.datetime(2014,1,1)
end=dt.datetime.now()

data = web.DataReader(f"{crypto}-{'USD'}",'yahoo-actions',start,end)['Close'][-1]


print(data)