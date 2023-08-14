import pandas as pd
import sys
import logging
import json
import os

def parseRelish(filepath):
    '''
    Function to create a list of all pmids included in the RELISH json file
    and removes its duplicates.

    Input:  filepath -> String: Filepath to the RELISH json file
            i.e. "RELISH/data/RELISH.json".
    Output: A set contaning a pmid for each row.

    Developer notice: Since the amount of entries would increase drastically,
    the associated pmids to each pmid were not included and commented out.
    '''
    if not isinstance(filepath, str):
        logging.alert("Wrong parameter type for parseRELISH.")
        sys.exit("filepath needs to be of type String")
    else:
        try:
            with open(filepath) as data_file:    
                data = json.load(data_file)
                df = pd.DataFrame({})
                for entry in data:
                    ref_df = pd.DataFrame({})
                    pmid = entry['pmid']
                    response = entry['response']
                    for relevance in response:
                        if relevance == 'relevant':
                            relevant_df = pd.DataFrame({'assess_pmid':response['relevant']})
                            relevant_df['ref_pmid'] = pmid
                            relevant_df['relevance'] = 2
                        elif relevance == 'partial':
                            partial_df = pd.DataFrame({'assess_pmid':response['partial']})
                            partial_df['ref_pmid'] = pmid
                            partial_df['relevance'] = 1
                        elif relevance == 'irrelevant':
                            irrelevant_df = pd.DataFrame({'assess_pmid':response['irrelevant']})
                            irrelevant_df['ref_pmid'] = pmid
                            irrelevant_df['relevance'] = 0
                    ref_df = pd.concat([relevant_df, partial_df, irrelevant_df], ignore_index=True)
                    ref_df = ref_df[['ref_pmid', 'assess_pmid', 'relevance']]
                    df = pd.concat([df, ref_df], ignore_index=True)
            # Delete duplicates where assessment is the same. Keep first instance.
            df = df.drop_duplicates(subset=['ref_pmid', 'assess_pmid', 'relevance'], keep='first')
            # Delete remaining duplicates where pmid and assess_pmid is the same but not the assessment. Keep non of them.
            duplicates = df.loc[df.duplicated(subset=['ref_pmid', 'assess_pmid'], keep=False),]
            duplicates.to_csv(f'{os.path.dirname(filepath)}/RELISH_duplicates.tsv', sep='\t', index=False)
            df = df.drop_duplicates(subset=['ref_pmid', 'assess_pmid'], keep=False)
            # Save tsv to input folder
            df.to_csv(f'{os.path.dirname(filepath)}/RELISH.tsv', sep='\t', index=False, header=False)
            # Create tsv with alternative assessment !!!!!! FOR INTERNAL USE ONLY !!!!!!
            # df_alternate = df.copy()
            # df_alternate['relevance'] = df_alternate['relevance'].apply(lambda x: 1 if (x == 2) | (x == 1) else 0)
            # df_alternate.to_csv(f'{os.path.dirname(filepath)}/RELISH_alternative.tsv', sep='\t', index=False, header=False)
            # Create a list of all pmids for further processing
            pmidList = df['assess_pmid'].tolist()
        except Exception:
            logging.error("Input file directory not found.", exc_info=True)
        return set(pmidList)

def parseTREC(filepath):
    '''
    Function to create a list of all pmids included in the TREC tsv file
    and removes its duplicates.

    Input:  filepath -> String: Filepath to the TREC tsv file
            i.e. './TREC/data/TREC.tsv'.
    Output: A set contaning a pmid for each row.
    '''
    if not isinstance(filepath, str):
        logging.alert("Wrong parameter type for parseTREC.")
        sys.exit("filepath needs to be of type String")
    else:
        try:
            TREC_data = pd.read_table(filepath, names=['topic_id', 'zeros', 'pmid', 'relevance'])
            pmidSet = set(TREC_data['pmid'])
        except Exception:
            logging.error("Input file directory not found.", exc_info=True)
        return pmidSet