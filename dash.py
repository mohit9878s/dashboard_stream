import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import pytz

# Image to base64
def image_to_base64(img_path):
    with open(img_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Paths
jarvis_path = r"jarvis_Logo_.webp"
jarvis_base64 = image_to_base64(jarvis_path)

india_time = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

# Page Config
st.set_page_config(page_title="Communication Dashboard", layout="wide", initial_sidebar_state='auto')

# Header UI
st.markdown(f"""
    <div style='display: flex; align-items: center; justify-content: space-between; padding: 12px 0;'>
        <div><img src='data:image/webp;base64,{jarvis_base64}' width='120'/></div>
        <div style='text-align: center; flex-grow: 1;'>
            <span style='font-size: 38px; font-weight: bold;
                background: linear-gradient(90deg, #ff9900, #ff6600);
                -webkit-background-clip: text; color: transparent;
                text-shadow: 0 0 10px rgba(255,102,0,0.1);'>
                Communication Dashboard
            </span>
        </div>
        <div></div>
    </div>
""", unsafe_allow_html=True)

# Google Sheet URL
sheet_url = "https://docs.google.com/spreadsheets/d/1PAmuXQHqkVE5r0OjMwyvlxDS-O4e8CzBo8auI4uVYCA/edit#gid=1379708796"

# Load data
@st.cache_data(ttl=60)
def load_data(sheet_url):
    try:
        csv_export_url = sheet_url.replace("/edit#gid=", "/export?format=csv&gid=")
        df = pd.read_csv(csv_export_url)
        return df
    except Exception as e:
        st.error(f"❌ Failed to fetch data: {e}")
        return None

df = load_data(sheet_url)
if df is None:
    st.stop()

# Auto App refresh every 3 hours
st_autorefresh(interval=3 * 60 * 60 * 1000, key="datarefresh")

# Required columns check
required_columns = ["State", "Vendor Name", "Type of Communication", "Cohort", "Total Phone Numbers", "Total Success"]
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    st.warning(f"⚠️ Some columns are missing in the sheet: {', '.join(missing_columns)}.")

# Sidebar - Communication Filter
with st.sidebar:
    st.markdown("### 📨 Type of Communication")
    comm_options = sorted(df["Type of Communication"].dropna().unique())
    select_all = st.checkbox("Select All Communication Types")
    comm_selected = comm_options if select_all else st.pills("Filter Communication Types", comm_options, selection_mode="multi")

# Sidebar - Other filters
for key in ["state_filter", "vendor_filter", "cohort_filter"]:
    if key not in st.session_state:
        st.session_state[key] = []

with st.sidebar:
    with st.expander("🎛️ Apply Filters", expanded=True):
        if st.button("❌ Clear Filters"):
            st.session_state.state_filter = []
            st.session_state.vendor_filter = []
            st.session_state.cohort_filter = []

        state_options = sorted(df["State"].dropna().unique())
        vendor_options = sorted(df["Vendor Name"].dropna().unique())
        cohort_options = sorted(df["Cohort"].dropna().unique())

        state = st.multiselect("📍 State", state_options, default=st.session_state.state_filter, key="state_filter")
        vendor = st.multiselect("🏷️ Vendor", vendor_options, default=st.session_state.vendor_filter, key="vendor_filter")
        cohort = st.multiselect("🎯 Cohort", cohort_options, default=st.session_state.cohort_filter, key="cohort_filter")

    st.markdown("---")
    compact_style = "comma"
    format_option = st.pills("Show Numbering Format As", ["Decimal Format ( e.g. 1.1 : K, L, Cr )"])
    if format_option:
        compact_style = "compact"

    st.markdown("#### 📊 Dashboard Update")
    if st.button("🔄 Click Refresh"):
        st.cache_data.clear()
        st.rerun()

# Format functions
def format_indian_number(n):
    s = str(int(n))
    if len(s) <= 3:
        return s
    last_three = s[-3:]
    rest = s[:-3]
    parts = []
    while len(rest) > 2:
        parts.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest:
        parts.insert(0, rest)
    return ",".join(parts) + "," + last_three

def format_compact_decimal(n):
    n = int(n)
    if n >= 1e7:
        return f"{int(n / 1e5) / 100:.2f} Cr"
    elif n >= 1e5:
        return f"{int(n / 1e3) / 100:.2f} L"
    elif n >= 1e3:
        return f"{int(n / 10) / 100:.2f} K"
    return str(n)

# Accurate Vendor-wise Comment Function
def get_comment(success_pct, vendor):
    vendor = vendor.strip().lower()
    pct = round(success_pct)

    rr_vendors = ["rr communication", "go2market", "half circle", "cosmic", "inbox media"]
    sarv_vendors = ["sarv", "jio"]
    riddhi_vendors = ["riddhi tech"]
    netcore_vendors = ["netcore"]

    if vendor in rr_vendors:
        if 0 <= pct <= 20:
            return "Runs on only 50% Data with No retries"
        elif 21 <= pct <= 35:    
            return "Run with No retries"
        elif 36 <= pct <= 60:
            return "Runs perfectly with 3 retries"
        elif 61 <= pct <= 75:
            return "5% chances of fraud"
        elif 76 <= pct <= 90:
            return "10% chances of fraud"
        elif 91 <= pct <= 100:
            return "15% chances of fraud"

    elif vendor in sarv_vendors:
        if 0 <= pct <= 35:
            return "Run with No retries"
        elif 36 <= pct <= 55:
            return "Runs perfectly with 3 retries"
        elif 56 <= pct <= 65:
            return "5% chances of fraud"
        elif 66 <= pct <= 80:
            return "10% chances of fraud"
        elif 81 <= pct <= 100:
            return "15% chances of fraud"

    elif vendor in riddhi_vendors:
        if 0 <= pct <= 25:
            return "100% DND scrubbing"
        elif 26 <= pct <= 37:
            return "50% DND Scrubbing"
        elif 38 <= pct <= 60:
            return "Runs perfectly with 3 retries"
        elif 61 <= pct <= 70:
            return "5% chances of fraud"
        elif 71 <= pct <= 80:
            return "10% chances of fraud"
        elif 81 <= pct <= 100:
            return "15% chances of fraud"

    elif vendor in netcore_vendors:
        if 0 <= pct <= 20:
            return "100% DND scrubbing"
        elif 21 <= pct <= 30:
            return "80% DND Scrubbing"
        elif 31 <= pct <= 40:
            return "50% DND Scrubbing"
        elif 41 <= pct <= 60:
            return "Runs perfectly with 3 retries"
        elif 61 <= pct <= 70:
            return "5% chances of fraud"
        elif 71 <= pct <= 80:
            return "10% chances of fraud"
        elif 81 <= pct <= 100:
            return "15% chances of fraud"

    return "-"

# Apply Filters
filtered_df = df.copy()
if state:
    filtered_df = filtered_df[filtered_df["State"].isin(state)]
if vendor:
    filtered_df = filtered_df[filtered_df["Vendor Name"].isin(vendor)]
if cohort:
    filtered_df = filtered_df[filtered_df["Cohort"].isin(cohort)]
if comm_selected:
    filtered_df = filtered_df[filtered_df["Type of Communication"].isin(comm_selected)]

# Summary Table
if not filtered_df.empty:
    group_by = st.selectbox("📂 Group Data By", ["Vendor Name", "State", "Cohort"])
    summary = filtered_df.groupby(group_by)[["Total Phone Numbers", "Total Success"]].sum().reset_index()
    summary["Success %"] = summary.apply(lambda row: (row["Total Success"] / row["Total Phone Numbers"] * 100)
                                         if row["Total Phone Numbers"] > 0 else 0, axis=1).round(2)

    # Apply accurate comment logic only when grouped by Vendor Name and OBD selected
    if len(comm_selected) == 1 and comm_selected[0] == "OBD" and group_by == "Vendor Name":
        summary["Comment"] = summary.apply(lambda row: get_comment(row["Success %"], row["Vendor Name"]), axis=1)

    total_ph = filtered_df["Total Phone Numbers"].sum()
    total_succ = filtered_df["Total Success"].sum()
    overall_pct = (total_succ / total_ph * 100) if total_ph else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**📞 Total Phone Numbers**")
        st.markdown(f"<h4>{format_compact_decimal(total_ph)} <span style='color:steelblue;'>({format_indian_number(total_ph)})</span></h4>", unsafe_allow_html=True)
    with col2:
        st.markdown("**☑️ Total Success**")
        st.markdown(f"<h4>{format_compact_decimal(total_succ)} <span style='color:orangered;'>({format_indian_number(total_succ)})</span></h4>", unsafe_allow_html=True)
    with col3:
        st.markdown("**📈 Overall Success %**")
        st.markdown(f"<h4>{overall_pct:.0f} %</h4>", unsafe_allow_html=True)

    st.markdown("### 📋 Summary Table")
    display_df = summary.copy()
    if compact_style == "compact":
        display_df["Total Phone Numbers"] = summary["Total Phone Numbers"].apply(format_compact_decimal)
        display_df["Total Success"] = summary["Total Success"].apply(format_compact_decimal)
    else:
        display_df["Total Phone Numbers"] = summary["Total Phone Numbers"].apply(format_indian_number)
        display_df["Total Success"] = summary["Total Success"].apply(format_indian_number)

    display_df["Success %"] = summary["Success %"].apply(lambda x: f"{x:.0f} %")
    if "Comment" in summary.columns:
        display_df["Comment"] = summary["Comment"]

    display_df.index = range(1, len(display_df) + 1)
    st.dataframe(display_df, use_container_width=True)

    # Chart
    chart_data = summary.copy().sort_values("Success %", ascending=False)
    chart_data["Success %"] = chart_data["Success %"].apply(lambda x: f"{x:.0f} %")
    fig = px.bar(
        chart_data,
        x=group_by,
        y="Success %",
        text="Success %",
        color="Success %",
        color_continuous_scale="Viridis",
        title=f"{group_by}-wise Success %"
    )
    fig.update_traces(texttemplate="<b>%{text}</b>", textposition="inside")
    fig.update_layout(yaxis_title="Success %", xaxis_title=group_by)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("📌 Not enough data to display summary or metrics.")
