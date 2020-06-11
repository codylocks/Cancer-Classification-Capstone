# imports
import pandas as pd
import numpy as np

# imports for file logistics
from google.cloud import storage
import gcloud_storage
import os

# imports for image processing
from deephistopath.wsi import slide, tiles
from deephistopath.wsi import filter as filter_

# garbage collector to free memory
import gc

# SET PATHS
diagnosis_df_path = './diagnosis_df.csv'
svs_path = './data/svs_files'
tiles_png_path = './data/tiles_png/'
google_credentials_path = './Capstone-Image-Classifcation-393c7bd67e84.json'

# Establish Credentals
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credentials_path

# Load in Dataframe
diagnosis_df = pd.read_csv(diagnosis_df_path)

# loop through database at increments = increments
start = 0
increment = 4
list_to_loop = [x for x in range(len(diagnosis_df['file_name']))]

# for each batch of svs files
for i in list_to_loop[start::increment]:

    # for each file in batch:
    for j in range(increment):
        if i+j in list_to_loop:
            # download our svs file to ./data/svs_files/TEST-TR-{slide_num} (needed naming convetion for deephistopath)
            gcloud_storage.download_blob('svs_images_bucket',
                                         diagnosis_df['file_name'][i+j],
                                         os.path.join('data', 'svs_files', f'TEST-TR-{str(j+1).zfill(3)}.svs'))

            # add refrences to diagnosis_df
            slide_ref_mask = diagnosis_df['file_name'] == diagnosis_df['file_name'][i+j]
            diagnosis_df.loc[slide_ref_mask, 'batch_number'] = f'batch_{i}'
            diagnosis_df.loc[slide_ref_mask, 'slide_number'] = f'{str(j+1).zfill(3)}'

    diagnosis_df.to_csv('./data/diagnosis_df_backup.csv', index = False)
    # run the following on whole batch
    slide.multiprocess_training_slides_to_images()
    filter_.multiprocess_apply_filters_to_images()
    tiles.multiprocess_filtered_images_to_tiles()

    # transfer all files (except svs) to bucket to save
    #remove svs first:
    for svs in os.listdir(os.path.join('data', 'svs_files')):
        kill_command = f'rm -rf ./data/svs_files/{svs}'
        os.system(kill_command)

    # copy everything else to bucket
    copy_command_string = f'gsutil -m cp -r ./data gs://deephistopath-output/batch_{i}'
    os.system(copy_command_string)

    # clean data folder
    for files in os.listdir(os.path.join('data')):
        if files != 'svs_files':
            kill_command = f'rm -rf ./data/{files}'
            os.system(kill_command)

    # clear garbage
    for i in range(2):
        n = gc.collect()
        print(f'Unreachable Trash: {n}')
