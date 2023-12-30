import logging
import boto3
from botocore.exceptions import ClientError
import os
from tqdm import tqdm


def import_local_files(folder_url: str) -> list[str]:
    file_list = os.listdir(f"{folder_url}")
    file_local_urls = []

    for file in file_list:
        
        if not os.path.isdir(f"{folder_url}/{file}"):
            file_local_urls.append(f"{folder_url}/{file}")

        elif os.path.isdir(f"{folder_url}/{file}"):

            file_local_urls += import_local_files(f"{folder_url}/{file}")
    return file_local_urls


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client: boto3 = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name )
    except ClientError as e:
        logging.error(e)
        return False
    return True

file_urls = import_local_files("../raw-img")
for i,file_url  in tqdm(enumerate(file_urls), total=len(file_urls)):
    result = upload_file(file_url, "lb-mlse", f"animals/image-{i}")
    if not result:
        print(f"Error: {file_url}")
