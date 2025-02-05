# Classifying Brain Tumors using a Convolutional Neural Net.

## Problem Statement:

Can we classify different types of brain cancers from whole slide images?

## Executive Summary:

### Data Collection: 

Data was taken from [GDC Cancer Portal](https://gdc.cancer.gov/). 

I used the 1703 primary diagnostic slides from the brain cancer sections. And downloaded the following:

1. Manifest (text file)
1. Clinical data (json)
1. Metadata (json)

### GDC Downloader Tool:

The following tool, [GDC-Data-Transfer-Tool](https://gdc.cancer.gov/access-data/gdc-data-transfer-tool), was used to download the SVS files onto a google compute instance, at the same time [this process](./cloud-scripts/continous_transfer_to_bucket.py) transferred them to a Bucket for storage. 

### Dataframes:

The Clinical and Metadata Json files needed to be unpacked, put into dataframes, and joined to make a working database.  This is handled by [This function](./cloud-scripts/build_database.py), which is called in the image processing function.

### Image Processing:

This is handled by the [image_processor.py](./cloud-scripts/image_processor.py). The function performs the following processes:

1. Builds dataframe from clinical and metadata json files
1. Loads batch of `batch size` (this should be set relative to number of cores/ availble memory). 
1. Using the [Deephistopath library](https://github.com/CODAIT/deep-histopath) (special thanks) the svs files are converted to png's, filtered, tiled, and the top 100 tiles are saved.  
1. Tiles are converted to arrays, and an array of diagnoses are created. 
1. Arrays and all created images are sent to a bucket.
1. Files are removed from the local compute instance.
1. Garbage Collection is performed.
1. Loop starts again for the next batch.

### Neural Net:

Arrays are transferred to the bucket using `gsutil` and run through [neural-net.py](./cloud-scripts/neural-net.py)


## Results:

For full results please see [here](./slidedeck.pdf)

Issues that were not overcome prevented me from building a model using the entire set of data.

A smaller set of data (3600 images) was used and I was able to achieve a testing accuracy of 94.37% and a training accuracy of 94.47%.  

It is my belief that increasing the size of the dataset used to train the CNN will improve the accuracy and robustness of the CNN.


## Citations:

[openslide](https://openslide.org/)

[deep-histopath](https://github.com/CODAIT/deep-histopath) **Special Thanks**

[Python WSI Preprocessing](https://github.com/deroneriksson/python-wsi-preprocessing) **Special Thanks**

[py-wsi](https://github.com/ysbecca/py-wsi)






