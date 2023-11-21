import argparse
import numpy as np
import nltk
from nltk.corpus import stopwords

def prepare_from_npy(filepath_in: str, filepath_out: str):
    '''
    Removes stopwords for the tokenized npy file format, as an optional step in preprocessing.

    Parameters
    ----------
    filepath_in: str
        The filepath of the RELISH input npy file.
    filepath_out: str
        The filepath of the RELISH output npy file.
    '''
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))
    doc = np.load(filepath_in, allow_pickle=True)
    for line in doc:
        line[1] = [w for w in line[1] if not w in stop_words]
        line[2] = [w for w in line[2] if not w in stop_words]
    np.save(filepath_out, doc, allow_pickle=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", type=str,
                       help="Path to input tokenized NPY file")
    parser.add_argument("-o", "--output", type=str,
                       help="Path to output tokenized NPY file")
    args = parser.parse_args()

    prepare_from_npy(args.input, args.output)
