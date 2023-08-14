# Structure words removal

The following script is used to generate a list of common structure words that appear in the articles' abstract. These structure words are words or groups of words followed by a colon, most likely required by the journals. Since they do not provide any meaningful information to the text, they should be removed.

Some examples of these structure words are "BACKGROUND:", "CONCLUSIONS:", "METHODS:", etc.

The regular expression that matches these structure words follows:

* The word/group of words should be at least 3 characters long and at most 70.

* The word/group of words must be at the start of a sentence.

* The word/group of words must be followed by a colon and an empty space ": ".

# Prerequisites

1. A TSV file which contains an abstract column. The file can be generated following instructions [here](https://github.com/zbmed-semtec/medline-preprocessing/blob/main/docs/BioC_API_Tutorials/tutorial_RELISH.ipynb)
2. (Optional) A list of structure words. If you already have one, you can skip steps 2 and 3.

# Steps

## Step 1: Imports

Import the necessary packages and files to run the script:


```python
import sys
import pandas as pd
import glob

sys.path.append('../../code/Structure_Words_removal/')

import structurewords_remover as SW_rem
import structurewords_list_generator as SW_lg

```

## Step 2: Loading the data (Optional)

Load the input `.TSV` files from which the structure words list will be generated. You can either input a file itself or a directory containing several files:


```python
in_files = ["../../data/RELISH/RELISH_documents.tsv",
            "../../data/TREC/TREC_documents.tsv"]

input_dir = "../../data/"
in_files = glob.glob(f"{input_dir}/*.tsv")

df_list = []
for file in in_files:
    df_list.append(pd.read_csv(file, sep="\t", quotechar="`"))
data = pd.concat(df_list, axis=0, ignore_index=True)

```

## Step 3: Generate the list (Optional)

Generate the structure word list. In order to avoid false positives from the algorithm (removing words that can be relevant but follow the regular expression), it is advised to input either a minimum relative frequency of appearance or a minimum number of total appearances:


```python
structure_words = SW_lg.structure_words_pipeline(
    data, ratio_threshold=0, occurrences_threshold=0)

```

The list can be pruned afterwards:


```python
structure_words_pruned = SW_lg.prune_structure_words(
    structure_words, ratio_threshold=0.0001, occurrences_threshold=10)

print(f"Total number of structure words matched: {len(structure_words)}")
print(
    f"Total number of structure words after pruning: {len(structure_words_pruned)}")

```

    Total number of structure words matched: 10362
    Total number of structure words after pruning: 241


The list can be stored either as plain words or with some extra information like the relative frequency and the total occurrences. It is recommended to manually check the list in order to identify if some false positives made through the cut, but with a reasonable threshold, the effects of a few false positives should be negligible.


```python
SW_lg.export_to_list("structure_word_list.txt", structure_words_pruned)
SW_lg.export_to_list("../../data/Structure_Words_removal/structure_word_list_pruned.txt", structure_words_pruned)
SW_lg.export_to_json("../../data/Structure_Words_removal/structure_word_list.json", structure_words)
```

## Step 4: Load the list

Once you are sure that the list of structure words are ready to be removed from the abstract, you can either read the list from the file or convert the current variable to a suitable format


```python
structure_words_list = SW_rem.read_list("structure_word_list.txt")

#structure_words_list = SW_lg.convert_to_list(structure_words_pruned)
```

If the loaded list is in `.json` format and have the extra information of the structure words, the list can be pruned afterwards:


```python
structure_words = SW_rem.read_json("../../data/Structure_Words_removal/structure_word_list.json")

structure_words_pruned = SW_lg.prune_structure_words(structure_words, ratio_threshold=0.0001)
structure_words_list = SW_lg.convert_to_list(structure_words_pruned)
```

## Step 5: Removing the structure words

Once the list of structure words is ready, you can remove them from the abstract by loading a `.tsv` file and running `structure_words_remover()`. Save the data in the desired output file.


```python
input_file = "../../data/RELISH/RELISH_documents.tsv"
output_file = "../../data/RELISH/RELISH_documents_pruned.tsv"

data = pd.read_csv(input_file, sep="\t", quotechar="`")

data_pruned = SW_rem.structure_words_remover(data, structure_words_list)

data_pruned.to_csv(output_file, sep="\t", quotechar="`", index=False)
```

It is also possible to remove structure words from XML files. Given a directory path, two lists containing the input and output files are created. You can the run the `pipeline_xml` function to remove the structure words:


```python
%%script false --no-raise-error
import glob
import os

input_path = "../../data/RELISH/xml-files/pmid-xml/"
output_path = "../../data/RELISH/xml-files/pmid-xml_no_structure_words/"

if not os.path.isdir(output_path): os.mkdir(output_path)

# It is a directory:
input_files = glob.glob(input_path + "/*.xml")
output_files = list(map(lambda x: x.replace(input_path, output_path), input_files))

SW_rem.pipeline_xml(input_files, output_files, structure_words_list)
```

The output XML files are in the  `data/RELISH/xml-files/pmid-xml_no_structure_words` directory.

# Other options

## Generate the list from the script

The code files are prepared to work on their own given some parameters. In order to execute the structure words list generator script, run the following command:

```bash
python structurewords_list_generator.py [-h] (-i INPUT | -d INDIR) [-o OUTPUT] [--ratio_threshold RATIO_THRESHOLD] [--occurrences_threshold OCCURRENCES_THRESHOLD]
```

You must pass one of the following arguments:

* -i / --input: path to TSV file with the data.

* -d / --indir: path to directory containing the TSV files with the data.

Optionally, you can pass the following arguments:

* -o / --output: path to the output structure words list.

* --ratio_threshold: minimum relative frequency of appearance to be saved.

* --occurrence_threshold: minimum number of total appearances to be saved.

An example of the command that will create the files `structure_word_list.txt`, `structure_word_list.json` (one containing the list itself and the other containing other relevant information of the structure words selected):

```bash
python structurewords_list_generator.py --input ../../data/RELISH/RELISH_documents.tsv --ratio_threshold 0.0001
```

## Remove the structure words from the script

The code files are prepared to work on their own given some parameters. In order to execute the structure words removal script, run the following command:

```bash
python structurewords_remover.py [-h] [-i INPUT | -d INDIR] -l LIST [-o OUTPUT]
```

You must pass one of the following arguments:

* -i / --input: path to TSV file with the data.

* -d / --indir: path to directory containing the TSV files with the data.

Optionally, you can pass the following arguments:

* -o / --output: path to the output pruned file.

* -l / --list: path to the file generated from the structurewords_list_generator script that contains the structure word list.

An example of the command that will create a pruned `.tsv`:

```bash
python structurewords_remover.py --input ../../data/RELISH/RELISH_documents.tsv --list structure_word_list.txt --output RELISH_documents_pruned.tsv
```

The script can also remove structure words from XML files, however, it is recommended to input `.tsv` files with a dedicated `abstract` column per publication. In order to execute the script for XML files, input a file or a directory containing XML files, a output file/directory (defaults to file/directory name plus `_no_structure_words`) and set the `--xml` tag to 1.

```bash
python structurewords_remover.py --indir ../../data/RELISH/xml-files/pmid-xml/ --list ../../data/Structure_Words_removal/structure_word_list_prunned.txt
```

The output XML files are in the  `data/RELISH/xml-files/pmid-xml_no_structure_words` directory.


# Results

Example of structure words removal:

<table>
<tr>
<th>Abstract Input</th>
<th>Abstract Output</th>
</tr>
<tr>
<td width="50%">
<mark>OBJECTIVE: </mark>To describe the development of evidence-based electronic prescribing (e-prescribing) triggers and treatment algorithms for potentially inappropriate medications (PIMs) for older adults. <mark>DESIGN: </mark>Literature review, expert panel and focus group. <mark>SETTING: </mark>Primary care with access to e-prescribing systems. <mark>PARTICIPANTS: </mark>Primary care physicians using e-prescribing systems receiving medication history. <mark>INTERVENTIONS: </mark>Standardised treatment algorithms for clinicians attempting to prescribe PIMs for older patients. <mark>MAIN OUTCOME MEASURE: </mark>Development of 15 treatment algorithms suggesting alternative therapies. <mark>RESULTS: </mark>Evidence-based treatment algorithms were well received by primary care physicians. Providing alternatives to PIMs would make it easier for physicians to change decisions at the point of prescribing. <mark>CONCLUSION: </mark>Prospectively identifying older persons receiving PIMs or with adherence issues and providing feasible interventions may prevent adverse drug events.
</td>
<td width="50%">
To describe the development of evidence-based electronic prescribing (e-prescribing) triggers and treatment algorithms for potentially inappropriate medications (PIMs) for older adults. Literature review, expert panel and focus group. Primary care with access to e-prescribing systems. Primary care physicians using e-prescribing systems receiving medication history. Standardised treatment algorithms for clinicians attempting to prescribe PIMs for older patients. Development of 15 treatment algorithms suggesting alternative therapies. Evidence-based treatment algorithms were well received by primary care physicians. Providing alternatives to PIMs would make it easier for physicians to change decisions at the point of prescribing. Prospectively identifying older persons receiving PIMs or with adherence issues and providing feasible interventions may prevent adverse drug events.
</td>
</tr>
</table>

# Decision notes

## Code strategy:

1. Using a regular expression (`r"(?:^[\s]*|\.|\?|: )(?: *)(?=([A-Z]+[A-Z\s&a-z]{2,69}:\s))"`), find all matches in the input abstracts. Add the matches to a dictionary and keep track of how many times each match is found.

2. The dictionary with `{word: counts}` is converted into a list of dictionaries that stores the word, the total occurrences, and the relative frequency (total occurrences divided by total number of articles): `[{word: _, occurrences: _, ratio_of_occurrences: occurrences/len(data)}, ...]`

3. The list is pruned by both the total occurrences or the relative frequency. Thus, most words that only appear a few times will not be removed in order to avoid false positives. A recommended minimum relative frequency is 0.0001.

4. Save the list into a text format document to be read by the remover program and to allow humans to manually inspect it.

5. To remove the structure words from the abstract:

    5.1 The first step is to divide the structure word list in those that match the regular expression and those that not. If the user has added custom structure words, they might not follow the pattern.

    5.2 Loop through every abstract and match the same regular expression used to generate the structure words.

    5.3 For every match, check if the word is in the structure words removal list, and save the starting and ending position of the match.

    5.4 The last step is to extract the characters contained between the starting and ending position of each match, leaving behind the abstract without the desired structure words.

    5.5 For every structure word in the non-matched list, remove it from the abstract. We cannot use a regular expression in this case.

6. Save the pruned file into a `.tsv`.

## Decisions:

* Why to split the procedure in "generating the structure word list" and "removing the structure words"? 

    To generate the list, the user has to input as many articles as possible in order to have a more complete list. Once the list is generated, if new articles are added to the pipeline, it is not necessary to run the list generator algorithm again. Thus, I believe that splitting the two processes allows for a faster deployment of new data.

* Why is this process not integrated in the pre-process pipeline, like lower case everything or stopword removal?

    Most of the other pre-process techniques requires previous tokenization or splitting of words. This is different. The structure words require both the period and colon punctuations to identify them, and some structure words can be composed of several words (like "MAIN OUTCOME MEASURES: "). I think the process is different enough for it to have each own pipeline.

    Also, this process should be common in every approach (including [whatizit-dictionary-ner](https://github.com/zbmed-semtec/whatizit-dictionary-ner)), so creating a modified `.tsv` file facilitates its integration.

* In the algorithm to remove the structure words, why to split the structure words in those that matched the regular expression and those that don't?

    For efficiency. Most of the structure words are going to follow the regular expression, and removing them using the regular expression is quite efficient. I tested the use of the `replace()` function for everything, but it had a huge performance impact. For the few custom structure words that might be added, using the `replace()` function is good enough.

**REMOVE THIS LINE BEFORE FINAL VERSION COMMIT**



```python
!jupyter nbconvert tutorial_structure_words_removal.ipynb --to markdown --output README.md
```

    [NbConvertApp] Converting notebook tutorial_structure_words_removal.ipynb to markdown
    [NbConvertApp] Writing 14219 bytes to README.md

