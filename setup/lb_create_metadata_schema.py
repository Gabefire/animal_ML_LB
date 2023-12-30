import labelbox as lb
from datetime import datetime
from pprint import pprint
from labelbox.schema.data_row_metadata import DataRowMetadataKind
from uuid import uuid4
from dotenv import load_dotenv, find_dotenv
import sys

_=load_dotenv(find_dotenv())

client = lb.Client()

mdo = client.get_data_row_metadata_ontology()
metadata_ontologies = mdo.fields_by_id


enum_schema = mdo.create_schema(
    name="animal_class",
    kind=DataRowMetadataKind.enum,
    options=translate.values()
)

schema_id = enum_schema.uid

print(schema_id)