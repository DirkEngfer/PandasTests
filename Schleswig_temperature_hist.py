#!/usr/bin/env python
# coding: utf-8

# In[ ]:

'''
https://github.com/DirkEngfer/PandasTests
Temperature trend from historical measures in city Schleswig from 1947. programmer: Dirk Engfer, Germany
Provided Input data file: Schleswig_Klima_Tag_hist.txt

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
'''


import os, numpy as np
import pandas as pd
from matplotlib import pyplot as plt
homedir = os.getenv('HOME')

datapath = os.path.join(homedir, 'Dokumente','python-apps','tensorflow', 'eu_air_pollution_data')
datafile = 'Schleswig_Klima_Tag_hist.txt'

indatapath = os.path.join(datapath,datafile)

df = pd.read_csv(indatapath, header=0, sep=';',usecols=[1,13], names=['Datum', 'daytempmean'])
df['dt'] = pd.to_datetime(df.Datum, format='%Y%m%d')
df.drop(columns='Datum', inplace=True)
df['year'] = df['dt'].dt.year
df.sort_values(by=['dt'], ascending=[True], inplace=True, axis=0)
# Deal with missings:
mis = df.loc[(df.daytempmean == -999)]
#print(len(mis)) No missings in the data
df2 = pd.DataFrame()
df2['av_temp_year'] = df.groupby(['year'], sort=False, as_index=True).daytempmean.mean()
print(df2)


fig, ax = plt.subplots(figsize=[10,7.5])
ax.scatter(df2.index, df2.av_temp_year, color='b')

ax.set_xlim(1947, 2018)
ax.tick_params(labelsize=18)

ax.set_title('Mean annual temperature (°celsius) in city Schleswig', fontsize='xx-large')
ax.legend(loc=3, prop={'size': 18})
ax.grid(True)

plt.xlabel('1947 - 2018', fontsize='xx-large')
plt.ylabel('Temp. [°Celsius]', fontsize='xx-large')
fig.autofmt_xdate(rotation=30)
plt.savefig('Schleswig_temperature_historical.png', dpi=None, facecolor='w', edgecolor='w',
        orientation='landscape', format='png')



# do linear regression:
import statsmodels.api as sm
x = np.arange(1, len(df2.index)+1)
y = df2.av_temp_year # response
X = x # predictor
X = sm.add_constant(X)  # Adds a constant term to the predictor
model = sm.OLS(y, X).fit()
df2['predicted'] = model.predict(X)

fig, ax = plt.subplots(figsize=[10,7.5])
ax.plot(df2.index, df2['predicted'], label='Trend (linear regression)', color='red')
ax.scatter(df2.index, df2.av_temp_year, color='grey')

ax.set_xlim(1947, 2018)
ax.tick_params(labelsize=18)

ax.set_title('Mean annual temperature in city Schleswig', fontsize='xx-large')
ax.legend(loc=3, prop={'size': 18})
ax.grid(True)

plt.xlabel('1947 - 2018', fontsize='xx-large')
plt.ylabel('Temperature (°Celsius)', fontsize='xx-large')
fig.autofmt_xdate(rotation=30)
plt.savefig('Schleswig_temperature_historical2.png', dpi=None, facecolor='w', edgecolor='w',
        orientation='landscape', format='png')


