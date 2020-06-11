'''

The following contains functions to move and rename files and directories

'''
import shutil
from google.cloud import storage
import os
import sys
import pandas as pd

def rename_svs_update_df(df, svs_path):
    '''
    Here we rename our svs files to follow naming convention used in
    python-wsi-preprocessing for ease of use.  We also need to update our
    dataframe to keep track of which images belongs to which row.

    These two happen in the same function to avoid mistakes
    '''
    # creates list of files to rename
    file_list = [file for file in os.listdir(svs_path) if file.endswith('.svs')]
    # creates new column to add new names to
    df['renamed_image_file'] = df['file_name']
    for i, file in enumerate(file_list):
        df.loc[df['file_name'] == file, 'renamed_image_file'] = f'TEST-TR-{str(i + 1).zfill(3)}.svs'
        os.rename(svs_path + file, svs_path + f'TEST-TR-{str(i + 1).zfill(3)}.svs')
        print(f'Renaming file {file} ==> TEST-TR-{str(i + 1).zfill(3)}.svs')


def relocate_svs(start_path, dest_path):
    '''
    All the svs files save to their own directory, we want them all in one directory
    '''
    # looop through each directory in main directory
    for dir_ in os.listdir(start_path):

        # each svs file is contained within its own directory, so we go into each dir
        if os.path.isdir(start_path + dir_):

            # for each item in the specifified directory
            for file in os.listdir(start_path + dir_):

                # Look for svs files
                if file.endswith('.svs'):

                    # move svs file to where we will access them
                    svs_file_path = start_path + dir_ + '/' + file
                    shutil.move(svs_file_path, dest_path)


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )

# def continuous_transfer_to_bucket(download_path):
#     directory_list = [file_folder for file_folder in os.listdir(download_path) if os.path.isdir(download_path + file_folder)]
#     while len(directory_list) > 0:
#         # print('entered while', len(directory_list))
#         for directory in directory_list:
#             # print('entered first for', directory)
#             for file in os.listdir(download_path + directory):
#                 # print('entered second for', file)
#                 if file.endswith('.svs'):
#                     upload_blob('test-bucket-capstone', "./manifest/{}/{}".format(directory, file), 'svs_files/' + file)
#                     os.remove("./manifest/{}/{}".format(directory, file))
#         directory_list = [file_folder for file_folder in os.listdir(download_path) if os.path.isdir(download_path + file_folder)]
# # continuous_transfer_to_bucket(sys.argv[1])


# import os
# import sys
#
# def clean_partials(download_path):
#     directory_list = [file_folder for file_folder in os.listdir(download_path) if os.path.isdir(download_path + file_folder)]
#     for directory in directory_list:
#         for file in os.listdir(download_path + directory):
#             if file.endswith('.svs.partial'):
#                 os.remove("./manifest/{}/{}".format(directory, file))
#
# # clean_partials(sys.argv[1])
