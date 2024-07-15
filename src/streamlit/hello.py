import streamlit as st

# This is the landing page of the Streamlit application. From here, the user can choose a sub-app from the sidebar.

st.set_page_config(page_title="Board Games LLM App", page_icon="🎲")

st.write("# 🎲 Board Games LLM App")

st.sidebar.success("Please select a sub-app above.")

st.markdown("Select from the sub-apps on the left.")
