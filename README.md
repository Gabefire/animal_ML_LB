# Animal Machine Learning Project

## Overview

- Convolutional neural networks project using [Labelbox](https://labelbox.com/) to manage data and provide annotations
- Dataset from [Kaggle](https://www.kaggle.com/datasets/alessiocorrado99/animals10) provided by [Carrado Alessio](https://www.kaggle.com/alessiocorrado99)

## Practicing

- Python
- Labelbox
- Tensorflow
- AWS S3

## Setup Steps

1. Download dataset from [Kaggle](https://www.kaggle.com/datasets/alessiocorrado99/animals10)
2. Upload images to AWS using boto3
3. Create dataset and create data rows inside Labelbox
4. Create ontology and include a radio feature with all the different classes
5. Create project and attach ontology
6. Create Foundry application inside Labelbox get predictions for data rows in dataset
7. Clean up data rows that do not meet set confidence parameter on model used in Foundry
8. Send data rows to created project
9. Create model from exported data rows and labels
10. Predict images and import predictions to Model inside Labelbox for version control
