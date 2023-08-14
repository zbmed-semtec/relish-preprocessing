import csv
import logging
import re
import sys
import spacy
import numpy as np
from nltk import download
from nltk.corpus import stopwords

# Download using "pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.0/en_core_sci_lg-0.5.0.tar.gz"
nlp = spacy.load("en_core_sci_lg")  # Scispacy model en_core_sci_lg

def get_entities(doc):
    '''
    Retrieves entities from a sequence of ScispaCy Token objects.

    Parameters
    ----------
    doc: spacy.tokens.doc.Doc
        Sequence of Token objects from ScispaCy.
    Returns
    -------
    ents: list
        A list of identified entities.
    '''
    ents = list(doc.ents)

    return ents

def get_tokens(text):
    '''
    Tokenize the text.

    Parameters
    ----------
    text: str
        Plain text that is to be tokenized.
    Returns
    -------
    tokens: list
        A list of tokens.
    '''
    tokens = []
    doc = nlp(text)

    # Get entities in the text
    text_ents = get_entities(doc)

    # Keep track of entity counts
    ent_count = 0
    for token in doc:
        # Check if the token is the boundary part of an entity
        if str(token.ent_iob_) == "B":
            ent = str(text_ents[ent_count])

            string_list = ent.split()
            tokens += string_list

            ent_count += 1

        # Skip if the token is the inside part of an entity
        elif str(token.ent_iob_) == "I":
            continue

        # Add to the list of tokens all those words outside the entity
        else:
            tokens.append(token)

    return tokens

def preprocessPhrases(filepathIn=None, filepathOut=None):
    '''
    Transforms TREC and RELISH tsv file to lowercase and removes all special characters aside from the hyphen.
    Saves transformed TREC and RELISH files as an .npy format as a multi-dimensional array.

    Parameters
    ----------
    filepathIn: str
        The input file for the RELISH or TREC tsv to be transformed.
    '''
    if not isinstance(filepathIn, str):
        logging.warn("Wrong parameter type for preprocessPhrases.")
        sys.exit("filepathIn needs to be of type string")
    elif not isinstance(filepathOut, str):
        logging.warn("Wrong parameter type for preprocessPhrases.")
        sys.exit("filepathOut needs to be of type string")
    else:
        letters_pattern = '.*[a-zA-Z\d\-].*' #Includes all letters which are numbers, letters or a hyphen.
        outputList = []
        with open(filepathIn) as input:
            inputFile = csv.reader(input, delimiter="\t")
            headerline = True
            for line in inputFile:
                if(headerline):
                        headerline = False
                else:
                    title = get_tokens(line[1].lower())
                    abstract = get_tokens(line[2].lower())
                    iteration = 0
                    while(iteration < len(title)):
                        word = "".join([c for c in str(title[iteration]) if re.match(letters_pattern, c)])
                        title[iteration] = word
                        iteration += 1
                    iteration = 0
                    while(iteration < len(abstract)):
                        word = "".join([c for c in str(abstract[iteration]) if re.match(letters_pattern, c)])
                        abstract[iteration] = word
                        iteration += 1
                    iteration = 0
                    cleanedTitle = []
                    for word in title:
                        if word != "":
                            cleanedTitle.append(word)
                    cleanedAbstract = []
                    for word in abstract:
                        if word != "":
                            cleanedAbstract.append(word)
                    outputList.append([np.asanyarray(line[0]), np.asanyarray(cleanedTitle), np.asanyarray(cleanedAbstract)])
            np.save(filepathOut, np.asanyarray(outputList))