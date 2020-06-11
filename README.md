# Classifying Brain Tumors using a Convolutional Neural Net.

## Problem Statement:

Can we classify different types of brain cancers from whole slide images?

## Executive Summary:

### Data Collection: 

Data was taken from [GDC Cancer Portal](https://gdc.cancer.gov/). 

I used the 1703 primary diagnostic slides from the brain cancer sections. And downloadedthe following:

1. Manifest (text file)
1. Clinical data (json)
1. Metadata (json)

### GDC Downlader Tool:

The following tool, [GDC-Data-Transfer-Tool](https://gdc.cancer.gov/access-data/gdc-data-transfer-tool), was used to download the SVS files onto a google compute instance, at the same time [this process](./_cloud-scripts/continous_transfer_to_bucket.py) transfered them to a Bucket for storage. 

### Building Dataframes:




## Citations:

[openslide](https://openslide.org/)

[deep-histopath](https://github.com/CODAIT/deep-histopath) **Special Thanks**

[Python WSI Preprocessing](https://github.com/deroneriksson/python-wsi-preprocessing) **Special Thanks**

[py-wsi](https://github.com/ysbecca/py-wsi)




