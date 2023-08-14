import os
import csv
import sys
import pathlib
import logging
from io import StringIO
from html.parser import HTMLParser
import xml.etree.cElementTree as ET

def structureDataset(pmidSet, inputDirectoryXML, outputDirectoryXML, outputFilepathTSV):
    '''
    Takes metadata from the pubmed FTP data set 'ftp.ncbi.nlm.nih.gov/pubmed/baseline' which match with the given pmid from the pmid set,
    writes it onto an xml file as well as a tsv file containing the article's pmid, title and abstract.
    
    Input:  pmidSet             ->  set: A set of pubmed ids.
            inputDirectoryXML   ->  string: The directory in which the XML files retrieved from the FTP server are located.
            outputDirectoryXML  ->  string: The output directory of the resulting individual xml files within two directories.
                                            Original: The original xml data copied directly from the FTP server
                                            Formatted: XML data only contains plaintext pmid, title and abstract where any HTML notations have been removed.
            outputFilepathTSV   ->  string: The output filepath of the resulting tsv file,
                                            results in a single tsv file containing all given pmids with their respective titles and abstracts.
    '''
    if not isinstance(pmidSet, set):
        logging.alert("Wrong parameter type for structureDataset.")
        sys.exit("pmidSet needs to be of type set")
    elif not isinstance(inputDirectoryXML, str):
        logging.alert("Wrong parameter type for structureDataset.")
        sys.exit("inputDirectoryXML needs to be of type string")
    elif not isinstance(outputFilepathTSV, str):
        logging.alert("Wrong parameter type for structureDataset.")
        sys.exit("outputDirectoryTSV needs to be of type string")
    elif not isinstance(outputDirectoryXML, str):
        logging.alert("Wrong parameter type for structureDataset.")
        sys.exit("outputDirectoryXML needs to be of type string")
    else:
        #MLStripper and strip_tags taken from https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python/925630#925630
        try:
            class MLStripper(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.reset()
                    self.strict = False
                    self.convert_charrefs= True
                    self.text = StringIO()
                def handle_data(self, d):
                    self.text.write(d)
                def get_data(self):
                    return self.text.getvalue()
            def strip_tags(html):
                s = MLStripper()
                s.feed(html)
                return s.get_data()
        except:
            logging.error("Couldn't strip HTML tags.")

        try:
            if not os.path.exists(f'{outputDirectoryXML}/Original'):
                os.makedirs(f'{outputDirectoryXML}/Original')
            if not os.path.exists(f'{outputDirectoryXML}/Formatted'):
                os.makedirs(f'{outputDirectoryXML}/Formatted')
            for path in pathlib.Path(inputDirectoryXML).iterdir():
                if path.is_file():
                    prevprevline = ''
                    prevline = ''
                    entry = ''
                    found = False
                    for line in open(path, encoding='UTF8'):
                        if line.startswith("      <PMID"):
                            value = int(line.partition('>')[2].partition('<')[0])
                            if(int(value) in pmidSet):
                                found = True
                                entry += prevprevline
                                entry += prevline
                                entry += line
                        elif found:
                            entry += line
                            if "</PubmedArticle>" in line:
                                with open(f'{outputDirectoryXML}/Original/{(int)(value)}.xml', 'w', encoding='UTF8') as f:
                                    f.write(entry)
                                prevprevline = ''
                                prevline = ''
                                entry = ''
                                found = False
                        else:
                            prevprevline = prevline
                            prevline = line
        except:
            logging.error("outputDirectoryXML is invalid.")
            return None

        header = ['PMID', 'title', 'abstract']
        try:
            with open(outputFilepathTSV, 'w', encoding='UTF8') as output:
                writer = csv.writer(output, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar=' ')
                writer.writerow(header)
                for path in pathlib.Path(f'{outputDirectoryXML}/Original').iterdir():
                    if path.is_file():
                        pmid = None
                        title = None
                        abstract = None
                        for line in open(path, encoding='UTF8'):
                            if line.startswith("      <PMID"):
                                pmid = line.partition('>')[2].partition('</PMID')[0]
                            elif line.startswith("        <ArticleTitle"):
                                title = line.partition('>')[2].partition('</ArticleTitle')[0]
                            elif line.startswith("          <AbstractText Label="):
                                category = line.partition('Label="')[2].partition('\"')[0]
                                abstractText = line.partition('>')[2].partition('</AbstractText')[0]
                                if(abstract == None):
                                    abstract = f"{category}: {abstractText}"
                                else:
                                    abstract += f" {category}: {abstractText}"
                            elif line.startswith("          <AbstractText>"):
                                if(abstract == None):
                                    abstract = line.partition('>')[2].partition('</AbstractText')[0]
                                else:
                                    abstract += line.partition('>')[2].partition('</AbstractText')[0]
                        if(pmid != None and title != None and abstract != None):
                            collection = ET.Element("collection")
                            ET.SubElement(collection, "source").text = "PubMed"
                            ET.SubElement(collection, "key").text = "collection.key"
                            document = ET.SubElement(collection, "document")
                            ET.SubElement(document, "id").text = pmid
                            passageTitle = ET.SubElement(document, "passage")
                            ET.SubElement(passageTitle, "infon", key="type").text = "title"
                            title = strip_tags(title)
                            abstract = strip_tags(abstract)
                            ET.SubElement(passageTitle, "text").text = title
                            passageAbstract = ET.SubElement(document, "passage")
                            ET.SubElement(passageAbstract, "infon", key="type").text = "abstract"
                            ET.SubElement(passageAbstract, "text").text = abstract
                            tree = ET.ElementTree(collection)
                            tree.write(f'{outputDirectoryXML}/Formatted/{pmid}.xml', encoding='UTF8')
                            writer.writerow([pmid,title,abstract])
        except:
            logging.error("Could not create tsv and xmls.")
            return None