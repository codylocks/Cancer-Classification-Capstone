'''
Contained here are functions to combine the clinical and metadata databases,
unpack the nested dictionaries, then combine them and keep the necessary columns
'''
import pandas as pd
import os

def build_metadata_df(file_path):
    '''
    Load in our metadata.json file.
    Unpack associated_entities column
    '''

    df = pd.read_json(file_path) # load in df

    # unpacking
    for key in df['associated_entities'][0][0].keys():
        df[key] = [value[0][key] for value in df['associated_entities']]

    return df

def build_clinical_df(file_path):
    '''
    Load in our clinical.json file.
    Unpack exposures, diagnoses, and demographic
    '''

    df = pd.read_json(file_path) # load in df
    df.dropna(inplace=True) # drop row 827 (NaN's)

    # unpacking
    for key in df['diagnoses'][0][0].keys():
        df[f'diagnoses_{key}'] = [value[0][key] for value in df['diagnoses']]

    return df



def combine_df(metadata_path, clinical_path, col_list = [], check_all_cols = False):
    '''
    This will combine the two datasets and keep only what we need
    '''

    metadata_df = build_metadata_df(metadata_path)
    clinical_df = build_clinical_df(clinical_path)
    if check_all_cols:
        print('Metadata_df Columns:\n', metadata_df.columns)
        print('Clinical_df Columns: \n', clinical_df.columns)
    cols_to_keep = ['case_id','file_id','file_name','diagnoses_primary_diagnosis','file_size']
    df = metadata_df.merge(clinical_df, left_on = 'case_id', right_on = 'case_id')
    cols_to_keep.extend(col_list)
    return_df = pd.DataFrame(df[cols_to_keep])

    return return_df
