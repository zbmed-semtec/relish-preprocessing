import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import train_test_split
from numpy import array

# Load the dataset
df_relish = pd.read_csv('data/RELISH.tsv', sep='\t')
df_relish.columns=['PID1', 'PID2','Value']

dfr_pid1=df_relish['PID1'].tolist()
dfr_pid2=df_relish['PID2'].tolist()

data = np.load('data/RELISH_Tokenized_Removed_Stopwords.npy', allow_pickle=True)
df_npy = pd.DataFrame(data)

df_npy = pd.DataFrame(data, columns=['PID', 'Title', 'Abstract'])

gt_pid=df_npy['PID'].tolist()
gt_pid = [int(arr) for arr in gt_pid]

def matching_and_non_matching_pairs(df_rel, df_npy, matching_output_tsv='output/matching_pairs_test_80_20.tsv',
                                    non_matching_output_tsv='output/non_matching_pairs_val.tsv'):
    # Read data from the first file
    file1_data_train = df_rel

    # Read data from the second file
    file2_data_train = df_npy

    # Extract unique PIDs from both columns (PID1 and PID2) in the first file
    pids_file1_train = set(file1_data_train['PID1']).union(set(file1_data_train['PID2']))

    # Extract PIDs from the second file
    pids_file2_train = set(file2_data_train['PID'])

    # Find pairs from the first file where both PID1 and PID2 are present in the second file
    matching_pairs_train = []
    non_matching_pairs_train = []

    for _, row in file1_data_train.iterrows():
        pid1 = row['PID1']
        pid2 = row['PID2']

        if pid1 in pids_file2_train and pid2 in pids_file2_train:
            matching_pairs_train.append((pid1, pid2))
        else:
            non_matching_pairs_train.append((pid1, pid2))

    # Create a DataFrame for matching pairs
    matching_pairs_df = pd.DataFrame(matching_pairs_train, columns=['PID1', 'PID2'])

    # Save matching pairs to a TSV file
    matching_pairs_df.to_csv(matching_output_tsv, sep='\t', index=False)

    # Create a DataFrame for non-matching pairs
    non_matching_pairs_df = pd.DataFrame(non_matching_pairs_train, columns=['PID1', 'PID2'])

    # Save non-matching pairs to a TSV file
    non_matching_pairs_df.to_csv(non_matching_output_tsv, sep='\t', index=False)

    mtpr1 = (len(matching_pairs_train) / len(file1_data_train['PID1'])) * 100
    return mtpr1


perc=0
best_train_set = None
best_test_set = None
list_perc=[]
for i in range(10000):
  # dfnpy_train, dfnpy_test=split_data(df_npy)
  dfnpy_train, dfnpy_test = train_test_split(df_npy, test_size=0.20, shuffle=True)
  #memory variables for best and worst case.
  dfnpy_train.to_csv('output/RELISH_NPY_Training_Dataset.tsv', sep='\t', index=False)
  dfnpy_test.to_csv('output/RELISH_NPY_Test_Dataset.tsv', sep='\t', index=False)

  # Load the dataset
  dfnpy_train = pd.read_csv('output/RELISH_NPY_Training_Dataset.tsv', sep='\t')
  dfnpy_test = pd.read_csv('output/RELISH_NPY_Test_Dataset.tsv', sep='\t')

  test_perc=matching_and_non_matching_pairs(df_relish,dfnpy_test)
  list_perc.append(test_perc)
  if(test_perc>perc and test_perc>=10):
    perc=test_perc
    best_train_set=dfnpy_train.copy()
    best_test_set=dfnpy_test.copy()

best_train_set.to_csv('output/best_train_80_latest.tsv')
best_test_set.to_csv('output/best_test_20_latest.tsv')
print("Best Match Percentage : ",perc)

with open('output/percentage_new_test.txt', 'w') as file:
  for index,item in enumerate(list_perc):
    file.write(f"Index {index}: {item}\n")
