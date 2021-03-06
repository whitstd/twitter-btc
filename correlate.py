import pandas as pd

btc = pd.read_csv('data/bitcoin_market_price_2017.csv')
btc['date'] = pd.to_datetime(btc['date']).dt.date 

sentiment = pd.DataFrame()

print('Merging sentiment datasets ...')

# merge sentiment data
for i in range(1, 4):
    cur_sentiment = pd.read_csv('data/sentiment{}.csv'.format(i))
    cur_sentiment['date'] = pd.to_datetime(cur_sentiment['timestamp']).dt.date 
    sentiment = sentiment.append(cur_sentiment)    
    
print('Grouping sentiment dataset by day ...')

# get daily mean polarity
day_group = sentiment.groupby('date')

daily = pd.DataFrame(columns = ['polarity_mean', 'perc_positive'], dtype = 'float64')
daily['date'] = sentiment['date'].unique()

for date, group in day_group:
    polarity_mean = group['polarity'].mean()
    perc_positive = group['polarity'].apply(lambda x: 1 if x > 0 else 0).sum() / len(group)
    
    daily.loc[daily.date == date, 'polarity_mean'] = polarity_mean
    daily.loc[daily.date == date, 'perc_positive'] = perc_positive

daily = daily.merge(btc, how = 'inner', on = 'date')

daily['polarity_diff'] = daily['polarity_mean'].diff(1)
daily['polarity_bin'] = daily['polarity_diff'].apply(lambda x: 1 if x >= 0 else 0)
daily['change_bin'] = daily['change'].apply(lambda x: 1 if x > 0 else 0)

# add lags
print('Adding lag features ...')

fields = ['polarity_mean', 'polarity_bin', 'perc_positive']
lags = 1

for field in fields:
    for i in range(1, lags + 1): 
        daily[field + '-{}'.format(i)] = daily[field].shift(i).values

print('Computing correlation matrix ...')
print(daily.corr())
