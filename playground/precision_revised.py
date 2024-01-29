import argparse
import pandas as pd
import numpy as np
from typing import List, Tuple


def read_file(tsv_file: str) -> Tuple[List, pd.DataFrame]:
    """
    Reads the input 4-column cosine similarity existing pairs TSV file in a pandas dataframe, generates all the unique PMIDs
    and returns the dataframe.
    Parameters
    ----------
    tsv_file : str
        File path to the 4-column cosine similarity existing pairs TSV file.
    Returns
    -------
    ref_pmids : list
        List of all unique PMIDs.
    data : pd.Dataframe
        Pandas Dataframe cosisting of 4 columns: PMID1, PMID2, Relevance, Cosine similarity.
    """
    colnames = ["PMID1", "PMID2", "Relevance", "Cosine Similarity"]
    data = pd.read_csv(tsv_file, sep='\t', header=0, names=colnames)
    ref_pmids = data["PMID1"].unique()
    return ref_pmids, data


def sort_collection(pmid: str, data: pd.DataFrame) -> pd.DataFrame:
    """
    Sorts the input dataframe for the given PMID based on the cosine similarity values in the descending order.
    Parameters
    ----------
    pmid : str
        PMID for which the collection needs to be sorted.
    data : pd.Datafarme
        Pandas Dataframe cosisting of 4 columns: PMID1, PMID2, Relevance, Cosine similarity.
    Returns
    -------
    sorted_collection : pd.Dataframe
        Sorted Pandas Dataframe based on the given PMID .
    """
    collection = data[data['PMID1'] == pmid]
    sorted_collection = collection.sort_values(['PMID1', 'Cosine Similarity'],
                                               ascending=[True, False], ignore_index=True)
    return sorted_collection


def calculate_precision(sorted_collection: pd.DataFrame, n: int) -> float:
    """
    Calculates the precision score for the input sorted_collection at given n value.
    Parameters
    ----------
    sorted_collection : pd.Dataframe
        Sorted Pandas Dataframe based on the given PMID .
    n : int
        Value of n at which precision is to be calculated.
    Returns
    -------
    precision_n : float
        Value of Precision@n.
    """
    top_n = sorted_collection[:n]
    # true_positives_n = len(top_n[(top_n["Relevance"] == 2)])
    true_positives_n = len(top_n[(top_n["Relevance"] == 2) | (top_n["Relevance"] == 1)])
    precision_n = round(true_positives_n/n, 4)
    return precision_n


def generate_matrix(ref_pmids: list, data: pd.DataFrame) -> np.array:
    """
    Wrapper function to generate the precision matrix at the given values of n for every unique PMID in the input data.
    Parameters
    ----------
    ref_pmids : list
        List of all unique PMIDs.
    data : pd.Dataframe
        Pandas Dataframe cosisting of 4 columns: PMID1, PMID2, Relevance, Cosine similarity.
    Returns
    -------
    precision_matrix : np.array
        Generated precision matrix.
    """
    value_of_n = [5, 10, 15, 20, 25, 50]
    precision_matrix = np.empty(shape=(len(ref_pmids), len(value_of_n)))
    for pmid_index, pmid in enumerate(ref_pmids):
        sorted_collection = sort_collection(pmid, data)
        if len(sorted_collection) >= max(value_of_n):
            for index, n in enumerate(value_of_n):
                precision_n = calculate_precision(sorted_collection, n)
                precision_matrix[pmid_index][index] = precision_n
            else:
                continue
    return precision_matrix


def write_to_tsv(ref_pmids: list, precision_matrix: np.array, output_filepath: str):
    """
    Write the generated precision matrix to a TSV file and computes the avergae of the precision@n scores.
    Parameters
    ----------
    ref_pmids: list
        List of all unique PMIDs.
    precision_matrix : np.array
        Generated precision matrix.
    output_filepath : str
        File path to save the TSV file.
    """
    matrix = pd.DataFrame(precision_matrix, columns=['P@5', 'P@10', 'P@15', 'P@20', 'P@25', 'P@50'])
    matrix.insert(0, 'PMIDs', ref_pmids)
    # Calculate and append average of each precision score
    average_values = ['Average'] + list(matrix[['P@5', 'P@10', 'P@15', 'P@20', 'P@25', 'P@50']]
                                        .mean(axis=0).round(4))
    matrix.loc[len(matrix.index)] = average_values
    pd.DataFrame(matrix).to_csv(output_filepath, sep="\t")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cosine_file_path", help="File path to the 4-column cosine similarity existing pair matrix"
                        , required=True)
    parser.add_argument("-o", "--output_path", help="File path to save the precision matrix",
                        required=True)

    args = parser.parse_args()

    ref_pmids, data = read_file(args.cosine_file_path)
    matrix = generate_matrix(ref_pmids, data)
    write_to_tsv(ref_pmids, matrix, args.output_path)
