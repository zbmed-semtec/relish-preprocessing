import xml.etree.cElementTree as et
from xml.etree.ElementTree import Element, SubElement
from xml.etree.ElementTree import ElementTree 
from bs4 import BeautifulSoup
import pandas as pd
import sys
import requests
import re
import glob
import logging
import os
from shutil import rmtree
from tqdm.notebook import tqdm, trange
from multiprocessing import Pool, freeze_support
from datetime import date

def requestAPI(pmid_chunk, filename):
    '''
    Function to request XML data from ncbi RESTful API and safe it to './data/xml-files/chunk-xml'.
    
    Input:  pmid_chunk ->  List of pmids that get requested per request (maximum 400).
            filename -> The filename of the output xml.
    Output: xml-file named './data/{project}/xml-files/{pmid}.xml'
    '''
    if not isinstance(pmid_chunk, list):
        logging.error("Wrong parameter type for requestAPI, pmid_chunk.")
        sys.exit("pmid_chunk needs to be of type List")
    elif len(pmid_chunk) > 400:
        logging.error("Illegal parameter input for requestAPI, pmid_chunk.")
        sys.exit("len(pmid_chunk) must not be higher than 400.")
    elif not isinstance(filename, str):
        logging.error("Wrong parameter type for requestAPI, filename.")
        sys.exit("filepath needs to be of type String")
    pmid_string = ''
    for id in pmid_chunk:
        string = f'{id}|'
        pmid_string += string
    try:
        url = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pubmed.cgi/BioC_xml/{pmid_string}/unicode"
        resp = requests.get(url)
        xml_data = BeautifulSoup(resp.content, 'xml')
        with open(filename, 'w') as f:
            f.write(xml_data.prettify())
        logging.info(f'Finished and saved to: {filename}')
    except Exception:
        logging.error("API Request couldn't be made.", exc_info=True)

def chunk_requestAPI(pmidList, outputFolder, chunk_size=400, processes=30, **kwargs):
    '''
    Function to chunk the pmidList and run requestAPI in parallel.
    Input:  pmidList -> List of pmids to be retrieved.
            outputFolder -> Directory with the output formatted xml files.
            chunk_size -> Number of pmids per request.
            processes -> Number of parallel processes.
    '''
    if not isinstance(chunk_size, int):
        logging.error("Wrong parameter type for chunk_requestAPI, chunk_size.")
        sys.exit("chunk_size needs to be of type Integer")
    elif chunk_size > 400:
        logging.error("Illegal parameter input for chunk_requestAPI, chunk_size.")
        sys.exit("len(chunk_size) must not be higher than 400.")
    elif processes > 30:
        logging.warning('''Number of processes is very high. This might lead to system overload. 
                            We recommend to use a maximum of 30 processes.''')
    elif not isinstance(outputFolder, str):
        logging.error("Wrong parameter type for chunk_requestAPI, outputFolder.")
        sys.exit("filepath needs to be of type String")
    
    pmidList_chunked = [pmidList[i:i + chunk_size] for i in range(0, len(pmidList), chunk_size)] 
    output_filenames = [f'{outputFolder}/chunk-{pmidList_chunked.index(pmid_chunk)}.xml' for pmid_chunk in pmidList_chunked]
    arguments = list(zip(pmidList_chunked, output_filenames)) 
    try:
        freeze_support()
        with Pool(processes) as p:
            p.starmap(requestAPI, arguments)
    except Exception:
        logging.error("Multiple API request couldn't be made.", exc_info=True)

def createXML(document, filename):
    '''
    Function to create an xml file from a document object. 
    Iterates through all elements in the document object and passes xml tags, attributes, text and tails.
    
    Input:  filename -> String: The filename of the output xml.
            document -> xml Element Object: Containing the content of the resulting xml
    Output: written xml-file based on the filename defined.
    '''
    if not isinstance(filename, str):
        logging.error("Wrong parameter type for createXML.")
        sys.exit("filename needs to be of type String")
    else:
        try:
            new_root = Element('collection', {})
            new_root.text = '\n '
            tree = ElementTree(new_root)
            var = SubElement(new_root, document.tag, attrib=document.attrib)
            var.text = document.text
            var.tail = document.tail
            for element in document:
                var_1 = SubElement(var, element.tag, attrib=element.attrib)
                var_1.text = element.text
                var_1.tail = element.tail
                for subelement in element:
                    var_2 = SubElement(var_1, subelement.tag, attrib=subelement.attrib)
                    var_2.text = subelement.text
                    var_2.tail = subelement.tail
            with open(filename, 'wb') as f:
                tree.write(f, encoding='utf-8', xml_declaration=True)
        except Exception:
            logging.error("Error in createXML.", exc_info=True)

def processPMID(inputPath, outputPath):
    '''
    Function to retrieve [PMID, Title and Abstract] from chunked XML-files.
    
    Input:  inputPath -> Directory with the chunked xml files.
            outputPath -> Directory with the output formatted xml files.
    Output: Returns pandas.DataFrame(columns=['PMID', 'title', 'abstract']) for retrieved pmids
            and pandas.DataFrame(columns=['PMID', 'reason']) for missing pmids
    '''
    if not isinstance(inputPath, str):
        logging.error("Wrong parameter type for processPMID, inputPath.")
        sys.exit("inputPath needs to be of type String")
    elif not isinstance(outputPath, str):
        logging.error("Wrong parameter type for processPMID, outputPath.")
        sys.exit("outputPath needs to be of type String")
    else:
        pubmedData_df = pd.DataFrame(columns=['PMID', 'title', 'abstract'], dtype=object)
        skipped_pmids = []
        try:
            xml_files = glob.glob(inputPath+'/*.xml', recursive=True)
        except Exception:
            logging.error("InputPath is not valid.", exc_info=True)
        pubmedData_df = pd.DataFrame(columns=['PMID', 'title', 'abstract'], dtype=object)
        doc_dicts = []
        logging.info(f'Processing {len(xml_files)} chunk files.')
        for i in trange(len(xml_files)): # iterate through all chunk-{i}.xml files
            xml_file = xml_files[i]
            root = et.parse(xml_file).getroot() 
            for document in root.findall('document'):
                element_lst = [element.tag for element in document.iter()]
                document_dict = {}
                for id in document.findall('id'):
                    pmid = re.sub(r"\n+", "", id.text)
                    pmid = pmid.strip(' ')
                if element_lst.count('passage') == 2:
                    if element_lst.count('text') == 2: 
                        document_dict['PMID'] = pmid
                        outputFilename = f'{outputPath}/{pmid}.xml'
                        if not os.path.exists(outputFilename):
                            try:
                                createXML(document, outputFilename)
                            except Exception:
                                logging.error("OutputPath is not valid.", exc_info=True)
                        else:
                            #logging.info('File already exists.')
                            pass
                        for passage in document.findall('passage'):
                            infon = re.sub(r"\n+\s+", "", passage.find('infon').text)
                            if infon == 'title':
                                title = passage.find('text').text
                                title = re.sub(r"\n+", "", title)
                                title = title.strip(' ')
                                document_dict['title'] = str(title)
                            if infon == 'abstract':
                                abstract = passage.find('text').text
                                abstract = re.sub(r"\n+", "", abstract)
                                abstract = abstract.strip(' ')
                                document_dict['abstract'] = str(abstract)
                        doc_dicts.append(document_dict)
                        doc_df = pd.DataFrame(doc_dicts)
                    else:
                        skipped_pmids.append(pmid)
                        #logging.info(f'Only one <text> tag found. Either title or abstract is missing. Skipping PMID {pmid}...')
                        continue
                else:
                    skipped_pmids.append(pmid)
                    #logging.info(f'Only one <passage> tag found. Either title or abstract is missing. Skipping PMID {pmid}...')
                    continue
        try:
            pubmedData_df = pd.concat([pubmedData_df, doc_df], axis=0, ignore_index=True)
        except:
            skipped_pmids.append(pmid)
            logging.error('Error while processing PMIDs.')
        return pubmedData_df, skipped_pmids

def main(pmidList, parentPath, log=False, delete_tmp=False, **kwargs):
    '''
    Main function that runs processPMID on the retrieved xml files and compares it to the pmidList input.
    Input:  pmidList -> List of pmids to be retrieved.
            inputPath -> Directory with the chunked xml files.
            outputPath -> Directory with the output formatted xml files.
    '''
    if log:
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
    logging.info('Started script.')
    try:
        today = date.today().strftime("%Y%m%d")
        logging.info(f'Number of PMIDs to process: {len(pmidList)}')
        chunkPath = f'{parentPath}/temp/chunk-xml'
        pmidPath = f'{parentPath}/temp/pmid-xml'
        os.makedirs(chunkPath, exist_ok=True)
        os.makedirs(pmidPath, exist_ok=True)
        chunk_requestAPI(pmidList, chunkPath, **kwargs)

        # Initiate processPMID function to retrieve abstracts and titles
        pubmedData_df, skipped_pmids = processPMID(chunkPath, pmidPath)
        pubmedData_df.sort_values('PMID').to_csv(f'{parentPath}/documents_{today}.tsv', sep='\t', index=False, quotechar="`")
        logging.info(f'Titles, abstracts and pmids saved to tsv file (Path: {parentPath}/documents_{today}.tsv).')
        
        # Check missing pmids
        missing_pmids = [str(pmid) for pmid in pmidList if str(pmid) not in pubmedData_df['PMID'].to_list()]
        if len(missing_pmids) > 0:
            logging.info(f'Missing PMIDs: {len(missing_pmids)}')
            logging.info(f'Missing due to no title or abstract: {len(skipped_pmids)}')
            logging.info(f'Probably missing due to non-existing API entry: {len([str(pmid) for pmid in missing_pmids if str(pmid) not in skipped_pmids])}')
            missing_pmids_df = pd.DataFrame({'PMID':missing_pmids, 'Reason': ''})
            no_api_entry = [str(pmid) for pmid in missing_pmids if str(pmid) not in skipped_pmids]
            for pmid in missing_pmids:
                if pmid in skipped_pmids:
                    missing_pmids_df.loc[missing_pmids_df.PMID == pmid, 'Reason'] = 'No title or abstract'
                elif pmid in no_api_entry:
                    missing_pmids_df.loc[missing_pmids_df.PMID == pmid, 'Reason'] = 'No API entry'
                else:
                    missing_pmids_df.loc[missing_pmids_df.PMID == pmid, 'Reason'] = 'Unknown'
            missing_pmids_df.to_csv(f'{parentPath}/missing_{today}.tsv', sep='\t', index=False, quotechar="`")
            logging.info(f'Missing pmids saved to tsv file (Path: {parentPath}/missing_{today}.tsv).')
        else:
            logging.info('All titles and abstracts successfully retrieved.')
        if delete_tmp:
            rmtree(f'{parentPath}/temp')
        logging.info('Finished script.')
    except Exception:
        logging.error("Error in main function.", exc_info=True)
