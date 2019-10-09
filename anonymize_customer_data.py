#!/usr/bin/env python
# coding: utf-8

# In[115]:


import pandas as pd
# import contact information data and drop unnecessary columns
contacts = pd.read_csv('customer_contact_list.csv').drop(
    columns=['Unnamed: 0', 'Full Name','Phone Numbers', 'Email', 'Shipping Address'])

# extract state from billing address and create column
contacts['state'] = contacts['Billing Address'].str.extract(r'\.*(\w\w)\s\d\d\d\d\d')
# convert state abbreviations to upper case
contacts['state'] = contacts['state'].str.upper()

# drop the billing address column
contacts = contacts.drop(columns=['Billing Address'])
# drop the 'All customers' row
contacts = contacts[~contacts.Customer.str.contains('All customers', na=False)]
contacts


# In[116]:


def anon_cust(row):
    return "Customer " + str(row.name)


# In[117]:


contacts['Anonymized customer'] = contacts.apply(lambda row: anon_cust(row), axis=1)


# In[118]:


contacts


# In[119]:


# contacts = contacts.drop(columns=['Customer'])
contacts = contacts.rename(columns={'Customer':'customer'})
contacts


# In[ ]:





# In[120]:


# import the sales by customer data for the past (two) years
sales = pd.read_excel('sales_by_customer_detail.xlsx', skiprows=4, names=['customer','date','transactiontype','num','product','memo','qty','price','sales','balance'
])

# drop unnecessary rows
sales = sales.drop(columns=['transactiontype' ,'num' ,'product' ,'qty','price' ,'balance' ,'memo'])

# only keep rows that *do not* contain 'Total' in the 'customer' column
sales = sales.loc[~sales.customer.str.contains('Total', na=False)]

# reset the index
sales.reset_index(drop=True)

# fill customer names forward through rows missing customer name
sales['customer'] = sales['customer'].fillna(method='ffill')

# drop any rows that are missing ANY of customer name, transaction date, or amount (which should just be junk rows)
sales = sales.dropna()

# uncomment below to check which columns are being dropped 
# sales[sales.isnull().any(axis=1)].to_excel('sales_na.xlsx')

# convert date column to datetime
sales.date = pd.to_datetime(sales.date)

sales.head()


# In[121]:


# use merge to effectively add the 'state' column to sales dataframe
sales = sales.merge(contacts, how='left', on='customer').sort_values(by='date')
# fill transactions with missing states with 'other'
sales.state = sales.state.fillna('other')

sales


# In[122]:


contacts.loc[contacts['customer'] == 'Bianca Simonian']


# In[123]:


sales.sum()


# In[124]:


sales = sales.drop(columns=['customer']).rename(columns={'Anonymized customer':'customer'})
sales


# In[125]:


sales.sales = sales.sales.apply(lambda x: x * 15)


# In[126]:


sales


# In[127]:


sales.to_csv('sales_anonymized.csv')

