#!/usr/bin/env python
# coding: utf-8

# In[12]:


import pandas as pd
import numpy as np
from datetime import datetime
import dateutil.relativedelta
import seaborn as sns
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')


# In[13]:


sales = pd.read_csv('sales_anonymized.csv').drop(columns=['Unnamed: 0'])
sales.date = pd.to_datetime(sales.date)
sales


# In[14]:


sales.sum() # check against Total at bottom of 'sales_by_customer_detail.xlsx' — should be the same number


# In[15]:


# build a dataframe containing sales data for the past num_months (this year)
num_months = 3
# set forecsat_day to the date immediately following the most recent date in sales
forecast_day = pd.to_datetime(sales.iloc[len(sales.index) - 1].date) + pd.Timedelta(days=1)
print(forecast_day)
#
months = pd.DataFrame(columns=['state'])
for i in range(1, num_months + 1):
    month_ago = forecast_day - dateutil.relativedelta.relativedelta(months=i)
    # use mask to isolate sales between month starting i months ago and ending i - 1 months ago
    mask = (sales.date >= month_ago) & (sales.date < forecast_day - dateutil.relativedelta.relativedelta(months=i-1))
    # group sales by state and rename column appropriately 
    month_sales = sales.loc[mask].groupby(['state']).sum()
    month_sales = month_sales.rename(columns={'sales': str(i) + ' months ago'})
    # add the column for this month to the months DataFrame
    months = months.merge(month_sales, how='outer', on='state')

# after exiting this loop, we now have a DataFrame with monthly sales for the past [num_months] months
this_year_months = months
this_year_months.head()


# In[16]:


this_year_months.sum()


# In[17]:


# build a dataframe containing sales data for the past num_months, minus one year
# very similar process to building this_year_months (see above)
forecast_day = forecast_day - pd.Timedelta(days=365)
print(forecast_day)
months = pd.DataFrame(columns=['state'])
for i in range(1, num_months + 1):
    month_ago = forecast_day - dateutil.relativedelta.relativedelta(months=i)
    mask = (sales.date >= month_ago) & (sales.date < forecast_day - dateutil.relativedelta.relativedelta(months=i-1))
    month_sales = sales.loc[mask].groupby(['state']).sum()
    month_sales = month_sales.rename(columns={'sales': 'one year and ' + str(i) + ' months ago'})
    months = months.merge(month_sales, how='outer', on='state')
    
last_year_months = months
last_year_months


# In[18]:


last_year_months.sum()


# In[19]:


YOY_raw = this_year_months.merge(last_year_months, on='state', how='outer')
YOY_raw = YOY_raw.replace(0, np.NaN)
YOY = pd.DataFrame()
YOY_raw


# In[20]:


# find projected sales increase (as ratio)

for index, row in YOY_raw.iterrows():
    # populate array of ratios
    months_ratios = []
    for i in range(1, num_months + 1):
        month_ratio = row[str(i) + ' months ago'] / row['one year and ' + str(i) + ' months ago']
        # if any ratio is NaN (i.e. on of the months didn't have any sales), then default the avg_sales_increase to 1
        if (np.isnan(month_ratio)):
            months_ratios = [1]
            break
        months_ratios.append(month_ratio)
            
    avg_sales_increase = np.mean(months_ratios)
    
    YOY_row = {'state': row.state}
    for i, ratio in enumerate(months_ratios):
        YOY_row['month ' + str(i + 1)] = ratio
    YOY_row['projected sales increase'] = avg_sales_increase
    YOY = YOY.append(YOY_row, ignore_index=True)
    
YOY = YOY.fillna({'projected sales increase': 1})
print(YOY.to_string())


# In[21]:


# TODO: drop observations if there aren't at least 2 not np.isnan() values 


# In[22]:


forecast_day = pd.to_datetime(sales.iloc[len(sales.index) - 1].date) + pd.Timedelta(days=1)
# loop over the below for months_to_project
forecast = pd.DataFrame(columns=['state'])
forecast.state = sales.state.drop_duplicates()

for i in range (0, num_months):
    year_ago_BOM = forecast_day - dateutil.relativedelta.relativedelta(months=12 - i)
    year_ago_EOM = forecast_day - dateutil.relativedelta.relativedelta(months=11 - i)
    mask = (sales.date >= year_ago_BOM) & (sales.date < year_ago_EOM)
    year_ago_sales = sales.loc[mask].groupby(['state']).sum()

    month_forecast = year_ago_sales.merge(YOY, how='outer', on='state')
    forecast_column = []
    for index, row in month_forecast.iterrows():
        state_forecast = row['sales'] * row['projected sales increase']
        forecast_column.append(state_forecast)
    month_forecast['projected sales for ' + 
                                            str(forecast_day + dateutil.relativedelta.relativedelta(months=i)).split(' ')[0]] = pd.Series(forecast_column, index=month_forecast.index)
    month_forecast = month_forecast.rename(columns={'sales':'sales in ' +
                                                    str(year_ago_BOM).split(' ')[0]})
    forecast = forecast.merge(month_forecast, on='state', how='outer')

# end loop
# drop all columns with 'month' or 'projected sales increase' in their name, also drop duplicates of 'projected sales increase' column
forecast = forecast.drop(columns = list(forecast.filter(regex='month')))
forecast = forecast.drop(columns = list(forecast.filter(regex='projected sales increase')))
forecast = forecast.append(forecast.sum(numeric_only=True), ignore_index=True)
# NOTE: .shape[0] returns the row count, whereas .shape[1] returns the column count, consistent with axis=0 vs. axis=1
forecast.at[forecast.shape[0] - 1, 'state'] = 'Total'
forecast

# set index for forecast as state, then add columns for next 2 months (3 months total) by 
# creating columns (pd.Series) containing projections for each month
# and then add the columns to forecast (vector operations...)


# In[26]:


forecast.loc[~forecast.state.str.match('Total', na=False)].sum()


# In[27]:


forecast.index


# In[28]:


forecast.to_excel('anonymized forecast '+ str(forecast_day).split(' ')[0] + '.xlsx')


# In[29]:


# GET PERCENT INCREASE BETWEEN TOTAL COLS FOR EACH MONTH, THEN APPLY TO ACTUAL SALES IN EACH OF THOSE MONTHS TO GET 
# PROJECTED OVERALL SALES


# In[32]:


#drop "Total row from forecast"
forecast = forecast.loc[~forecast.state.str.match('Total', na=False)]

# loop [num_months] times to generate graphs for each  month to be predicted, starting at 2nd column (skip 'state' column)
for i in range(1, len(forecast.columns), 2):

    year_ago_sales_str = forecast.columns[i]
    projected_sales_str = forecast.columns[i + 1]
    # set width of bar
    barWidth = .5

    # set height of bar
    bars1 = forecast[year_ago_sales_str].tolist()
    bars2 = forecast[projected_sales_str].tolist()

    # Set position of bar on X axis
    r1 = np.arange(len(bars1))
    r2 = [x + barWidth for x in r1]

    # Make the plot
    plt.bar(r1, bars1, color='#7f6d5f', width=barWidth, edgecolor='white', label=year_ago_sales_str)
    plt.bar(r2, bars2, color='#557f2d', width=barWidth, edgecolor='white', label=projected_sales_str)

    # Add xticks on the middle of the group bars
    plt.xlabel('group', fontweight='bold')
    plt.xticks([r + barWidth for r in range(len(bars1))], forecast.state.tolist())

    # Create legend & Show graphic
    plt.legend()
    plt.rcParams['figure.figsize'] = (30,15)
    plt.show()
    # https://stackoverflow.com/questions/8213522/when-to-use-cla-clf-or-close-for-clearing-a-plot-in-matplotlib
    plt.clf()


# In[ ]:


#  %reset -f


# In[ ]:





# In[ ]:




