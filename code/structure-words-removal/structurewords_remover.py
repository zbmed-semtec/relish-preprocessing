import sys
import os
import re
import glob
import logging

from typing import Union, List

import argparse
import json
import pandas as pd


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


def read_json(input_list: str) -> list:
    """
    Read a .json file containing information about the structure words. The
    file was generated in the "structurewords_list_generator" script.

    Parameters
    ----------
    input_list: str
        Path to the structure words .json file

    Returns
    -------
    sw_json: list[dict]
        List of dictionaries containing information of all the matched structure
        words.
    """
    with open(input_list, "r") as file:
        sw_json = json.load(file)

    return sw_json


def read_list(input_list: str) -> list:
    """
    Read a .txt file containing a list of the structure words. The file was
    generated in the "structurewords_list_generator" script.

    Parameters
    ----------
    input_list: str
        Path to the structure words .txt file

    Returns
    -------
    sw_list: list
        List of structure words.
    """
    sw_list = read_json(input_list)

    if isinstance(sw_list[0], dict):
        sw_list = [word["word"] for word in sw_list]

    return sw_list


def remove_span_matches(abstract: str, span_range: list) -> str:
    """
    Given a text an a list of (start, end) ranges, eliminates from
    the text the characters between the (start, end) indices.

    This function is used to remove the matched structure words from a string.

    Parameters
    ----------
    abstract: str
        String from which to eliminate the characters.
    span_range: list[(int, int)]
        List of tuples containing the start and end indices to be removed from
        the "abstract" parameter.

    Returns
    -------
    str:
        A string with the indicated characters removed.
    """
    output = []
    i = 0
    for ran_start, ran_end in span_range:
        output.append(abstract[i:ran_start])
        i = ran_end
    output.append(abstract[i:])

    return "".join(output)


def structure_words_remover(data: Union[str, pd.DataFrame], 
                            structure_words_list: list) -> pd.DataFrame:
    """
    Rremove the structure words from either a dataframe with
    the abstract column in the data, or a string.

    Parameters
    ----------
    data: pd.DataFrame or str
        Dataframe containing an abstract column or string to remove structure
        words from.
    structure_words_list: list
        List of structure words.

    Returns
    -------
    data: pd.DataFrame or str
        Dataframe with the structure words removed from its abstract column or
        a string.
    """
    keywords_pattern = r"(?:^[\s]*|\.|\?|: )(?: *)(?=([A-Z]+[A-Z\s&a-z]{2,69}:\s))"

    # Separate the structure words list into those that match the regular
    # expression and those that do not. This is done in order to allow the user
    # to input their personal structure word list that may not necessarilly
    # match the pattern.
    regex_structure_words = []
    non_regex_strcuture_words = []
    for word in structure_words_list:
        if re.match(keywords_pattern, word):
            regex_structure_words.append(word)
        else:
            non_regex_strcuture_words.append(word)

    if isinstance(data, pd.DataFrame):
        for i, row in data.iterrows():
            abstract = row["abstract"]
            # Only write in the dataframe if the abstract is modified.
            save_abstract = False

            # Regular expression structure words
            span_ranges = [match.span(1) for match in re.finditer(
                keywords_pattern, abstract) if match.group(1) in regex_structure_words]

            if span_ranges:
                abstract = remove_span_matches(abstract, span_ranges)
                save_abstract = True

            # Non regular expression structure words
            for word in non_regex_strcuture_words:
                if not save_abstract and word in abstract:
                    save_abstract = True
                abstract = abstract.replace(word, "")

            if save_abstract:
                data.at[i, "abstract"] = abstract
    elif isinstance(data, str):
        span_ranges = [match.span(1) for match in re.finditer(
            keywords_pattern, data) if match.group(1) in regex_structure_words]

        if span_ranges:
            data = remove_span_matches(data, span_ranges)
        for word in non_regex_strcuture_words:
            data = data.replace(word, "")
    else:
        logging.error(
            "The input parameter should be either a dataframe or a string.")

    return data


def save_output(data: pd.DataFrame, output_file: str) -> None:
    """
    Save the given dataframe into the output file in a .tsv format.

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe containing an abstract column.
    output_file: str
        Path to the output .tsv file where the articles are saved without
        structure words.
    """
    if not output_file.endswith(".tsv"):
        output_file += ".tsv"
    data.to_csv(output_file, sep="\t", quotechar="`", index=False)


def load_input_xml(args: argparse.ArgumentParser) -> Union[List[str], List[str]]:
    """
    Process the arguments passed to the script to obtain a list of
    input and output XML files.

    Parameters
    ----------
    args : argparse.ArgumentParser
        Arguments from argparse.

    Returns
    -------
    files_in: list[str]
        List of input files.
    files_out: list[str]
        List of output files.
    """
    if args.indir:      # If the user inputs a directory
        if args.indir.endswith(".xml"):
            logging.error(
                f"Your input is not a directory, please use --input instead.", exc_info=False)
            sys.exit("No valid input directory.")

        indir = args.indir.rstrip("/")
        files_in = glob.glob(indir + "/*.xml")

        outdir = args.output if args.output != "data_pruned.tsv" else indir + "_no_structure_words"
        files_out = list(map(lambda x: x.replace(indir, outdir), files_in))

        if not files_in:
            logging.error(
                f"No XML files located in the input directory.", exc_info=False)
            sys.exit("No valid input directory.")

        logging.info(f"Files from {indir} will be trasnlated into {outdir}")

        if not os.path.exists(outdir):
            logging.info(f"Output directory created at {outdir}")
            os.mkdir(outdir)
    elif args.input:    # If the user inputs a file
        files_in = [args.input]
        if args.output != "data_pruned.tsv":
            files_out = [args.output]
        else:
            files_out = [args.input.replace(".xml", "_no_structure_words.xml")]

    return files_in, files_out


def pipeline_xml(files_in: List[str], files_out: List[str], structure_words_list):
    """
    Pipeline to remove a list of structure words from the input XML files. The
    output is always another XML file for each input. 

    Parameters
    ----------
    files_in : list[str]
        List of input files.
    files_out : list[str]
        List of output files.
    """
    from xml.etree import ElementTree as ET

    for i, file, in enumerate(files_in):
        logging.info(f"File {file} open.")

        xml_tree = ET.parse(file)
        xml_root = xml_tree.getroot()

        for text_tag in xml_root.iter("text"):
            text_tag.text = structure_words_remover(
                text_tag.text, structure_words_list)

        with open(files_out[i], "wb") as file:
            xml_tree.write(file, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-i", "--input", type=str,
                       help="Path to input TSV file")
    group.add_argument("-d", "--indir", type=str,
                       help="Path to input folder with TSV files")
    parser.add_argument("-l", "--list", type=str,
                        help="Path to structure_word lists previously generated", required=True)
    parser.add_argument("-o", "--output", type=str, default="data_pruned.tsv",
                        help="Path to output text file/dir")
    parser.add_argument("--xml", type=int, default=0,
                        help="Indicate if the input is an XML file.")
    args = parser.parse_args()
    out_file = args.output
    structure_words_list = read_list(args.list)

    if args.xml:
        files_in, files_out = load_input_xml(args)
        pipeline_xml(files_in, files_out, structure_words_list)
    else:
        data = read_files(args)

        data = structure_words_remover(data, structure_words_list)
        save_output(data, out_file)
