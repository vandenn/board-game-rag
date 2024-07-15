import weaviate.classes as wvc

import weaviate
from src.settings import (
    COLLECTION_NAME,
    IS_LOCAL_WEAVIATE,
    OPENAI_API_KEY,
    WCD_API_KEY,
    WCD_URL,
    WEAVIATE_HOST,
    WEAVIATE_PORT,
)


def initiate_weaviate_client():
    """
    Start up the Weaviate client that connects to either a local Docker container (via docker-compose) or to WCD.
    The docker configuration can eventually be extended to connect to some deployed instance instead.
    """
    if IS_LOCAL_WEAVIATE == "false" and WCD_URL and WCD_API_KEY:
        client = weaviate.connect_to_wcs(
            cluster_url=WCD_URL,
            auth_credentials=weaviate.auth.AuthApiKey(WCD_API_KEY),
            headers={"X-Openai-Api-Key": OPENAI_API_KEY},
        )
    else:
        client = weaviate.connect_to_local(
            host=WEAVIATE_HOST,
            port=int(WEAVIATE_PORT),
            headers={"X-Openai-Api-Key": OPENAI_API_KEY},
        )
    return client


def close_weaviate_client(client):
    """
    Clean up the client connection by closing it.
    """
    client.close()


def create_board_game_rules_collection(client):
    """
    For the purpose of this demo, we recreate the collection every time the ingestion runs.
    This was primarily for ease nd flexibility of experimentation.
    However, when considering for production, it is likely better to keep the existing collection and
    simply append or update properties so as not to destroy data, especially if the collection grows.
    """
    if client.collections.exists(COLLECTION_NAME):
        client.collections.delete(COLLECTION_NAME)

    client.collections.create(
        name=COLLECTION_NAME,
        vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai(),
        generative_config=wvc.config.Configure.Generative.openai(),
    )


def load_rules_to_db(client, rules_list):
    """
    Bulk push the rules to the Weaviate collection.
    """
    rules_collection = client.collections.get(COLLECTION_NAME)
    rules_collection.data.insert_many(rules_list)
