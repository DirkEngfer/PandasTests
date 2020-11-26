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
- Translate the SAS SET statement and friends into Pandas
- calculate the arithmetic mean of the 3 highest measures per station/day
- devide data into Kiel and Bornhöved (urban vs country)
'''

# In[2]:


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
Bo = dailymean.loc[(dailymean.Stationsname.isin(['Bornhöved']))]
Bo2 = Bo.copy()
Bo2['Bornh'] = 'yes'


# In[ ]:

'''
Set together 2 dataframes,
  (1) perform Append
  (2) perform Concatenation
  (3) Compare methods 1 and 2 for differences in the resulting dataframe
      i.e. Merge both results ON all columns and look at Merge-indicator variable = 'both'
'''

# In[3]:


_appended = Ki.append(Bo2, ignore_index=True, verify_integrity=False, sort=False)
_concatenated = pd.concat([Ki, Bo2], join='outer', axis=0)
compared = _appended.merge(_concatenated, on=['Stationsname', 'mydate', 'Messwert', 'day_count', 'Jahresgrenzwert', 'Bornh'], how='inner', indicator=True)
print(compared.loc[compared._merge != 'both', :])

# Some more tests on Merge facets:
d1 = pd.DataFrame({'x':['x1', 'x2', 'x2', 'x3'], 'y':['y1', 'y2a','y2b', 'y3'], 'z': ['z1', 'z2a','z2b', 'z3']})
#d1
d2 = pd.DataFrame({'x':['x2', 'x3', 'x40', 'x50'], 'y':['y10', 'y20','y20', 'y30'], 'z': ['z10', 'z20','z20', 'z30']})
d3 = d1.merge(d2, on='x', how='outer')
d4 = d1.merge(d2, on='x', how='inner')
d5 = _concatenated.copy()


# In[35]:


def mysum( x,y):
    return x + y


dfw = pd.DataFrame({'A': [1, 2,3], 'B': [10, 20,30]})
# arg self: frame passed in, y and z: from args=, m: keyword arg:
#dfw2 = dfw.apply(mysum, args=(1, 2), m=10)
#print(dfw2)
#print(dfw.apply(lambda x: x+100))
# Check out list-comprehension based approach of modifying dataframe:
dfw['row_sum'] = [mysum(x,y) for x, y in zip(dfw.A, dfw.B)]
#print(dfw)

df.sort_values(by=['Stationsname', 'mydate', 'Uhrzeit'], ascending=[True,True, True], inplace=True, axis=0)

# Modify dataframe using list comps:
# ----------------------------------
import timeit
dfx = df.copy()
dfx.Uhrzeit.replace(regex=["'"], value='', inplace=True)
dfx.Uhrzeit.replace(regex=["24:00"], value='00:00', inplace=True)
dfx.Stationsname.replace(regex=["Kiel-Bahnhofstr. Verk."], value='Kiel', inplace=True)

# Emulate SAS if-else if-else construct on multiple columns:
def set_timefor(row):
    if row[0] == "16:00" and row[1] != '31.12.2019' and row[2] != 'Kiel':
        return "coffee"
    if row[0] == "16:00" and row[2] == 'Kiel':
        return "tea"
    elif row[1] == '31.12.2019':
        return "New year's eve"
    elif row[0] in ["18:00", "19:00"]:
        return "dinner"
    else:
        return "other"
print('Check out speed when performing a list comp:')
#print(dfx)
'''
Next, check out a few datetime operations.
subset data using the apply method
Emulate if-else if-else construct
Emulate SAS RETAIN statement on groups
Do speed test on method Apply to compare with list comp from above
'''

# In[34]:


df2 = df.copy()
df2.Uhrzeit.replace(regex=["'"], value='', inplace=True)
df2.Uhrzeit.replace(regex=["24:00"], value='00:00', inplace=True)
df2.Stationsname.replace(regex=["Kiel-Bahnhofstr. Verk."], value='Kiel', inplace=True)
df2['datumuhrzeit'] = df2['Datum'] + ' ' + df2['Uhrzeit']
# Example for map method and datetime operations:
f = lambda x:datetime.strptime(x[-10:], "%d.%m.%Y")
df['mydate'] = df['Datum'].map(f)
# datetime in pandas notation:
df2['mydt']   = pd.to_datetime(df2['datumuhrzeit'], format='%d.%m.%Y %H:%M')
# Subset data:
subset_df2 = df2.loc[df2.apply(lambda x: x['Uhrzeit'] in ['16:00', '17:00'] and x.Messwert < 20, axis=1)]

# Emulate SAS if-else if-else construct on multiple columns:
def set_timefor(row):
    if row["Uhrzeit"] == "16:00" and row.Datum != '31.12.2019' and row['Stationsname'] != 'Kiel':
        return "coffee"
    if row["Uhrzeit"] == "16:00" and row['Stationsname'] == 'Kiel':
        return "tea"
    elif row.Datum == '31.12.2019':
        return "New year's eve"
    elif row["Uhrzeit"] in ["18:00", "19:00"]:
        return "dinner"
    else:
        return "other"

df2 = df2.assign(time_for=df2.apply(set_timefor, axis=1))
# Doing a speed test on method ".apply":
print('Apply is ca. 50 times slower than list comp from above:')
get_ipython().run_line_magic('timeit', "df2['speedtest'] = df2.apply(set_timefor, axis=1)")

# Emulate SAS RETAIN statement on groups:
# Task: retain column time_for from the first measure per station (use of method apply), first build up groups
st_gr = df2.groupby(df2['Stationsname'], as_index=False)
first = st_gr.first()
first['isfirst'] = 1
first.drop(columns=['Messwert', 'mydate', 
       'datumuhrzeit', 'mydt', 'time_for'], inplace=True)
df2 = df2.merge(first, how='left', on=['Stationsname', 'Datum', 'Uhrzeit'])

retained_row = pd.Series([], dtype=np.str)
def retainer(row):
    global retained_row
    return_value = np.NaN
    if row.isfirst == 1:
        return_value = row.time_for
        retained_row = row.copy()
        
    else:
        return_value = retained_row['time_for']
    return return_value

df2 = df2.assign(initial_event=df2.apply(retainer,  axis=1))
#print(df2.info())

print(df2.head())
print(df2.tail())


