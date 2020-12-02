#!/usr/bin/env python
# coding: utf-8

# In[ ]:

'''
https://github.com/DirkEngfer/PandasTests
Monthly precipitation [mm] summed up in city Schleswig/Germany). programmer: Dirk Engfer, Germany
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
'''

# In[1]:


import os, numpy as np
import pandas as pd
from matplotlib import pyplot as plt
homedir = os.getenv('HOME')

datapath = os.path.join(homedir, 'Dokumente','python-apps','tensorflow', 'eu_air_pollution_data')
datafile = 'wetter_historical_Schleswig.csv'

indatapath = os.path.join(datapath,datafile)

'''
Demonstration of:
  - Working on "lag" records [emulating SAS Lag function] 
  - Data munging without costly iteration (no itertuples() nor iterrows() ) but using .loc attribute
  - Emulating LOCF 

'''

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
skeleton = pd.DataFrame({'year':np.arange(1960, 2019)})
yearly = df.groupby('year')['rain'].sum() # returns Series object
df['yearly_mean'] = yearly.mean() # mean over all years
df = df.merge(yearly, left_on='year', right_on='year', how='inner')
df.rename(columns={'rain_y':'rain'}, inplace=True) 
# Get in full range of years from skeleton:
# skeleton for years enables line plot with disconnected segments
df = df.merge(skeleton, how='right', left_on='year_', right_on='year')
df.rename(columns={'year_y':'year'}, inplace=True)
df.drop(columns='year_x', inplace=True)
df = df.loc[:, ['year','rain']]
df.drop_duplicates(inplace=True)
df.reset_index(inplace=True, drop=True)
df['peak'] = 0
#print(df)

row = -1
previdx = 0
previdx2= 0
checkvar = 'rain'
def process_rows(tup):
	global row, previdx, previdx2
	row +=1
	if row >= 2:
		# remember the previous index:
		previdx = df.loc[tup[0]-1].name
		# remember the second previous index:
		previdx2 = df.loc[tup[0]-2].name
		# get previous rainfall:
		prevrain = np.NaN
		if pd.notna(df.loc[previdx,checkvar]):
			prevrain = df.loc[previdx,checkvar]
		# get second previous rainfall:
		prevrain2 = np.NaN
		if pd.notna(df.loc[previdx2,checkvar]):
		    prevrain2 = df.loc[previdx2,checkvar]
		# get actual precipitation:
		actualrain = df.loc[tup[0], checkvar]
		# process if actual rain + prevrain + prevrain2:
		if pd.notnull(actualrain) and pd.notnull(prevrain) and pd.notnull(prevrain2):
			if (prevrain > actualrain) and (prevrain2 < prevrain):
				#print(actualrain, prevrain, prevrain2)
				df.loc[previdx, 'peak'] = 1
				df.loc[previdx, 'peak_ffill'] = df.loc[previdx, checkvar]
			
[process_rows([x,y]) for x,y in zip(df.index, df.rain)]
df['rain_peaks'] = df.peak_ffill
df.peak_ffill.fillna(method='ffill', inplace=True)
print(df)

fig, ax = plt.subplots(figsize=[20,15])
ax.plot(df['year'], df['peak_ffill'], label='Peak values of rainfall carried forward', color='b')
ax.scatter(df['year'], df.rain_peaks, color='b')

ax.set_xlim(1960, 2018)
ax.tick_params(labelsize=18)

ax.set_title('Yearly precipitation in city Schleswig', fontsize='xx-large')
ax.legend(loc=3, prop={'size': 18})
ax.grid(True)

plt.xlabel('1960 - 2018', fontsize='xx-large')
plt.ylabel('Precipitation in mm', fontsize='xx-large')
fig.autofmt_xdate(rotation=30)
plt.savefig('lineplot_peaks_carried_forward.png', dpi=None, facecolor='w', edgecolor='w',
        orientation='landscape', format='png')



