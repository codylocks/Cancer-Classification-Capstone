from google.cloud import storage
import pandas as pd
import numpy as np
import os
from build_database import combine_df
import gcloud_storage
from deephistopath.wsi import slide, tiles
from deephistopath.wsi import filter as filter_
from tensorflow.keras.preprocessing.image import load_img, img_to_array, array_to_img
import time
import gc

# SET PATHS
metadata_df_path = './metadata.cart.2020-06-05.json'
clinical_df_path = './clinical.cart.2020-06-05.json'
original_svs_files_path = './data/svs_files/'
tiles_png_path = './data/tiles_png/'
google_credentials_path = '[YOUR GOOGLE_APPLICATION_CREDENTIALS]'

# Establish Credentals
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credentials_path

# build dataframe
original_df = combine_df('./metadata.cart.2020-06-05.json', './clinical.cart.2020-06-05.json')

# add column to be used later
original_df['renamed_image_file'] = 'tbd'

# drop diagnosis of huge imbalance (the only two 2 Malignant lymphoma, large B-cell, diffuse, NOS)
original_df.drop(original_df[original_df['diagnoses_primary_diagnosis'] == 'Malignant lymphoma, large B-cell, diffuse, NOS'].index, inplace = True)

# main function:
# how many files we process at a time
increment = 12
start = 0
#create list length of diagnosis_df['file_name']
list_to_loop = [x for x in range(len(original_df['file_name']))]

# for each batch of svs files
for i in list_to_loop[start::increment]:

    # instantiate lists:
    tile_array_list = []
    diagnosis_list = []
    slide_list = []

    # instantiate array to concat image arrays (try, except to create on first pass)
    try:
        main_tile_array_array = np.load('./main_tile_array_array.npy')
        print('Successfully Loaded main_tile_array_array.npy')
    except:
        main_tile_array_array = np.empty(shape=[0,256,256,3])
        print('main_tile_array_array.npy not found. Created empty array')

    # instantiate df to concat diagnosis
    try:
        diagnosis_df_saved = pd.read_csv('./diagnosis_df_saved.csv')
        print('Successfully Loaded diagnosis_df_saved.csv')
    except:
        diagnosis_df_saved = pd.DataFrame(columns=['diagnosis'])
        print('diagnosis_df_saved.csv not found. Created empty df')

    # weird to reset it each time, but allows us to locate the new batch of files in the dataframe
    # and through that the diagnosis
    original_df['renamed_image_file'] = 'tbd'

    # download svs file name svs file TEST-TR-XXX
    for j in range(increment):
        if (i + j) in list_to_loop:
            gcloud_storage.download_blob('svs_images_bucket',
                                         original_df['file_name'][i+j],
                                         os.path.join('data', 'svs_files', f'TEST-TR-{str(j+1).zfill(3)}.svs'))

            original_df.loc[original_df['file_name'] == original_df['file_name'][i+j],
                             'renamed_image_file'] = f'TEST-TR-{str(j+1).zfill(3)}.svs'
            slide_list.append(str(original_df.loc[i+j]['file_name']))

    with open("./data/slide_ref_list.txt", "w") as outfile:
        outfile.write("\n".join(slide_list))

    # run slide, filter, tile
    slide.multiprocess_training_slides_to_images()
    filter_.multiprocess_apply_filters_to_images()
    tiles.multiprocess_filtered_images_to_tiles()

    # for each tile in tile_png
    for directory in os.listdir(tiles_png_path):
        for file in os.listdir(os.path.join(tiles_png_path, directory)):
            diagnosis = original_df[original_df['renamed_image_file'] == f'{"-".join(file.split("-", 3)[:3])}.svs']['diagnoses_primary_diagnosis'].item()
            print('Processing: ', file)
            print('File refrence: ', "-".join(file.split("-", 3)[:3]))
            print('diagnosis: ', diagnosis)
            tile = load_img(os.path.join(tiles_png_path, directory, file))

            tile_array = img_to_array(tile, dtype = 'int16')
            tile_array_list.append(tile_array)
            diagnosis_list.append(diagnosis)


    # save lists (overwrite each time so we are saving progress)

    # first we save image arrays
    tile_array_array = np.asarray(tile_array_list, dtype = np.int16)
    main_tile_array_array = np.concatenate((main_tile_array_array, tile_array_array))
    main_tile_array_array = main_tile_array_array.astype('int16')
    np.save('./data/main_tile_array_array_upto_batch{i}.npy', main_tile_array_array)
    np.save('./main_tile_array_array.npy', main_tile_array_array)

    # second we save diagnosis list:
    diagnosis_df_temp = pd.DataFrame({'Diagnosis': diagnosis_list})
    diagnosis_df_saved = diagnosis_df_saved.append(diagnosis_df_temp, ignore_index=True)
    diagnosis_df_saved.to_csv('./data/diagnosis_df_saved_upto_batch{i}.csv', index = False)
    diagnosis_df_saved.to_csv('./diagnosis_df_saved.csv', index = False)

    # transfer all files (except svs) to bucket to save
    #remove svs first:
    for svs in os.listdir(os.path.join('data', 'svs_files')):
        kill_command = f'sudo rm -rf ./data/svs_files/{svs}'
        os.system(kill_command)

    # copy files to bucket
    copy_command_string = f'sudo gsutil -m cp -r ./data gs://full-svs-to-arrays/batch_{i}'
    os.system(copy_command_string)

    # delete files/dirs to prepare for next svs
    natrins_barrow = 'sudo rm -rf ./data'
    rebuild_data = 'sudo mkdir data'
    rebuild_svs_files = 'sudo mkdir data/svs_files'
    for command in [natrins_barrow, rebuild_data, rebuild_svs_files]:
        os.system(command)

    # for files in os.listdir(os.path.join('data')):
    #     if files != 'svs_files':
    #         kill_command = f'rm -rf ./data/{files}'
    #         os.system(kill_command)

    # clear garbage
    for i in range(2):
        n = gc.collect()
        print(f'Unreachable Trash: {n}')
