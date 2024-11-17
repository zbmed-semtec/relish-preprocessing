import pandas as pd
import numpy as np


def create_text_datasets(file_path, test_fuile, train_file, valid_file):
    main_file = pd.read_csv(file_path, sep='\t')
    test_file = np.load(test_file, allow_pickle=True)
    pmids = [np.int64(line[0]) for line in test_file]
    filtered_main_file = main_file[main_file['PMID'].isin(pmids)]
    filtered_main_file.to_csv("data/input_test_text_data.tsv", sep='\t', index=False)

    train_file = np.load(train_file, allow_pickle=True)
    pmids = [np.int64(line[0]) for line in test_file]
    filtered_main_file = main_file[main_file['PMID'].isin(pmids)]
    filtered_main_file.to_csv("data/input_train_text_data.tsv", sep='\t', index=False)

    valid_file = np.load(valid_file, allow_pickle=True)
    pmids = [np.int64(line[0]) for line in test_file]
    filtered_main_file = main_file[main_file['PMID'].isin(pmids)]
    filtered_main_file.to_csv("data/input_valid_text_data.tsv", sep='\t', index=False)