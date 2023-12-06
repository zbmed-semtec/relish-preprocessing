import pandas as pd
from sklearn.model_selection import train_test_split


# Load the dataset
df = pd.read_csv('relish.tsv', sep='\t')
df.columns=['PID1', 'PID2','Value']

from sklearn.model_selection import train_test_split 
train, test = train_test_split(df, test_size=0.20, stratify=df['Value'])

# Save the training and test sets to .tsv files
train.to_csv('RELISH_Training_Dataset.tsv', sep='\t', index=False)
test.to_csv('RELISH_Test_Dataset.tsv', sep='\t', index=False)

# Load the dataset
dftr = pd.read_csv('RELISH_Training_Dataset.tsv', sep='\t')

