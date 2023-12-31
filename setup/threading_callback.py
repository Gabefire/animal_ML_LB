import boto3
from PIL import Image
import numpy as np
import io

IMG_SIZE = 64

def get_img(aws_url: str):
    s3 = boto3.resource('s3', region_name='us-east-1')
    bucket = s3.Bucket('lb-mlse')
    img_name = aws_url.split("/")[-1]
    image = bucket.Object(f'animals/{img_name}')
    img_data = image.get().get('Body').read()

    return Image.open(io.BytesIO(img_data))

def threading_callback(data_row: dict[str:str]):
    img = get_img(data_row["data_row"]["row_data"])
    global_key = data_row["data_row"]["global_key"]
    img = img.resize((IMG_SIZE, IMG_SIZE))
    img = np.asarray(img, dtype=np.float32) / 255
    if img.shape != (IMG_SIZE,IMG_SIZE,3):
        return
    
    with open(f"../numpy/{global_key}.npy", "wb") as file:
        np.save(file, img)