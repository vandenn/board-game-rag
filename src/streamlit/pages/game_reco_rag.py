import os
import sys

from langchain.chains.llm import LLMChain
from langchain.chat_models.openai import ChatOpenAI
from langchain.prompts import PromptTemplate

import streamlit as st

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if root_path not in sys.path:
    sys.path.append(root_path)

from src.helpers.weaviate_helpers import initiate_weaviate_client  # noqa: E402
from src.settings import COLLECTION_NAME, MODEL_NAME_QUERY, OPENAI_API_KEY  # noqa: E402

# Streamlit boilerplate
st.set_page_config(page_title="Board Game Recommender", page_icon="🎲")
st.title("💡 Board Game Recommender")

client = initiate_weaviate_client()

# We use OpenAI's GPT 3.5 for answering
llm = ChatOpenAI(api_key=OPENAI_API_KEY, model=MODEL_NAME_QUERY, temperature=0.7)

# This page contains a two-step prompt chain. One to augment the query and the other to do the actual generation of response.

# This first prompt is for augmenting the query to have GPT3.5 use its inherent knowledge to write sample board game rules from
# board games it has seen before that fit the query, e.g. if the user asks for euro games, it will generate rules typical of euro games.
# This will make it easier to retrieve games from the Weaviate collection that meet the query.
with open("./src/streamlit/prompts/recommender_query_augmenter.txt") as prompt_file:
    prompt_text = prompt_file.read()
# For this, we only send the query as input to the prompt.
recommender_query_augmenter_prompt = PromptTemplate(
    template=prompt_text, input_variables=["query"]
)
# We then create the LLM chain that we call later with our input parameters.
recommender_query_augmenter_chain = LLMChain(
    llm=llm, prompt=recommender_query_augmenter_prompt, verbose=True
)

# This second prompt is for the actual text generation, which takes in the augmented query and retrieved chunks
# and outputs a summary of the recommendations based on what was retrieved from Weaviate.
with open("./src/streamlit/prompts/recommender_prompt.txt") as prompt_file:
    prompt_text = prompt_file.read()
# We send two inputs: the augmented user query and the snippets we'll retrieve from Weaviate related to the query.
recommender_prompt = PromptTemplate(
    template=prompt_text, input_variables=["query", "snippets"]
)
recommender_chain = LLMChain(llm=llm, prompt=recommender_prompt, verbose=True)


def prepare_snippets(vector_store_objects):
    """
    This function preprocesses the results we get from Weaviate to feed to the prompt.
    """
    snippets = ""
    for object in vector_store_objects:
        snippets = snippets + "Content: " + object.properties["content"] + "\n"
    return snippets


def postprocess_answer(answer):
    """
    This function postprocesses the response from the LLM to prevent display issues in the st.info box.
    """
    answer = answer.replace("$", "\\$")
    return answer


with st.form("reco_form"):
    # We allow the user to play around with the hybrid retrieval alpha for this page.
    # Adjusting this hyperparameter yields some interesting differences in the recommendations that the system gives.
    # After some light testing, pure keyword search does better because it adheres to the board game terminologies a
    # bit more strictly than vector/semantic search. For example, when looking for "euro" game recommendations, keyword
    # search correctly gives you games in that genre like Terra Mystica, while semantic search gives board games that
    # are related to the culture of the continent, Europe.
    alpha = st.number_input(
        "Set hybrid retrieval alpha (0.0 = pure keyword, 1.0 = pure vector):",
        min_value=0.0,
        max_value=1.0,
        value=1.0,
    )
    # Input field
    query = st.text_area(
        "Want a board game recommendation?",
        placeholder="Example: Give me a euro game recommendation",
    )
    submitted = st.form_submit_button("Submit")

    if query:
        # We first augment the query by asking the LLM to create sample board game rules
        # from its vast knowledge based on whatt was queried.
        augmented_query = recommender_query_augmenter_chain(query)["text"]
        # We show the augmented query in the frontend.
        st.text("Augmented Query:")
        st.info(augmented_query)
        # Get the Weaviate collection.
        rules_collection = client.collections.get(COLLECTION_NAME)
        # We retrieve only the top 3 games that are relevant to the augmented query.
        response = rules_collection.query.hybrid(
            query=augmented_query, limit=3, alpha=alpha
        )
        snippets = prepare_snippets(response.objects)
        payload = {"query": augmented_query, "snippets": snippets}
        # Pass the payload to the query chain.
        generated_answer = recommender_chain(payload)
        generated_answer = postprocess_answer(generated_answer["text"])
        # Display the answer.
        st.text("Recommendations:")
        st.info(generated_answer)
