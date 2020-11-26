#!/usr/bin/env python
# coding: utf-8

# In[ ]:


https://github.com/DirkEngfer/PandasTests
Monthly precipitation [mm] summed up in (Schleswig-Holstein/Germany). programmer: Dirk Engfer, Germany
Provided Input data file: wetter_historical_Schleswig.csv

------------------------------
Original source of Input Data:
------------------------------

Datenquelle:
https://www.dwd.de/DE/leistungen/klimadatendeutschland/klarchivtagmonat.html?nn=510076
    
Deutscher Wetterdienst
Zentraler Vertrieb Klima und Umwelt
Frankfurter Straße 135
Postfach 100465
63004 Offenbach

Copyright notice by data provider:
https://www.dwd.de/DE/service/copyright/copyright_node.html


# In[1]:


import os, numpy as np
import pandas as pd
from matplotlib import pyplot as plt
homedir = os.getenv('HOME')

datapath = os.path.join(homedir, 'Dokumente','python-apps','tensorflow', 'eu_air_pollution_data')
datafile = 'wetter_historical_Schleswig.csv'

indatapath = os.path.join(datapath,datafile)


# In[12]:


df = pd.read_csv(indatapath, header=0, sep=';',usecols=[1,14])
df['start_dt'] = pd.to_datetime(df.MESS_DATUM_BEGINN, format='%Y%m%d')
df['year'] = df['start_dt'].dt.year
df.sort_values(by=['year'], ascending=[True], inplace=True, axis=0)
df.rename(columns={"MO_RR": "rain"}, inplace=True) # rain includes all kind of precipitation
df = df.loc[(df.start_dt >= pd.to_datetime('19600101', format='%Y%m%d'))] # from year 1960
df = df.loc[(df.rain >= 0)] # discard negative values

# check all months were reported:
#print(df.groupby(['year'], sort=False, as_index=False).year.count())
# Exclude incomplete years i.e. the ones with less than 12 obs:
g = df.groupby('year', sort=False)
valid = pd.DataFrame(g['rain'].count())
valid.rename(columns={'rain':'months_with_measures'}, inplace=True)
valid = valid.loc[(valid['months_with_measures'] == 12)]
valid['year_'] = valid.index
df = df.merge(valid, left_on='year', right_on='year_', how='inner', sort=False)
# Build skeleton to complete all years in time range:
skeleton = pd.DataFrame({'year':np.arange(1960, 2018+4)}) # up to 2021 
yearly = df.groupby('year')['rain'].sum() # returns Series object
df['yearly_mean'] = yearly.mean() # mean over all years
df = df.merge(yearly, left_on='year', right_on='year', how='inner')
df.rename(columns={'rain_y':'rain_sum'}, inplace=True)
# Get in full range of years from skeleton:
# skeleton for years enables line plot with disconnected segments
df = df.merge(skeleton, how='right')


# test: subset df for demonstration purposes:
# initialize column: period
df = df[['rain_sum']]
df = df.iloc[650:656]
df.loc[655:,'rain_sum'] = 100
df.loc[650,'rain_sum'] = np.NaN
df['period'] = 0

''' START building up time series with values=NOT-NaN vs NaN, ie group missings:
                 *** Define functions ***
'''
def check_isnan(checkvar):
    return len(df.loc[df[checkvar].isna()])

def getIndexMin():
    return df.index[0]

def process_rows(tup):
    global period
    # check each previous index for NaN:
    first_idx = getIndexMin()
    if df.loc[tup[0]].name == first_idx:
        previdx = np.NaN
    else:
        # get the previous index:
        previdx = df.loc[tup[0]-1].name
    # get previous rainfall:
    prevrain = np.NaN
    if tup[0] > first_idx:
        if pd.notna(df.loc[previdx,'rain_sum']):
            prevrain = df.loc[previdx,'rain_sum']
    # get actual precipitation:
    actualrain = df.loc[tup[0], 'rain_sum']
    # process rain == NaN:
    if pd.isna(actualrain):
        # is first NaN vs is NaN in the middle:
        if pd.isnull(prevrain):
            pass#print('NO actualrain + NO prevrain', tup[0])
        if pd.notnull(prevrain):
            period = period + 1
            pass#print('NO actualrain + prevrain', tup[0])
    # process if actual rain:
    if pd.notnull(actualrain):
        if pd.isnull(prevrain):
            period = period + 1
            pass#print('actualrain + NO prev rain', tup[0])
        else:
            pass#print('actualrain + prev rain', tup[0])
    df.loc[tup[0], 'period'] = period
period = 0
first_idx = getIndexMin()
checkvar = 'rain_sum'
if check_isnan(checkvar) > 0:
    [process_rows([x,y]) for x,y in zip(df.index, df.rain_sum)]
print(df)
'''
    rain_sum  period
650       NaN       0
651     756.7       1
652     756.7       1
653       NaN       2
654       NaN       2
655     100.0       3
'''


