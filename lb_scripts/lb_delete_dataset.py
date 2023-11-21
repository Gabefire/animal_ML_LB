import labelbox as lb
from dotenv import load_dotenv, find_dotenv

_=load_dotenv(find_dotenv())

client = lb.Client()

datasets = client.get_datasets(where=(lb.Dataset.name == "animal_dataset"))
for dataset in datasets:
    dataset.delete()