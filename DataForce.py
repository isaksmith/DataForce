import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(page_title="MAGI Dashboard", layout="wide")

branches = pd.read_csv("Hack The Plains 2026 Datasets/branches.csv")

city_coordinates = {
    ("KS", "Emporia"): (38.4040, -96.1817),
    ("KS", "Derby"): (37.5458, -97.2689),
    ("KS", "Hutchinson"): (38.0608, -97.9298),
    ("KS", "KC Metro"): (39.0997, -94.5786),
    ("KS", "Newton"): (38.0461, -97.3450),
    ("KS", "Salina"): (38.8403, -97.6114),
    ("KS", "Topeka"): (39.0473, -95.6752),
    ("KS", "Omaha"): (41.2565, -95.9345),
    ("KS", "Tulsa"): (36.1540, -95.9928),
    ("KS", "Wichita"): (37.6872, -97.3301),
    ("OK", "Newton"): (35.2226, -97.4395),
    ("OK", "Salina"): (36.3084, -95.1533),
    ("OK", "Derby"): (36.0229, -95.9683),
    ("OK", "Topeka"): (35.4676, -97.5164),
    ("NE", "Tulsa"): (41.1400, -96.2500),
    ("NE", "Wichita"): (40.8136, -96.7026),
    ("NE", "KC Metro"): (40.9264, -98.3420),
    ("NE", "Salina"): (41.1117, -98.0026),
    ("MO", "Tulsa"): (37.2089, -93.2923),
}

city_summary = (
    branches.groupby(["branch_state", "branch_city"])
    .size()
    .reset_index(name="branches")
)

city_points = []
for row in city_summary.itertuples():
    coords = city_coordinates.get((row.branch_state, row.branch_city))
    if coords is None:
        continue
    city_points.append(
        {
            "state": row.branch_state,
            "city": row.branch_city,
            "lat": coords[0],
            "lon": coords[1],
            "branchCount": int(row.branches),
        }
    )

state_code_to_name = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
    "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}

choropleth_df = (
    branches.groupby("branch_state")
    .agg(branchCount=("branch_code", "count"))
    .reset_index()
    .rename(columns={"branch_state": "state"})
)
choropleth_df["state_name"] = choropleth_df["state"].map(state_code_to_name)

us_geojson_url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json"

terminal_map = folium.Map(location=[39.8, -98.6], zoom_start=4, tiles=None, control_scale=False)

folium.TileLayer(
    tiles="CartoDB dark_matter",
    name="Terminal Base",
    control=False,
).add_to(terminal_map)

folium.Choropleth(
    geo_data=us_geojson_url,
    name="choropleth",
    data=choropleth_df,
    columns=["state_name", "branchCount"],
    key_on="feature.id",
    fill_color="YlOrBr",
    fill_opacity=0.82,
    line_opacity=0.45,
    line_color="#fbbf24",
    line_weight=1.8,
    legend_name="Branch Data",
).add_to(terminal_map)

for point in city_points:
    popup_html = f"""
    <div style='font-family: VT323, monospace; min-width: 220px;'>
      <strong>{point['city']}, {point['state']}</strong><br>
      Branches: {point['branchCount']}
    </div>
    """
    marker_radius = max(3, point["branchCount"] * 0.75)

    folium.CircleMarker(
        location=[point["lat"], point["lon"]],
        radius=marker_radius,
        color="#f59e0b",
        weight=2,
        fill=True,
        fill_color="#22d3ee",
        fill_opacity=0.88,
        tooltip=f"{point['city']}, {point['state']} | Branches: {point['branchCount']}",
        popup=folium.Popup(popup_html, max_width=280),
    ).add_to(terminal_map)

terminal_map.get_root().html.add_child(folium.Element("""
<style>
.folium-map {
  border: 1px solid #f59e0b;
}
.leaflet-container {
  background: #05070b !important;
  font-family: 'VT323', monospace !important;
}
.leaflet-control-zoom,
.leaflet-control-attribution {
  background: #000000 !important;
  color: #fcd34d !important;
  border: 1px solid #f59e0b !important;
  box-shadow: none !important;
}
.leaflet-control-zoom a {
  background: #000000 !important;
  color: #fcd34d !important;
  border-bottom: 1px solid #f59e0b !important;
}
.leaflet-control-attribution a {
  color: #fbbf24 !important;
}
.leaflet-tooltip {
  background: #000000 !important;
  color: #fcd34d !important;
  border: 1px solid #f59e0b !important;
  box-shadow: none !important;
  font-family: 'VT323', monospace !important;
}
.leaflet-popup-content-wrapper,
.leaflet-popup-tip {
  background: #000000 !important;
  color: #fcd34d !important;
  border: 1px solid #f59e0b !important;
  box-shadow: none !important;
  font-family: 'VT323', monospace !important;
}
.legend,
.legend *,
.legend-title,
.legend-scale,
.legend-labels,
.legend-labels * {
  color: #fcd34d !important;
  fill: #fcd34d !important;
  font-family: 'VT323', monospace !important;
}
.legend {
  background: rgba(0, 0, 0, 0.88) !important;
  border: 1px solid #f59e0b !important;
  padding: 4px 6px !important;
  box-shadow: none !important;
  font-size: 9px !important;
}
.legend-title {
  font-size: 10px !important;
  letter-spacing: 0.08em !important;
  margin-bottom: 2px !important;
}
.legend-labels,
.legend-labels span,
.legend-scale ul li,
.legend-scale ul {
  font-size: 8px !important;
}
.legend-scale ul {
  margin: 0 !important;
  padding: 0 !important;
}
.legend-scale ul li span {
  border-color: rgba(251, 191, 36, 0.25) !important;
  height: 8px !important;
  width: 18px !important;
}
</style>
"""))

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');
  .terminal-shell,
  .terminal-shell *,
  .terminal-card,
  .terminal-card *,
  .leaflet-container,
  .leaflet-container *,
  .leaflet-control,
  .leaflet-control *,
  .leaflet-popup,
  .leaflet-popup *,
  .leaflet-tooltip,
  .leaflet-tooltip * {
    font-family: 'VT323', monospace !important;
  }
  .terminal-shell {
        background: #0f1116;
        color: #fcd34d;
        border: 1px solid #f59e0b;
        padding: 1rem;
    }
    .terminal-card {
        background: #000000;
        border: 1px solid #f59e0b;
        padding: 0.9rem;
        height: 100%;
    }
    .terminal-label {
        font-size: 0.96rem;
        letter-spacing: 0.11em;
        line-height: 1.05;
        color: #fbbf24;
        margin-bottom: 0.8rem;
    }
    .terminal-value {
        font-size: 1.1rem;
        color: #fde68a;
        font-weight: 700;
    }
    .ticker-wrap {
      overflow: hidden;
      border: 1px solid #f59e0b;
      background: #000000;
      margin-bottom: 0.75rem;
      white-space: nowrap;
    }
    .ticker-track {
      display: inline-flex;
      width: max-content;
      animation: ticker-scroll 18s linear infinite;
    }
    .ticker-item {
      display: inline-block;
      color: #67e8f9;
      font-size: 1rem;
      letter-spacing: 0.15em;
      margin-right: 1.25rem;
    }
    @keyframes ticker-scroll {
      0% { transform: translateX(0); }
      100% { transform: translateX(-50%); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="ticker-wrap">
      <div class="ticker-track">
        <span class="ticker-item">LIVE TELEMETRY // TOTAL SESSIONS 2,000,000</span>
        <span class="ticker-item">SESSION ALERT // FAILED TRANSACTIONS 4.8%</span>
        <span class="ticker-item">ERROR FEED // ERR_AUTH 15K</span>
        <span class="ticker-item">ERROR FEED // ERR_TIMEOUT 8K</span>
        <span class="ticker-item">SUPPORT ALERT // LIVE TICKETS 65,000</span>
        <span class="ticker-item">SYSTEM STATUS // INTERVENTION REQUIRED</span>
        <span class="ticker-item">LIVE TELEMETRY // TOTAL SESSIONS 2,000,000</span>
        <span class="ticker-item">SESSION ALERT // FAILED TRANSACTIONS 4.8%</span>
        <span class="ticker-item">ERROR FEED // ERR_AUTH 15K</span>
        <span class="ticker-item">ERROR FEED // ERR_TIMEOUT 8K</span>
        <span class="ticker-item">SUPPORT ALERT // LIVE TICKETS 65,000</span>
        <span class="ticker-item">SYSTEM STATUS // INTERVENTION REQUIRED</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div style="display:flex; justify-content:space-between; align-items:center; border:1px solid #f59e0b; background:#000; padding:0.9rem 1rem; margin-bottom:1rem;">
      <div style="font-size:1.8rem; font-weight:800; letter-spacing:0.22em; color:#fcd34d;">DASHBOARD</div>
      <div style="font-size:1rem; color:#fde68a; font-family:'VT323', monospace; letter-spacing:0.12em;">NATIONAL INSIGHT VIEW</div>
    </div>
    """,
    unsafe_allow_html=True,
)

left, center, right = st.columns([1.05, 1.7, 1.05])

with left:
    st.markdown("<div class='terminal-card'><div class='terminal-label'>LIVE TELEMETRY</div><div class='terminal-value'>TOTAL SESSIONS: 2,000,000</div><div class='terminal-value'>FAILED TRANSACTIONS: 4.8%</div></div>", unsafe_allow_html=True)
    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    st.markdown("<div class='terminal-card'><div class='terminal-label'>ERROR TRACKING</div><div class='terminal-value'>ERR_AUTH: 15K</div><div class='terminal-value'>ERR_TIMEOUT: 8K</div><div class='terminal-value'>ERR_DEPOSIT: 5K</div></div>", unsafe_allow_html=True)
    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    st.markdown("<div class='terminal-card'><div class='terminal-label'>COST PER FEATURE</div><div class='terminal-value'>SUCCESSFUL TRANSACTION: $0.01</div><div class='terminal-value'>FAILED TRANSACTION: $12.00</div></div>", unsafe_allow_html=True)

with center:
    st_folium(terminal_map, use_container_width=True, height=520)
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class='terminal-card' style='margin-bottom:1rem;'>
          <div style='display:grid; grid-template-columns:repeat(3,1fr); gap:0.75rem; margin-bottom:1rem;'>
            <div style='border:1px solid #f59e0b; padding:0.75rem; background:#111827;'><div class='terminal-label'>DEMOGRAPHICS</div><div class='terminal-value'>ACTIVE PROFILES: 355,000</div></div>
            <div style='border:1px solid #f59e0b; padding:0.75rem; background:#111827;'><div class='terminal-label'>SESSION LOGS</div><div class='terminal-value'>FAILED PATHWAYS: 96,000</div></div>
            <div style='border:1px solid #f59e0b; padding:0.75rem; background:#111827;'><div class='terminal-label'>SUPPORT ALERTS</div><div class='terminal-value'>LIVE TICKETS: 65,000</div></div>
          </div>
          <div style='border:1px solid #ef4444; background:#220808; padding:1.25rem; text-align:center;'>
            <div style='font-size:0.8rem; letter-spacing:0.28em; color:#fca5a5; margin-bottom:0.8rem;'>TOTAL FRICTION COST</div>
            <div style='font-size:3.5rem; font-weight:800; color:#f87171;'>$12,450.00</div>
            <div style='margin-top:0.9rem; border:1px solid #f59e0b; background:#000; padding:0.7rem; color:#fcd34d; font-size:1rem; letter-spacing:0.2em;'>SYSTEM INTERVENTION: REQUIRED</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown("<div class='terminal-card'><div class='terminal-label'>CUSTOMER DEMOGRAPHICS</div><div class='terminal-value'>ACTIVE PROFILES: 355,000</div></div>", unsafe_allow_html=True)
    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    st.markdown("<div class='terminal-card'><div class='terminal-label'>SUPPORT SATURATION</div><div class='terminal-value'>LIVE TICKETS: 65,000</div><div class='terminal-value'>AGENT LOAD: 92%</div></div>", unsafe_allow_html=True)
    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    st.markdown("<div class='terminal-card'><div class='terminal-label'>AVG FRICTION SCORE</div><div style='border:1px solid #ef4444; background:#450a0a; color:#fca5a5; padding:0.9rem; text-align:center; font-size:2.3rem; line-height:1.0; font-weight:800;'>22.55</div></div>", unsafe_allow_html=True)
