# RELISH Preprocessing
The RELISH preprocessing repository is responsible for managing processes related to obtaining and transforming Medline articles for utilization in software pipelines focused on dictionary-based Named Entity Recognition (NER), word embeddings and  document level embeddings targeting document-to-document relevance, similarity, and recommendations. The current functionality of the 'relish-preprocessing' involves processing a list of articles adhering to the RELISH format.

# Data input
[RELISH](https://academic.oup.com/database/article/doi/10.1093/database/baz138/5871485?login=false) is an expert-curated database designed for benchmarking document similarity in biomedical literature. The database v1 was downloaded from its corresponding [FigShare record](https://figshare.com/projects/RELISH-DB/60095) on the 24th of January 2022. It consists of a [JSON file](https://github.com/zbmed-semtec/relish-preprocessing/blob/main/data/input/RELISH_v1.json) with PubMed Ids (PMIDs) and the corresponding document-2-document relevance assessments wrt other PMIDs. Relevance is categorized as "relevant", "partial" or "irrelevant".

Please be aware that the files might not have been uploaded to the repository on the same date as they were initially downloaded.


# Process
The following section outlines the primary processes applied to the input data of the RELISH dataset.

### Retrieving PMID Articles
+ Iteration through articles in the RELISH JSON format using the [BioC API](https://www.ncbi.nlm.nih.gov/research/bionlp/APIs/BioC-PubMed/) to obtain XML files containing identifiers (PMIDs), titles, and abstracts. Refer to the provided [XML sample files](https://github.com/zbmed-semtec/relish-preprocessing/blob/main/data/output/sample-files/xml) for RELISH. It's also possible to retrieve this information from the bulk download from Medline using the JATS format.
+ Recording missing PMIDs, indicating PMIDs for which the retrieval process failed or whose title/abstract is not available as text. Refer to the list of [missing PMIDs]() for RELISH.
+ Creation of a TSV file with PMID, title and abstract. Review the [TSV sample file](https://github.com/zbmed-semtec/relish-preprocessing/blob/main/data/output/sample-files/tsv/documents_20220822.tsv) for RELISH.


### Generating Ground Truth Data: PMID Pairs and Relevance Labels
+ Creation of a [TSV file](https://github.com/zbmed-semtec/relish-preprocessing/blob/main/data/output/relish-ground-truth/RELISH.tsv) that serves as a reference dataset from the RELISH JSON file. It comprises of all pairs of PMIDs along with its corresponding relevance labeled as 0,1, or 2. These labels represent the levels of relevance, specifically "non-relevant", "partially-relevant", and "relevant" respectively. This structured file aids in establishing a reliable ground truth for further analysis and evaluation.

At this stage, we have Medline articles in two formats: XML and plain-text TSV. We use XML files for NER and the TSV file for word embedding and document embedding approaches.

### Text preprocessing for Generating Embeddings
For the purpose of generating embeddings, several cleaning and pruning steps are undertaken. The following outlines the cleaning processes applied to the XML and TSV files:

+ Removal of "structural expressions" within abstracts. Certain expressions, such as "Results:" and "Methodology:" recommended by journals for structured abstracts, are removed from the text to avoid introducing noise to the embeddings.
    + Initial analysis of the text to identify the most common "structural words." and creation of a [plain-text file](https://github.com/zbmed-semtec/relish-preprocessing/blob/main/data/output/structure-words/structure_word_list_pruned.txt) and a [JSON file](https://github.com/zbmed-semtec/relish-preprocessing/blob/main/data/output/structure-words/structure_word_list.json) containing these common "structural words."
+ Additional common steps for word embeddings include:
    + Converting all text to lowercase.
    + Eliminating punctuation marks (excluding hyphens, as hyphenated words might carry a distinct meaning).
    + Removal of special characters.
    + Tokenization.
    + Stopwords removal.

After performing the proposed cleaning, the retrieved articles in TSV format are saved as a NumPy array. A sample of the [processed TSV file](https://github.com/zbmed-semtec/relish-preprocessing/blob/main/data/output/relish-preprocessed-text/RELISH_documents_pruned.tsv) and the [numPy arrays](https://github.com/zbmed-semtec/relish-preprocessing/blob/main/data/output/relish-preprocessed-text/RELISH_Tokenized.npy) are available for RELISH.

# Code Implementation
Code scripts for the following processes can be found here:
+ [Retrieving PMID Articles](https://github.com/zbmed-semtec/relish-preprocessing/blob/main/code/bioc-approach/bioc_api_retrieval.py)
+ [Generating Ground Truth: TSV file](https://github.com/zbmed-semtec/relish-preprocessing/blob/main/code/data-preprocessing/pmid_retrieval.py)
+ [Removal of Structural words](https://github.com/zbmed-semtec/relish-preprocessing/blob/main/code/structure-words-removal/structurewords_remover.py)
+ [Text Preprocessing](https://github.com/zbmed-semtec/relish-preprocessing/blob/main/code/data-preprocessing/preprocessing.py)

# Data output
The output files generated by the complete RELISH preprocessing pipeline include:

+ A RELISH TSV file consisting of three columns [PMIDs | title | abstract] used for downstream preprocessing. 
+ Individual RELISH XML files (one per each PubMed article).
+ A processed RELISH.npy file where each row is a listof three numpy arrays representing the PMID, tokenized title, and tokenized abstract of a document.  
+ RELISH ground truth TSV file with three columns [Reference PMID | Assessed PMID | Relevance score (0,1 or 2)].


# Tutorials
Tutorials are accessible in the form of Jupyter notebooks for the following processes:

+ [Retrieving PMID Articles](https://github.com/zbmed-semtec/relish-preprocessing/tree/main/docs/data-retrieval)
+ [Removal of Structural words](https://github.com/zbmed-semtec/relish-preprocessing/tree/main/docs/structure_words_removal)
+ [Text Preprocessing](https://github.com/zbmed-semtec/relish-preprocessing/tree/main/docs/phrase_preprocessing_tutorial)