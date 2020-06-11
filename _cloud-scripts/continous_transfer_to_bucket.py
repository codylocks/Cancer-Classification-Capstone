import shutil
from google.cloud import storage
import os
import sys

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

def continuous_transfer_to_bucket(download_path):
    directory_list = [file_folder for file_folder in os.listdir(download_path) if os.path.isdir(download_path + fil$
    while len(directory_list) > 0:
        #print('entered while', len(directory_list))
        for directory in directory_list:
            #print('entered first for', directory)
            for file in os.listdir(download_path + directory):
                #print('entered second for', file)
                if file.endswith('.svs'):
                    print('Transfering file: ', file)
                    upload_blob('svs_images_bucket', "./manifest/{}/{}".format(directory, file), file)
                    os.remove("./manifest/{}/{}".format(directory, file))
        directory_list = [file_folder for file_folder in os.listdir(download_path) if os.path.isdir(download_path +$
continuous_transfer_to_bucket(sys.argv[1])
