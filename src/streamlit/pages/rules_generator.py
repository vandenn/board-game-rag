import os
import sys

import streamlit as st

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if root_path not in sys.path:
    sys.path.append(root_path)

from src.helpers.weaviate_helpers import initiate_weaviate_client  # noqa: E402
from src.settings import COLLECTION_NAME  # noqa: E402

# Streamlit boilerplate
st.set_page_config(page_title="Board Game Rules Generator", page_icon="🎲")
st.title("✍ Board Game Rules Generator")

client = initiate_weaviate_client()

# In this sub-app, I opted not to use Langchain to purely try the generative module that's been configured for the
# board game rules collection.


def postprocess_answer(answer):
    """
    This function postprocesses the response from the LLM to prevent display issues in the st.info box.
    """
    answer = answer.replace("$", "\\$")
    return answer


with st.form("rules_form"):
    # Input field
    query = st.text_area(
        "Give me a fictional board game idea and let's make rules for it!",
        placeholder="Example: Make me board game rules for a game about pirates and ships",
    )
    submitted = st.form_submit_button("Submit")

    if query:
        # Get the Weaviate collection.
        rules_collection = client.collections.get(COLLECTION_NAME)
        # We do a grouped task generation using the query as part of the prompt, and leaving it to Weavite to append the 2
        # board game rules that it retrieves from the collection to generate fictional board game rules.
        response = rules_collection.generate.near_text(
            query=query,
            limit=2,
            grouped_task=f"Write fictional board game rules given the query '{query}' and the following board game rules as basis.",
        )
        generated_answer = postprocess_answer(response.generated)
        # Display the answer.
        st.info(generated_answer)
