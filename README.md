# Board Game Rules RAG with Weaviate
(requires Python 3.11+)

## Overview

An end-to-end Weaviate-based workflow from data ingestion to frontend RAG on board game rules.

### Board Game Rules RAG System Diagram

1. The board game rules are scraped from the UltraBoardGames aggregator website through a Dagster op.
1. The Dagster job saves the rules to files as artifacts, chunks the rules (with overlap), creates a Weaviate collection, and pushes the chunks there. The Dagster job was (overkill) designed to handle large volumes of data in parallel.
1. Documents are vectorized in Weaviate using the default `text-ada-002` embeddings.
1. The Weaviate collection is then accessed by the Streamlit web app, whose Q&A capabilities are powered by prompting LangChain + GPT3.5 and performing retrieval using Weaviate's querying capabilities.

## Setup and Running
### Environment Variables
Run the following command to get a fresh `.env` file:
```
cp .env.example .env
```
Then populate the `.env` file's missing values.

_Feel free to request for `.env` values from me, especially if you want a WCD instance that already has data!_

### First-time Setup
Run the following commands for first-time setup:
```
make init
make setup
```
If you're setting up a local Docker instance using the `docker-compose.yml` in this repo, set `IS_WEAVIATE_LOCAL` to `true` and run:
```
make docker-up
```
Otherwise, make sure you have WCD `.env` variables set up to connect to your cloud instance, and set `IS_WEAVIATE_LOCAL` to `false`.

### Data Ingestion
_(If you're connected to an instance that already has the data ingested, e.g. in WCD, you can skip this section.)_

To ingest the data for the board game rules RAG system, first run the following command:
```
make run
```
This will start a local Dagster instance which is accessible via localhost:3000.
From the Dagster UI, click on the "Launchpad" tab, then "Launch Run".

### Frontend
Once the data ingestion is completed, you can now run the Streamlit frontend via:
```
make streamlit
```
The frontend application should be accessible via localhost:8501.
