import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import train_test_split
from numpy import array

df_relish = pd.read_csv('data/RELISH.tsv', sep='\t')
df_relish.columns=['PID1', 'PID2','Value']

dfr_pid1=df_relish['PID1'].tolist()
dfr_pid2=df_relish['PID2'].tolist()

data = np.load('data/RELISH_tokenized.npy', allow_pickle=True)
df_npy = pd.DataFrame(data)

df_npy = pd.DataFrame(data, columns=['PID', 'Title', 'Abstract'])



def matching_pairs(df_rel, df_npy):

    """
    Finds matching pairs of PID1 and PID2 between two datasets.

    Args:
    - df_rel (DataFrame): DataFrame containing PID1, PID2, and Value columns.
    - df_npy (DataFrame): DataFrame containing PID, Title, and Abstract columns.

    Returns:
    - float: Matching pairs ratio as a percentage.
    """
    file1_data_train = df_rel  
    file2_data_train = df_npy  


    pids_file1_train = set(file1_data_train['PID1']).union(set(file1_data_train['PID2']))
    pids_file2_train = set(file2_data_train['PID'])

    matching_pairs_train = []

    for _, row in file1_data_train.iterrows():
        pid1 = row['PID1']
        pid2 = row['PID2']

        if pid1 in pids_file2_train and pid2 in pids_file2_train:
            matching_pairs_train.append((pid1, pid2))

    mtpr1 = (len(matching_pairs_train) / len(file1_data_train['PID1'])) * 100
    return mtpr1


perc=0
best_train_set = None
best_test_set = None
list_perc=[]

def best_train_test():

    """
    Finds the best train and test datasets based on matching pairs.

    Saves the best train and test datasets as TSV files.
    """

    for i in range(100):
    # dfnpy_train, dfnpy_test=split_data(df_npy)
    dfnpy_train, dfnpy_test = train_test_split(df_npy, test_size=0.20, shuffle=True)
    #memory variables for best and worst case.
    dfnpy_train.to_csv('split/RELISH_NPY_Training_Dataset.tsv', sep='\t', index=False)
    dfnpy_test.to_csv('split/8_RELISH_NPY_Test_Dataset.tsv', sep='\t', index=False)

    # Load the dataset
    dfnpy_train = pd.read_csv('split/RELISH_NPY_Training_Dataset.tsv', sep='\t')
    dfnpy_test = pd.read_csv('split/RELISH_NPY_Test_Dataset.tsv', sep='\t')

    train_perc=matching_pairs(df_relish,dfnpy_train,'split/matching_pairs_train_80_20.tsv')
    list_perc.append(train_perc)
    if(train_perc>perc):
        perc=train_perc
        best_train_set=dfnpy_train.copy()
        best_test_set=dfnpy_test.copy()

    best_train_set.to_csv('split/best_train_80_new.tsv')
    best_test_set.to_csv('split/best_test_20_new.tsv')

    with open('split/percentage.txt', 'w') as file:
    for index,item in enumerate(list_perc):
        file.write(f"Index {index}: {item}\n")



def matching_pairs_test_file(df_rel, df_npy, output_tsv=='split/matching_pairs_test_80_20.tsv'):

    """
    Finds matching pairs of PID1 and PID2 between two datasets.

    Args:
    - df_rel (DataFrame): DataFrame containing PID1, PID2, and Value columns.
    - df_npy (DataFrame): DataFrame containing PID, Title, and Abstract columns.
    - output_tsv (str): Output file path to save matching pairs as a TSV file.

    Returns:
    - float: Matching pairs ratio as a percentage.
    """

    file1_data_train = df_rel 
    file2_data_train = df_npy 

    # Extract unique PIDs from both columns (PID1 and PID2) in the first file
    pids_file1_train = set(file1_data_train['PID1']).union(set(file1_data_train['PID2']))

    # Extract PIDs from the second file
    pids_file2_train = set(file2_data_train['PID'])

    # Find pairs from the first file where both PID1 and PID2 are present in the second file
    matching_pairs_train = []

    for _, row in file1_data_train.iterrows():
        pid1 = row['PID1']
        pid2 = row['PID2']

        if pid1 in pids_file2_train and pid2 in pids_file2_train:
            matching_pairs_train.append((pid1, pid2))

    # Create a DataFrame for matching pairs
    matching_pairs_df = pd.DataFrame(matching_pairs_train, columns=['PID1', 'PID2'])

    # Save matching pairs to a TSV file
    matching_pairs_df.to_csv(output_tsv, sep='\t', index=False)

    mtpr1 = (len(matching_pairs_train) / len(file1_data_train['PID1'])) * 100
    return mtpr1



def matching_pairs_train_file(df_rel, df_npy, output_tsv=='split/matching_pairs_train_80_20.tsv'):


    """
    Finds matching pairs of PID1 and PID2 between two datasets.

    Args:
    - df_rel (DataFrame): DataFrame containing PID1, PID2, and Value columns.
    - df_npy (DataFrame): DataFrame containing PID, Title, and Abstract columns.
    - output_tsv (str): Output file path to save matching pairs as a TSV file.

    Returns:
    - float: Matching pairs ratio as a percentage.
    """

    file1_data_train = df_rel
    file2_data_train = df_npy

    # Extract unique PIDs from both columns (PID1 and PID2) in the first file
    pids_file1_train = set(file1_data_train['PID1']).union(set(file1_data_train['PID2']))

    # Extract PIDs from the second file
    pids_file2_train = set(file2_data_train['PID'])

    # Find pairs from the first file where both PID1 and PID2 are present in the second file
    matching_pairs_train = []

    for _, row in file1_data_train.iterrows():
        pid1 = row['PID1']
        pid2 = row['PID2']

        if pid1 in pids_file2_train and pid2 in pids_file2_train:
            matching_pairs_train.append((pid1, pid2))

    # Create a DataFrame for matching pairs
    matching_pairs_df = pd.DataFrame(matching_pairs_train, columns=['PID1', 'PID2'])

    # Save matching pairs to a TSV file
    matching_pairs_df.to_csv(output_tsv, sep='\t', index=False)

    mtpr1 = (len(matching_pairs_train) / len(file1_data_train['PID1'])) * 100
    return mtpr1



def matching_pairs_relish_test(df_rel, df_npy, output_tsv='split/matching_pairs_relish_test.tsv'):

    """
    Finds matching pairs of PID1 and PID2 between two datasets and includes the 'Value' attribute.

    Args:
    - df_rel (DataFrame): DataFrame containing PID1, PID2, and Value columns.
    - df_npy (DataFrame): DataFrame containing PID, Title, and Abstract columns.
    - output_tsv (str): Output file path to save matching pairs as a TSV file.

    Returns:
    - float: Matching pairs ratio as a percentage.
    """

    file1_data_train = df_rel
    file2_data_train = df_npy 

    # Extract unique PIDs from both columns (PID1 and PID2) in the first file
    pids_file1_train = set(file1_data_train['PID1']).union(set(file1_data_train['PID2']))

    # Extract PIDs from the second file
    pids_file2_train = set(file2_data_train['PID'])

    # Find pairs from the first file where both PID1 and PID2 are present in the second file
    matching_pairs_train = []

    for _, row in file1_data_train.iterrows():
        pid1 = row['PID1']
        pid2 = row['PID2']

        if pid1 in pids_file2_train and pid2 in pids_file2_train:
            matching_pairs_train.append((pid1, pid2, row['Value']))  # Include 'Value' attribute

    # Create a DataFrame for matching pairs
    matching_pairs_df = pd.DataFrame(matching_pairs_train, columns=['PID1', 'PID2', 'Value'])  # Include 'Value' column

    # Save matching pairs to a TSV file
    matching_pairs_df.to_csv(output_tsv, sep='\t', index=False)

    mtpr1 = (len(matching_pairs_train) / len(file1_data_train)) * 100  # Calculate matching pairs ratio
    return mtpr1



def matching_pairs_relish_train(df_rel, df_npy, output_tsv='split/matching_pairs_relish_train.tsv'):
    """
    Finds matching pairs of PID1 and PID2 between two datasets and includes the 'Value' attribute.

    Args:
    - df_rel (DataFrame): DataFrame containing PID1, PID2, and Value columns.
    - df_npy (DataFrame): DataFrame containing PID, Title, and Abstract columns.
    - output_tsv (str): Output file path to save matching pairs as a TSV file.

    Returns:
    - float: Matching pairs ratio as a percentage.
    """

    file1_data_train = df_rel
    file2_data_train = df_npy

    # Extract unique PIDs from both columns (PID1 and PID2) in the first file
    pids_file1_train = set(file1_data_train['PID1']).union(set(file1_data_train['PID2']))

    # Extract PIDs from the second file
    pids_file2_train = set(file2_data_train['PID'])

    # Find pairs from the first file where both PID1 and PID2 are present in the second file
    matching_pairs_train = []

    for _, row in file1_data_train.iterrows():
        pid1 = row['PID1']
        pid2 = row['PID2']

        if pid1 in pids_file2_train and pid2 in pids_file2_train:
            matching_pairs_train.append((pid1, pid2, row['Value']))  # Include 'Value' attribute

    # Create a DataFrame for matching pairs
    matching_pairs_df = pd.DataFrame(matching_pairs_train, columns=['PID1', 'PID2', 'Value'])  # Include 'Value' column

    # Save matching pairs to a TSV file
    matching_pairs_df.to_csv(output_tsv, sep='\t', index=False)

    mtpr1 = (len(matching_pairs_train) / len(file1_data_train)) * 100  # Calculate matching pairs ratio
    return mtpr1