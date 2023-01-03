# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 10:21:13 2023

@author: ivan
"""
import datetime
import requests
import pandas as pd
import numpy as np
from pandas_datareader import data
# 需要用此套建載入yahoo的API，否則無法取得資訊
import yfinance as yf
yf.pdr_override()

#--- 取得歷年平均每股盈餘EPS
head = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}

list_req = requests.get('https://stock.wespai.com/p/7733', headers=head)
tables = pd.read_html(
    list_req.content, 
    attrs = {"class":"display"},
    encoding = 'utf-8'
    )[0]
tables['代號'] = tables['代號'].astype('str')


#--- 取得最近的股價
# 設定股號代碼，先試試看上市
all_stock = tables['代號'] + '.TW'
all_stock = all_stock.tolist()
# 先設定要爬的時間
start = datetime.datetime.now() - datetime.timedelta(days=3) 
end = datetime.datetime.now()
# 取得全台灣所有的股票，每天的交易資訊
df_stock = data.get_data_yahoo(all_stock, start, end)

# 只抓今天的價格
todayPrice = pd.DataFrame(df_stock['Close'].iloc[-1])
todayPrice.columns = ['最近價格']
# 挑初沒抓到股價的，用上櫃在抓一次
todayPrice['最近價格'] = todayPrice['最近價格'].fillna(-1)

todayPrice['種類'] = np.where(todayPrice['最近價格'] >= 0, 'TW', 'TWO')
todayPrice['代號'] = todayPrice.index
todayPrice['代號'] = todayPrice['代號'].str.replace('.TW','')
todayPrice['代號'] = todayPrice['代號'] + '.' + todayPrice['種類']
# 在抓一次
all_stock = todayPrice['代號'].tolist()
# 取得全台灣所有的股票，每天的交易資訊
df_stock = data.get_data_yahoo(all_stock, start, end)
# 只抓今天的價格
todayPrice = pd.DataFrame(df_stock['Close'].iloc[-1])
todayPrice.columns = ['最近價格']
todayPrice['代號'] = todayPrice.index
todayPrice['代號'] = todayPrice['代號'].str.replace('.TWO','')
todayPrice['代號'] = todayPrice['代號'].str.replace('.TW','')


# 合併資料
tables = pd.merge( tables , todayPrice,
                  how = 'left',
                   on = '代號'
                  )


# 還是沒抓到股價的就沒辦法了，排除掉
tables['最近價格'] = tables['最近價格'].fillna(-1)
tables = tables[tables['最近價格'] >= 0]

tables['選股'] = np.where(tables['最近價格']  < tables['5年平均EPS(元)'] * 10, 1, 0)
tables[tables['選股']==1]

