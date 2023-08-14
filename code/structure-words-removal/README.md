# Structure words removal

## What it does
The following script is used to generate a list of common structure words that appear in the articles' abstract. These structure  words or groups of words followed by a colon, most likely required by the journals. Since they do not provide any meaningful information to the text, they should be removed.

Some examples of these structure words are "BACKGROUND:", "CONCLUSIONS:", "METHODS:", etc.

The regular expression that matches these structure words follows:

* The word/group of words should be at least 3 characters long and at most 70.

* The word/group of words must be at the start of a sentence.

* The word/group of words must be followed by a colon and an empty space ": ".

## How to use

### Generate the list from the script

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

### Remove the structure words from the script

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
python structurewords_remover.py --input ../../data/RELISH/xml-files/pmid-xml/ --list structure_word_list.txt
```

The output XML files are in the  `data/RELISH/xml-files/pmid-xml_no_structure_words` directory.

## Results

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

**REMOVE THIS LINE BEFORE FINAL VERSION COMMIT**


```python
!jupyter nbconvert readme_gen.ipynb --to markdown --output README.md
```
