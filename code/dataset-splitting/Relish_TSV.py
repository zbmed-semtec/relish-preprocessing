import pandas as pd
from sklearn.model_selection import train_test_split


# Load the dataset
df_train = pd.read_csv('RELISH_Training_Dataset.tsv', sep='\t')
df_test = pd.read_csv('RELISH_Test_Dataset.tsv', sep='\t')

df_train = pd.concat([df_train['PID1'], df_train['PID2']])
df_test = pd.concat([df_test['PID1'], df_test['PID2']])

df_train = df_train.drop_duplicates()
df_test = df_test.drop_duplicates()

df_train.to_csv('relish_df_train.tsv', sep='\t', index=False)
df_test.to_csv('relish_df_test.tsv', sep='\t', index=False)

# Load the TSV file containing PMID, title, and abstract
df2_train = pd.read_csv('relish.tsv', sep='\t')
# Filter the rows where PMID is in the list of unique PMIDs
df22_train = df2_train[df2_train['PMID'].isin(df_train)]
df22_train
df22_train.to_csv('relish_train.tsv', sep='\t', index=False)

# Load the TSV file containing PMID, title, and abstract
df2_test = pd.read_csv('relish.tsv', sep='\t')
# Filter the rows where PMID is in the list of unique PMIDs
df22_test
df22_test.to_csv('relish_test.tsv', sep='\t', index=False)

