import streamlit as st

from dataforce_utils import apply_global_font, add_download, load_csv, plot_value_counts, render_overview, render_preview, render_r_blurb

apply_global_font()

st.title("🎯 Tammy's Dashboard")
st.caption("Welcome to Tammy's personal workspace for exploring DataForce insights!")

# Display a greeting
st.markdown("---")
st.markdown("""
### Welcome to Your Page! 🎉

This is your dedicated space to explore and analyze the DataForce datasets. 
Feel free to customize this page with your favorite analyses and visualizations.
""")

# Create some sample analytics
st.markdown("---")
st.subheader("Quick Statistics")

col1, col2, col3, col4 = st.columns(4)

try:
    branches = load_csv("branches.csv")
    customers = load_csv("customers.csv")
    sessions = load_csv("digital_sessions.csv")
    
    with col1:
        st.metric("Total Branches", len(branches))
    
    with col2:
        st.metric("Total Customers", len(customers))
    
    with col3:
        st.metric("Digital Sessions", len(sessions))
    
    with col4:
        st.metric("Datasets", 6)
    
    # Add a section for exploring any dataset
    st.markdown("---")
    st.subheader("Dataset Explorer")
    
    selected_dataset = st.selectbox(
        "Choose a dataset to explore:",
        ["Branches", "Customers", "Digital Sessions", "Error Codes", "Feature Costs", "Support Interactions"]
    )
    
    dataset_map = {
        "Branches": "branches.csv",
        "Customers": "customers.csv",
        "Digital Sessions": "digital_sessions.csv",
        "Error Codes": "error_codes.csv",
        "Feature Costs": "feature_costs.csv",
        "Support Interactions": "support_interactions.csv"
    }
    
    df = load_csv(dataset_map[selected_dataset])
    
    st.markdown(f"### {selected_dataset}")
    render_overview(df)
    add_download(df, f"{selected_dataset.lower().replace(' ', '_')}.csv")
    render_preview(df)
    
except Exception as e:
    st.error(f"Error loading data: {e}")

st.markdown("---")
st.info("💡 Tip: Use the sidebar to navigate between different dataset pages for more detailed analyses!")
