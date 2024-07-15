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
st.set_page_config(page_title="Board Game Rules Q&A", page_icon="🎲")
st.title("❓ Board Game Rules Q&A")

client = initiate_weaviate_client()

# We use OpenAI's GPT 3.5 for answering
llm = ChatOpenAI(api_key=OPENAI_API_KEY, model=MODEL_NAME_QUERY, temperature=0.7)

# We store the prompt in a separate .txt file to avoid polluting the code
with open("./src/streamlit/prompts/rules_query_prompt.txt") as prompt_file:
    prompt_text = prompt_file.read()

# We send two inputs: the user query and the snippets we'll retrieve from Weaviate related to the query.
rules_query_prompt = PromptTemplate(
    template=prompt_text, input_variables=["query", "snippets"]
)

# Create the chain that we call with our input parameters to receive a result from our LLM.
rules_query_chain = LLMChain(llm=llm, prompt=rules_query_prompt, verbose=True)


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


with st.form("rules_form"):
    # Input field
    query = st.text_area(
        "Have a board game rules question?",
        placeholder="Example: How do I wen in Splendor?",
    )
    submitted = st.form_submit_button("Submit")

    if query:
        # Get the Weaviate collection.
        rules_collection = client.collections.get(COLLECTION_NAME)
        # Do hybrid search on the rules collection from the query.
        # We use hybrid because we want a combination of semantic understanding of the what rules they're asking for,
        # but we also want to take into account specific board game-specific keywords and terminologies the user uses.
        # We limit the results to 1 to prevent the possibility of having two different board games be results. However,
        # an intermediate step can be done to do some kind of reranking of the results.
        response = rules_collection.query.hybrid(query=query, limit=1)
        # The snippets are prepared for prompt formatting.
        snippets = prepare_snippets(response.objects)
        payload = {"query": query, "snippets": snippets}
        # Pass the payload to the query chain.
        generated_answer = rules_query_chain(payload)
        generated_answer = postprocess_answer(generated_answer["text"])
        # Display the answer.
        st.info(generated_answer)
