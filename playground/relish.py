import pandas as pd

file_path = 'playground/RELISH.tsv'
column_names = ['PMID1', 'PMID2', 'rel']
df = pd.read_csv(file_path, sep='\t', names=column_names)

#  Analyzing number of unique reference PMIDs
print(len(df['PMID1'].unique()))
      

#  Analyzing number of assessments for each reference PMID
pair_counts = df.groupby('PMID1')['PMID2'].nunique().reset_index(name='count')
pair_counts.to_csv('relish_assessments.tsv', sep='\t')


#  Analyzing unique number of assessments for all reference PMIDs
print(pair_counts['count'].unique())


#  Analyzing number of reference PMIDs with more than or equal to 50 assessments
print((pair_counts['count']>=50).sum())

#  List of reference PMIDs with less than 50 assessments
filtered_pmids = pair_counts.loc[pair_counts['count'] < 50, 'PMID1']
print(filtered_pmids)


#  Analyzing number of reference PMIDs with less than 50 assessments
print((pair_counts['count']<50).sum())


#  Analyzing number of pairs not to be considered (pairs whose PMID1 has less than 50 assessments)
pmid_counts = df['PMID1'].value_counts().reset_index(name='count')
selected_pmids = pmid_counts.loc[pmid_counts['count'] < 50]
pmids = selected_pmids['PMID1']

filtered_df = df[~df['PMID1'].isin(pmids)]
filtered_df.to_csv('relish_filtered_pairs.tsv', sep='\t')

print('Total number of pairs in RELISH:', len(df))
print('Total number of pairs after filtering:', len(filtered_df)) 
print('Number of pairs to be removed:', len(df)-len(filtered_df)) 
