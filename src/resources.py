from dagster import resource

from src.helpers import weaviate_helpers


# In order to be able to pass a Weaviate client to the ops in the pipelines,
# we need to declare a separate resource which is defined in the corresponding job.
@resource
def weaviate_client_resource(init_context):
    client = weaviate_helpers.initiate_weaviate_client()
    try:
        yield client
    finally:
        client.close()
