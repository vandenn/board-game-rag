from dagster import job

from src import ops
from src.resources import weaviate_client_resource


@job(
    resource_defs={"weaviate_client": weaviate_client_resource},
    config={"execution": {"config": {"multiprocess": {"max_concurrent": 4}}}},
)
def ingest_board_game_rules():
    """
    This is the main entry point for our primary board game rules ingestion pipeline.
    Here, we call all the ops for setting up Weaviate, scraping the rules, and pushing the text to the vector DB.
    Note: max_concurrent is not really necessary here -- it's purely for demonstration, i.e. to show the difference of prio vs. non-prio for beefier machines
    """

    # We first setup the collection in Weaviate where we'll store the board game rules.
    ops.setup_weaviate_collection()

    # We process links (each link = 1 board game) in batches.
    # This can help mitigate potential throttling issues and facilitates easier error recovery.
    # We also use op prioritization to make sure each batch is processed fully before moving to the next batch, allowing us to free memory.
    # Because of this, the pipeline can be extended for error recovery by adding a check for which links were processed and ignoring them in the re-run.
    def _for_each(links_batch):
        # Get the board game rules' links and scrape them.
        rules_batch = ops.read_rules_from_links(links_batch)
        # We save the rules to artifact files to allow for inspection and recovery.
        # This can also be used as the artifact for checking what needs to be re-ingested in case of pipeline error.
        # Ideally, this is pushed to some cloud blob storage for persistence.
        ops.load_raw_rules_to_files(rules_batch)
        # We perform chunking with overlap on the rules' texts to handle token limits.
        rules_batch = ops.chunk_rules(rules_batch)
        # We push the rules' chunks to Weaviate.
        ops.push_to_db(rules_batch)

    # We retrieve all the available board game rules in UltraBoardGames and their corresponding subpage links.
    links = ops.get_board_game_rules_links()
    links.map(_for_each)
