import streamlit as st

from dataforce_utils import DATASETS

st.set_page_config(page_title="DataForce Explorer", layout="wide")

st.title("Overview")
st.caption("Explore every Hack The Plains 2026 dataset through Python pages, with matching R/Shiny starter guidance.")

st.markdown("### Available pages")
for page_name, file_name in DATASETS.items():
    st.markdown(f"- **{page_name}** — `{file_name}`")

st.info("Use the left sidebar to open a dataset-specific page.")

st.markdown("### Included in each page")
st.markdown(
    """
- summary metrics
- interactive filters
- preview table
- Python charts
- R/Shiny implementation notes
"""
)
