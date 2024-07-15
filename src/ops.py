from dagster import DynamicOut, DynamicOutput, op

from src.helpers import (
    chunking_helpers,
    file_helpers,
    scraping_helpers,
    weaviate_helpers,
)

# `dagster/priority` tag is mainly to make sure that these ops are run end-to-end for each batch of links that we process.
# Otherwise, these ops run one at a time for all batches, i.e. the first op runs on all batches before moving on to the second op,
# which may not be what we want, especially if garbage collection and memory limits are involved.


@op(tags={"dagster/priority": 0}, required_resource_keys={"weaviate_client"})
def setup_weaviate_collection(context):
    """
    Create the Weaviate collection where we store the board game rules' chunks.
    """
    client = context.resources.weaviate_client
    weaviate_helpers.create_board_game_rules_collection(client)


@op(out=DynamicOut(), tags={"dagster/priority": 1})
def get_board_game_rules_links(context):
    """
    This op gets all the available board game rules sub-pages' links from UltraBoardGames.
    We process these links in batches.
    """
    for batch, offset in scraping_helpers.get_board_game_rules_links_batches():
        context.log.info(f"{offset + len(batch)} rules links retrieved.")
        yield DynamicOutput(batch, mapping_key=f"{offset}")


@op(tags={"dagster/priority": 2})
def read_rules_from_links(context, links_list):
    """
    We take the links batch and scrape the contents of the corresponding sub-pages which contain the board games' rules.
    """
    rules_list = []
    for link in links_list:
        rules_list.append(scraping_helpers.read_rules_from_link(link))
    return rules_list


@op(tags={"dagster/priority": 3})
def load_raw_rules_to_files(context, rules_list):
    """
    This is a mid-ingestion step we take to store artifacts, i.e. the scraped rules, to a file/blob system.
    This step is helpful for error recovery to prevent having to re-scrape data, and can also be used as a 'soft' means of checking which links have been processed already.
    """
    for rules in rules_list:
        file_helpers.create_rules_file(rules)


@op(tags={"dagster/priority": 4})
def chunk_rules(context, rules_list):
    """
    To account for token limits for both vectorization and eventually for usage in generation, we chunk the board game rules' contents.
    """
    chunked_rules_list = []
    for rules in rules_list:
        chunks = chunking_helpers.chunk_rules(rules)
        chunked_rules_list.extend(chunks)
    return chunked_rules_list


@op(tags={"dagster/priority": 5}, required_resource_keys={"weaviate_client"})
def push_to_db(context, rules_list):
    """
    Push the board game rules' chunks to the Weaviate collection.
    """
    client = context.resources.weaviate_client
    weaviate_helpers.load_rules_to_db(client, rules_list)
