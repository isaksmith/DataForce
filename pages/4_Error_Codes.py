import streamlit as st

from dataforce_utils import add_download, load_csv, render_overview, render_preview, render_r_blurb

st.title("Error Codes")
df = load_csv("error_codes.csv")

search = st.text_input("Search description or code")
filtered = df.copy()
if search:
    mask = filtered.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False))
    filtered = filtered[mask.any(axis=1)]

render_overview(filtered)
add_download(filtered, "error_codes_filtered.csv")
render_preview(filtered)

render_r_blurb("Error Codes", "error_codes.csv")
