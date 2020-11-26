#!/usr/bin/env python
# coding: utf-8

# In[ ]:

'''
https://github.com/DirkEngfer/PandasTests
Hourly NO2 measures in Bornhoeved (Schleswig-Holstein/Germany). programmer: Dirk Engfer, Germany
Provided Input data file: NO2_2019_Bornhoeved.csv

------------------------------
Original source of Input Data:
------------------------------
Quelle: Umweltbundesamt, https://www.umweltbundesamt.de/daten/luft/luftdaten/stationen
        (Abruf: 02.10.2020). Alle Uhrzeiten sind in der jeweils zum Messzeitpunkt
        gültigen Zeit (MEZ bzw. MESZ) angegeben.
'''

# In[1]:


import os, numpy as np
import pandas as pd
homedir = os.getenv('HOME')

datapath = os.path.join(homedir, 'Dokumente','python-apps','tensorflow', 'eu_air_pollution_data')
datafile = 'NO2_2019_Bornhoeved.csv'

indatapath = os.path.join(datapath,datafile)


# In[ ]:

'''
Aggregate data as follows:
    Pick the 3 highest measures of each day and calculate the arithmetic mean value of these.
'''

# In[6]:


df = pd.read_csv(indatapath, header=0, sep=',',usecols=[2,7,8,9])
df = df.loc[(df.Stationsname.isin(['Bornhöved', 'Kiel-Bahnhofstr. Verk.']))]
df = df.loc[(df.Messwert.str.contains(pat='-')) == False]
df['Messwert']  = df['Messwert'].astype(np.int)
from datetime import datetime
f = lambda x:datetime.strptime(x[-10:], "%d.%m.%Y")
df['mydate'] = df['Datum'].map(f)

df.sort_values(by=['Stationsname', 'mydate', 'Messwert'], ascending=[True,True, False], inplace=True, axis=0)
dailymean = df.groupby(['Stationsname', 'mydate'], sort=False, as_index=False).nth([0,1,2]).groupby(['Stationsname', 'mydate'], sort=False, as_index=False).mean()
dailymean['day_count'] = dailymean.groupby('Stationsname', sort=False, as_index=False).cumcount().add(1)
dailymean['Jahresgrenzwert'] = 40
Ki = dailymean.loc[(dailymean.Stationsname.isin(['Kiel-Bahnhofstr. Verk.']))]
dailymean = dailymean.loc[(dailymean.Stationsname.isin(['Bornhöved']))]
print(dailymean)

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=[20,15])

ax.plot(dailymean['day_count'], dailymean['Jahresgrenzwert'], label='Jahresgrenzwert')
ax.plot(dailymean['day_count'], dailymean['Messwert'], label='Bornhöved')
ax.plot(Ki['day_count'], Ki['Messwert'], label='Kiel')
ax.set_title('Exposure to outdoor NO2 on the country side vs Kiel city (urban) in Schleswig-Holstein\nCalculated mean value of the 3 highest measures per day in 2019', fontsize='xx-large')
ax.set_xlim(0, 365)
ax.set_ylim(0, 130)
ax.set_xticks(range(30,365,30))
ax.legend()
plt.xlabel('Day count from JAN 01 to DEC 31', fontsize='xx-large')
plt.ylabel('NO2 [microgram/m3]', fontsize='xx-large')
plt.savefig('NO2-SH_1.png', dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait', papertype=None, format='png')


# In[3]:


kiel_d = pd.DataFrame(Ki.Messwert)
kiel_d.rename(columns={'Messwert':'kiel'}, inplace=True)
kiel_d.reset_index(drop=True, inplace=True)
born_d = dailymean.Messwert
born_d.reset_index(drop=True, inplace=True)
ki_bo = pd.concat([kiel_d, born_d], axis=1, copy=True)
ki_bo.rename(columns={'Messwert':'bornh'}, inplace=True)

print(ki_bo)


# In[7]:


fig, ax = plt.subplots(figsize=[20,15])
# the histogram of the data
n, bins, patches = ax.hist([ki_bo.kiel, ki_bo.bornh], 20, density=True, label=['urban', 'country side'], histtype='stepfilled', alpha=0.75)

#ax.plot(n, bins)
ax.set_xlabel('Bins of NO2 [ug/m3]', fontsize=24)
ax.set_ylabel('Frequency density', fontsize=24)
ax.set_title(r'Histogram of outdoor NO2 urban vs country side in year 2019, Schleswig-Holstein/Germany', fontsize=24)
ax.legend(prop={'size': 18})
ax.xaxis.set_tick_params(labelsize=24)
ax.yaxis.set_tick_params(labelsize=24)
# Tweak spacing to prevent clipping of ylabel
fig.tight_layout()
plt.savefig('NO2-SH_2.png', dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait', format='png')


# In[8]:


df.sort_values(by=['Stationsname', 'mydate', 'Uhrzeit'], ascending=[True,True, True], inplace=True, axis=0)
df2 = df.copy()
df2.Uhrzeit.replace(regex=['16:00'], value='99', inplace=True)
print(df2)
def some_func(row):
    pass #print(row[2])

#df['result_col'] = [some_func(row[0]) for row in zip(df[['col_1', 'col_2',... ,'col_n']].to_numpy())]





