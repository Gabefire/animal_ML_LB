import labelbox as lb
import os
from math import ceil
from uuid import uuid4

from dotenv import load_dotenv, find_dotenv
import datetime
import multiprocessing
import time
import urllib3
from lb_scripts.translate import translate

_=load_dotenv(find_dotenv())

client = lb.Client()



def import_local_files(img_folder_url: str) -> list[dict[str: str]]:
    dataset = []
    folder_list = os.listdir(f"./{img_folder_url}")
    mdo = client.get_data_row_metadata_ontology()

    enum_schema = mdo.fields_by_id["clp7eyhcj043p07zue0jiefah"]

    for folder in folder_list:
        file_list = os.listdir(f"./{img_folder_url}/{folder}")
        for img in file_list:
            data_row_metadata_field = lb.DataRowMetadataField(
                name=enum_schema.name,
                value=translate[folder]
            )
            dataset.append({
                "row_data": f"./{img_folder_url}/{folder}/{img}",
                "global_key": str(uuid4()),
                "metadata_fields": [data_row_metadata_field]
                })

    return dataset

def create_ontology(img_folder_url: str, ontology_name: str, client: lb.Client) -> lb.Ontology:
    class_list = os.listdir(f"./{img_folder_url}")
    ontology = client.get_ontologies("animal_class").get_one()
    if ontology:
        return ontology  
    ontology_builder = lb.OntologyBuilder(
        classifications=[
            lb.Classification(class_type=lb.Classification.Type.CHECKLIST,
                              name="checklist_question",
                              options=[lb.Option(value=item_name) for item_name in class_list])
        ]
    )
    return client.create_ontology(ontology_name,
                                  ontology_builder.asdict(),
                                  media_type=lb.MediaType.Image)

def upload_data_row(assets: list[dict[str:str]], dataset: lb.Dataset, batch_size_steps: int = 100) -> None:
    index = 0
    num_batches = ceil(len(assets)/batch_size_steps)
    counter = 1
    errors = []
    print(f"Batch: {counter}/{num_batches}")
    while index <= len(assets):
        try:
            print("Uploading...")
            result = dataset.create_data_rows(assets[index: index + batch_size_steps])
            result.wait_till_done()
        except:
            print(f"Error: {result.errors}")
            print(f"Error_Range: {index}-{batch_size_steps}")
            errors.append((index, index + batch_size_steps))
        counter += 1
        os.system("clear")
        print(f"Batch: {counter}/{num_batches}")
        time.sleep(4)
        index += batch_size_steps
    if errors:
        print("Some batches were not uploaded")
        for (index, batch_size) in errors:
            print(f"Range: {index}-{batch_size}")

            upload_data_row(assets[index: batch_size], dataset, 1000)

def check_missed_data_rows(dataset: lb.Dataset) -> bool:
    export_params= {
    "attachments": False,
    "metadata_fields": False,
    "data_row_details": True,
    "project_details": True,
    "performance_details": True
    }

    export_task = dataset.export_v2(params=export_params)
    export_task.wait_till_done()


    if export_task.errors:
        print(export_task.errors)

    export_json = export_task.result
    uploaded_ids = [data["data_row"]["external_id"] for data in export_json]
    local_ids = [data["row_data"] for data in import_local_files("raw-img")]
    missing_ids = list(set(local_ids) - set(uploaded_ids))
    if len(missing_ids) == 0:
        print("No missing images!")
        return True
    print(f"Num of missing images: {len(missing_ids)}")
    upload_data_row(assets=missing_ids, dataset=dataset, batch_size_steps=1000)

def get_global_ids(dataset: lb.Dataset) -> list[str]:
    export_params= {
    "attachments": False,
    "metadata_fields": False,
    "data_row_details": True,
    "project_details": True,
    "performance_details": True
    }

    export_task = dataset.export_v2(params=export_params)
    export_task.wait_till_done()


    if export_task.errors:
        print(export_task.errors)

    export_json = export_task.result
    return [data["data_row"]["id"] for data in export_json]

def main(client: lb.Client) -> None:
    proj = client.get_projects(where=lb.Project.name == "animal_ML").get_one()
    if not proj:
        proj = client.create_project(
            name="animal_ML",
            media_type=lb.MediaType.Image
        )
    
    


    dataset: lb.Dataset = client.get_datasets(where=lb.Dataset.name=="animal_dataset").get_one()
    check_missed_data_rows(dataset)

    if not dataset:
        assets = import_local_files("raw-img")
        dataset = client.create_dataset(
            name="animal_dataset",
            iam_integration=None
        )
        upload_data_row(assets, dataset, 1000)
    
    result = False
    while not result:
        result = check_missed_data_rows(dataset=dataset)
    
    #create ontology if one does not exist if not return associated ontology
    ontology = create_ontology("raw-img", "animal_class", client)

    #check if project has ontology attached
    if not proj.ontology() or proj.ontology().uid != ontology.uid:
        proj.setup_editor(ontology)

    #check if project has batch
    batches = proj.batches()
    
    if not batches.get_one():
        data_rows = get_global_ids(dataset)
        proj.create_batch(name="main_batch", data_rows=data_rows)




if __name__ == "__main__":
    _=load_dotenv(find_dotenv())

    CLIENT = lb.Client()


    main(CLIENT)


    