import argparse
import pandas as pd
import re
import glob
import json


def read_files(args: argparse.Namespace) -> pd.DataFrame:
    """
    Read the input files from the arguments.

    Parameters
    ----------
    args: argparse.Namespace
        Arguments from the argsparse package.

    Returns
    -------
    data: pandas.DataFrame
        Dataframe with 3 columns: PMID, Title and abstract. Read from .tsv files
        provided in the input arguments.
    """
    if args.input:
        data = pd.read_csv(args.input, sep="\t", quotechar="`")
    elif args.indir:
        indir = args.indir.strip("/")
        in_files = glob.glob(f"{indir}/*.tsv")

        df_list = []
        for file in in_files:
            df_list.append(pd.read_csv(file, sep="\t", quotechar="`"))
        data = pd.concat(df_list, axis=0, ignore_index=True)

    return data


def create_dictionary(data: pd.DataFrame) -> dict:
    """
    Given the input dataframe containing an abstrat column, matches de regular
    expression and counts in how many articles does the match appear.

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe containing an abstract column.

    Returns
    -------
    structure_words_dict: dict
        Dictionary where the keys are the matched structure words and the values
        are the number of articles in which the structure word is found.

    """
    structure_words_dict = {}
    keywords_pattern = r"(?:^[\s]*|\.|\?|: )(?: *)(?=([A-Z]+[A-Z\s&a-z]{2,69}:\s))"

    for abstract in data["abstract"]:
        structure_words = set(re.findall(keywords_pattern, abstract))
        for word in structure_words:
            structure_words_dict[word] = structure_words_dict.get(word, 0) + 1

    return structure_words_dict


def sort_dictionary(structure_words_dict: dict) -> dict:
    """
    Given any dictionary, sorts by the value in descending order.

    Parameters
    ----------
    structure_words_dict: dict
        Input dictionary.

    Returns
    -------
    dict:
        Output sorted dictionary by its value in descending order.
    """
    return {k: v for k, v in sorted(structure_words_dict.items(), key=lambda item: item[1], reverse=True)}


def convert_to_json(structure_words_dict: dict, num_articles: int) -> list:
    """
    Converts the dictionary of counts to a list of dictionaries in with the
    following parameters:
        - word: word of group of words that matches the regular expression.
        - occurrences: number of articles in which the structure word is found.
        - ratio_of_occurrences: relative frequency of appearance of the
          structure word.

    Parameters
    ----------
    structure_words_dict: dict
        Dictionary where the keys are the matched structure words and the values
        are the number of articles in which the structure word is found.
    num_articles: int
        Number of articles in the dataset.

    Returns
    -------
    word_list: list[dict]
        List of dictionaries containing information of all the matched structure
        words.
    """
    word_list = []
    for key, value in structure_words_dict.items():
        word_entry = {"word": key, "occurrences": value,
                      "ratio_of_occurrences": value / num_articles}
        word_list.append(word_entry)

    return word_list


def convert_to_list(word_json: list) -> list:
    """
    Converts a list of dictionaries to a list of structure words.

    Parameters
    ----------
    word_json: list[dict]
        List of dictionaries containing information of all the matched structure
        words.

    Returns
    -------
    list:
        List of structure words.
    """
    return [word["word"] for word in word_json]


def prune_structure_words(word_list: list, ratio_threshold: float = 0, occurrences_threshold: int = 0) -> list:
    """
    Given some threshold for either the relative frequency of appearance or the
    total number of occurrences, prunes the list of dictionaries containing
    informaton of all the matched structure words.

    Parameters
    ----------
    word_json: list[dict]
        List of dictionaries containing information of all the matched structure
        words.
    ratio_threshold: float
        Minimum relative frequency of appearance of the structure word to be
        kept in the list of dictionaries.
    occurrences_threshold: float
        Minimum total occurrences of the structure word to be kept in the list
        of dictionaries.

    Returns
    -------
    output_list: list[dict]
        Pruned list of dictionaries containing information of all the matched structure
        words that satisfy the imposed thresholds.
    """
    output_list = [entry for entry in word_list if entry["ratio_of_occurrences"]
                   > ratio_threshold and entry["occurrences"] > occurrences_threshold]

    return output_list


def export_to_json(out_file: str, word_list: list) -> None:
    """
    Writes the list of dictionaries with the structure words into the output
    file.

    Parameters
    ----------
    out_file: str
        Path to the output file.
    word_list: list[dict]
        List of dictionaries containing information of the matched structure
        words.
    """
    if not out_file.endswith(".json"):
        out_file += ".json"

    with open(out_file, "w") as file:
        json.dump(word_list, file, indent=4)


def export_to_list(out_file: str, word_list: list) -> None:
    """
    Writes the list of structure words into the output file.

    Parameters
    ----------
    out_file: str
        Path to the output file.
    word_list: list[dict]
        List of dictionaries containing information of the matched structure
        words.
    """
    if not out_file.endswith(".txt"):
        out_file += ".txt"

    word_list = convert_to_list(word_list)

    with open(out_file, "w") as file:
        json.dump(word_list, file, indent=0)


def structure_words_pipeline(data: pd.DataFrame, ratio_threshold: float = 0, occurrences_threshold: int = 0) -> list:
    """
    Pipeline of all the required functions. From the data, it creates the
    dictionary of structure words, sorts them and prunes according to the input
    thresholds.

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe containing an abstract column.
    ratio_threshold: float
        Minimum relative frequency of appearance of the structure word to be
        kept in the list of dictionaries.
    occurrences_threshold: float
        Minimum total occurrences of the structure word to be kept in the list
        of dictionaries.

    Returns
    -------
    SW_json_pruned: list[dict]
        Pruned list of dictionaries containing information of all the matched
        structure words that satisfy the imposed thresholds.
    """
    SW_dict = create_dictionary(data)
    SW_dict = sort_dictionary(SW_dict)
    SW_json = convert_to_json(SW_dict, len(data))
    SW_json_pruned = prune_structure_words(
        SW_json, ratio_threshold, occurrences_threshold)

    return SW_json_pruned


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-i", "--input", type=str,
                       help="Path to input TSV file")
    group.add_argument("-d", "--indir", type=str,
                       help="Path to input folder with TSV files")
    parser.add_argument("-o", "--output", type=str, default="structure_word_list",
                        help="Path to output text file/dir")
    parser.add_argument("--ratio_threshold", type=float, default=0,
                        help="Minimum relative frequency of appearance of the structure word to be considered")
    parser.add_argument("--occurrences_threshold", type=int, default=0,
                        help="Minimum total occurrences of the structure word to be considered")
    args = parser.parse_args()
    out_file = args.output

    data = read_files(args)

    SW_json_pruned = structure_words_pipeline(
        data, ratio_threshold=args.ratio_threshold, occurrences_threshold=args.occurrences_threshold)

    # By default, both a .json file and a .txt file are created given the output filename.
    export_to_json(out_file, SW_json_pruned)
    export_to_list(out_file, SW_json_pruned)
