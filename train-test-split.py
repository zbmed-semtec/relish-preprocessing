#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from sklearn.model_selection import train_test_split


# In[2]:


# Load the dataset
df = pd.read_csv('relish.tsv', sep='\t')


# In[3]:


df.columns=['PID1', 'PID2','Value']


# In[6]:


from sklearn.model_selection import train_test_split 
train, test = train_test_split(df, test_size=0.20, stratify=df['Value'])


# In[7]:


# Save the training and test sets to .tsv files
train.to_csv('RELISH_Training_Dataset.tsv', sep='\t', index=False)
test.to_csv('RELISH_Test_Dataset.tsv', sep='\t', index=False)


# In[8]:


# Load the dataset
dftr = pd.read_csv('RELISH_Training_Dataset.tsv', sep='\t')

