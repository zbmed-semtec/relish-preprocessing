import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

"""
Data Splitting Algorithm

This script reads a TSV file ('RELISH.tsv') containing pairs of articles with relevance scores. It identifies unique reference and assessed articles, 
filters the data based on their existence, and saves excluded pairs in 'valid.tsv'. The main loop iterates 1000 times, 
splitting the data into training and testing sets with an 80/20 ratio. The best split is determined by minimizing the error from the target split percentage. 
Results, including sizes and percentages, are reported, and the best train and test splits are saved in 'train_split.tsv' and 'test_split.tsv'.

Usage:
- Ensure 'RELISH.tsv' is correctly formatted.
- Run the script for data splitting and result analysis.
- Check 'valid.tsv', 'train_split.tsv', and 'test_split.tsv' for excluded pairs and best splits.

Note:
- The loop uses different random seeds for each iteration to explore various splits.
- Adjust the random seed for experimentation and reproducibility.
"""


# Load the data
# data = pd.read_csv('data/output/relish-ground-truth/RELISH.tsv', delimiter='\t', header=None)
data = pd.read_csv('RELISH.tsv', delimiter='\t', header=None)
print('Initial pairs in relevance matrix:', len(data))

# Get the unique reference articles
refDocs = np.unique(data[0])  # First column
print('Length of unique reference articles:', len(refDocs))

# Get the unique assessed articles
asdDocs = np.unique(data[1])
print('Length of unique assessed articles:', len(asdDocs))

# Find reference articles if they do not exist in PID2
onlyRefDocs = [pid for pid in refDocs if pid not in asdDocs]  # Second column
print('Length of reference articles that do not exist as assessed articles:',len(onlyRefDocs))

# Assuming onlyRefDocs is the list of reference articles that do not exist as assessed articles
onlyRefDocs_data = data[data[0].isin(onlyRefDocs)]

# Find reference articles if they exist in PID2
notonlyRefDocs = [pid for pid in refDocs if pid in asdDocs]  # Second column
print('Length of reference articles that also exist as assessed articles:', len(notonlyRefDocs))

# Filter data based on onlyRefDocs
refRelMatrix = data[data[0].isin(onlyRefDocs)]  # Filter based on PID1
print('Total pairs after filtering:', len(refRelMatrix))

# Save the pairs being removed to 'valid.tsv'
valid_data = data[~data[0].isin(onlyRefDocs)]
valid_data.to_csv('valid.tsv', sep='\t', header=None, index=False)

# # Remove the corresponding pairs from data
# refRelMatrix = data[~data[1].isin(refDocs)]  # Filter based on PID2

# Initialize variables to store the best split
best_split = None
best_error = float('inf')
total_rows_initial = len(refRelMatrix)  # Total rows in the original refRelMatrix

# Loop for 1000 iterations
for i in range(1000):
    # Generate a different seed for each iteration
    np.random.seed(i)

    # Split onlyRefDocs into 80/20
    # train_onlyRef, test_onlyRef = train_test_split(onlyRefDocs, test_size=0.2)

    # Use 'Relevance' as the stratification variable
    train_data, test_data = train_test_split(onlyRefDocs_data, test_size=0.2, random_state=42, stratify=onlyRefDocs_data[2])

    # Filter refRelMatrix based on train_onlyRef
    ref_rel_train = refRelMatrix[refRelMatrix[0].isin(train_onlyRef)]  # Filter based on PID1

    # Update refRelMatrix by removing rows corresponding to train_onlyRef
    ref_rel_test = refRelMatrix[~refRelMatrix[0].isin(train_onlyRef)]  # Update based on PID1

    # Print out the size of train_onlyRef, ref_rel_train, and total rows in train and test for debugging
    total_rows_train_test = len(train_onlyRef) + len(test_onlyRef)
    print(f"Iteration {i+1}: Train OnlyRefDocs size: {len(train_onlyRef)}, Ref Rel Train size: {len(ref_rel_train)}, "
          f"Total rows in train and test: {total_rows_train_test}", f"Total pairs: {total_rows_initial}")

    # Find the percentage of those pairs in the 80-split
    train_percentage = len(ref_rel_train) / total_rows_initial

    # Calculate the error from 80%
    error = abs(train_percentage - 0.8)

    # Check if this split gives the closest pairs split to 80%
    if error < best_error:
        best_error = error
        best_split = (train_onlyRef, test_onlyRef, ref_rel_train, ref_rel_test)

    # Break the loop if all pairs have been exhausted
    if len(refRelMatrix) == 0:
        print("All pairs have been exhausted.")
        break

# Report best results
if best_split:
    best_train_onlyRef, best_test_onlyRef, ref_rel_train, ref_rel_test = best_split
    print("Best Split Found:")
    print(f"Train Data Size by PMID: {len(best_train_onlyRef)}, Test Data Size by PMID: {len(best_test_onlyRef)}")
    print(f"Train Data Size Pairs: {len(ref_rel_train)}, Test Data Size Pairs: {len(ref_rel_test)}")
    print(f"Percentage of Pairs in Train Data: {len(ref_rel_train) / total_rows_initial}")
    print(f"Percentage of Pairs in Test Data: {len(ref_rel_test) / total_rows_initial}")
    print(f"Error from 80%: {best_error}")

    # # Save the best train and test splits to separate files
    df = pd.DataFrame(ref_rel_train).to_csv('train_split.tsv', sep='\t', index=False)
    df = pd.DataFrame(ref_rel_test).to_csv('test_split.tsv', sep='\t', index=False)
else:
    print("No iterations performed.")

