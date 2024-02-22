import pandas as pd
import numpy as np


def extract_pmids(input_file: str):
        # Calculating unique PMIDs present in the Train Dataset
        train_df = pd.read_csv('train_split.tsv', sep='\t')
        pmid1_train_set = set(train_df['PMID1'])
        pmid2_train_set = set(train_df['PMID2'])
        unique_pmids_train = pmid1_train_set.union(pmid2_train_set)
        print('Number of unique PMIDs in Train Dataset:', len(unique_pmids_train))

        # Calculating unique PMIDs present in the Test Dataset
        test_df = pd.read_csv('test_split.tsv', sep='\t')
        pmid1_test_set = set(test_df['PMID1'])
        pmid2_test_set = set(test_df['PMID2'])
        unique_pmids_test = pmid1_test_set.union(pmid2_test_set)
        print('Number of unique PMIDs in Test Dataset:', len(unique_pmids_test))

        # Checking whether all PMIDs are exclusive between the Train and the Test dataset
        print(len((unique_pmids_train).intersection(unique_pmids_test)))

        # Loading the RELISH tokens npy file
        text_file = np.load(input_file, allow_pickle=True)

        data_train = []
        data_test = []
        data_val = []
        for line in text_file:
                if int(line[0]) in unique_pmids_train:
                        data_train.append(line)
                elif int(line[0]) in unique_pmids_test:
                        data_test.append(line)
                else:
                        data_val.append(line)

        print(len(data_train), len(data_test), len(data_val))

        # Saving all three npy files witht he corresponding pmids, title and abstracts
        np.save('relish_train_annotated_tokens_removed_stopwords.npy', data_train, allow_pickle=True)
        np.save('relish_test_annotated_removed_stopwords.npy', data_test, allow_pickle=True)
        np.save('relish_val_annotated_tokens_removed_stopwords.npy', data_val, allow_pickle=True)


extract_pmids('data/RELISH_Tokenized_Removed_Stopwords.npy')
extract_pmids('data/RELISH_Annotated_Tokenized_Removed_Stopwords.npy')


