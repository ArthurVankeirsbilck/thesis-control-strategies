import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('pv.csv', delimiter=',', skiprows=3)
df.drop(['_start', 'result', 'table', 'uuid', 'unit', 'location', 'Unnamed: 0', '_stop', 'device', '_measurement', '_field'], axis=1, inplace=True)
print(df)

df.info(verbose=True)
# print(df)
df['_value'] = df['_value'].apply(lambda x : x if x > 0 else 0)
plt.plot(df['_value'])
plt.show()
print(df.head())
print(df.tail())

df.to_csv('pvhenkmonth.csv', encoding='utf-8')