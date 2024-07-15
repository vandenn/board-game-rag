# A couple of constants and environment variables
# used across the codebase.

import os

from dotenv import load_dotenv

load_dotenv()

COLLECTION_NAME = "Rules"

DATA_FOLDER = "./data"

MODEL_NAME_EMBEDDINGS = "text-embedding-ada-002"
MODEL_NAME_QUERY = "gpt-3.5-turbo"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

WEAVIATE_HOST = os.getenv("WEAVIATE_HOST")
WEAVIATE_PORT = os.getenv("WEAVIATE_PORT")

IS_LOCAL_WEAVIATE = os.environ.get("IS_LOCAL_WEAVIATE", "false")
WCD_URL = os.environ.get("WCD_URL", "")
WCD_API_KEY = os.environ.get("WCD_API_KEY", "")

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 0.2
