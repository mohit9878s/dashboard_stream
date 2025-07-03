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

with st.sidebar:
    st.markdown("#### 📊 Dashboard Update")
    if st.button("🔄 Click Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Google Sheet URL
sheet_url = "https://docs.google.com/spreadsheets/d/1PAmuXQHqkVE5r0OjMwyvlxDS-O4e8CzBo8auI4uVYCA/edit#gid=1379708796"

# Load data from Google Sheets
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

# Check columns and warn if missing
required_columns = [
    "State", "Vendor Name", "Type of Communication",
    "Cohort", "Total Phone Numbers", "Total Success"
]

missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    st.warning(f"⚠️ Some columns are missing in the sheet: {', '.join(missing_columns)}. The dashboard will show partial data.")

# Filters session state
for key in ["state_filter", "vendor_filter", "cohort_filter"]:
    if key not in st.session_state:
        st.session_state[key] = []

with st.sidebar:
    with st.expander("🎛️ Apply Filters", expanded=True):
        if st.button("❌ Clear Filters"):
            st.session_state.state_filter = []
            st.session_state.vendor_filter = []
            st.session_state.cohort_filter = []

        state_options = sorted(df["State"].dropna().unique()) if "State" in df.columns else []
        vendor_options = sorted(df["Vendor Name"].dropna().unique()) if "Vendor Name" in df.columns else []
        cohort_options = sorted(df["Cohort"].dropna().unique()) if "Cohort" in df.columns else []

        valid_state_default = [x for x in st.session_state.state_filter if x in state_options]
        valid_vendor_default = [x for x in st.session_state.vendor_filter if x in vendor_options]
        valid_cohort_default = [x for x in st.session_state.cohort_filter if x in cohort_options]

        state = st.multiselect("📍 State", state_options, default=valid_state_default, key="state_filter")
        vendor = st.multiselect("🏷️ Vendor", vendor_options, default=valid_vendor_default, key="vendor_filter")
        cohort = st.multiselect("🎯 Cohort", cohort_options, default=valid_cohort_default, key="cohort_filter")

    st.markdown("---")
    st.subheader("🧾 Number Format View Options")
    if "compact_view" not in st.session_state:
        st.session_state.compact_view = False
    compact_view = st.checkbox("Enable View", value=st.session_state.compact_view)
    st.session_state.compact_view = compact_view

    compact_style = None
    if compact_view:
        compact_style = st.radio("Choose Format Style", [
            "Short Format (e.g. 2.57 Cr)",
            "Full Format (e.g. 2,57,08,228 Cr)"
        ], index=0)

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

def format_full_decimal(n):
    if n >= 1e7:
        return f"{format_indian_number(n)} Cr"
    elif n >= 1e5:
        return f"{format_indian_number(n)} L"
    elif n >= 1e3:
        return f"{format_indian_number(n)} K"
    return format_indian_number(n)

# Communication Type Filter
if "Type of Communication" in df.columns and df["Type of Communication"].dropna().nunique() > 0:
    st.markdown("### 📨 Type of Communication")
    comm_options = sorted(df["Type of Communication"].dropna().unique())
    select_all = st.checkbox("Select All Communication Types")
    comm_selected = comm_options if select_all else st.pills("Filter Communication Types", comm_options, selection_mode="multi")
else:
    comm_options = []
    comm_selected = []

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

# Summary Calculation
if not filtered_df.empty and all(col in filtered_df.columns for col in ["Total Phone Numbers", "Total Success"]):
    group_by = st.selectbox("📂 Group Data By", ["Vendor Name", "State", "Cohort"])
    summary = filtered_df.groupby(group_by)[["Total Phone Numbers", "Total Success"]].sum().reset_index()
    summary["Success %"] = summary.apply(lambda row: (row["Total Success"] / row["Total Phone Numbers"] * 100)
                                         if row["Total Phone Numbers"] > 0 else 0, axis=1).round(2)

    # Metrics
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

    # Applied Filters Display
    filters_applied = []
    if state:
        filters_applied.append(f"<span style='color:#2980b9;'>State:</span> {', '.join(state)}")
    if vendor:
        filters_applied.append(f"<span style='color:#f39c12;'>Vendor:</span> {', '.join(vendor)}")
    if cohort:
        filters_applied.append(f"<span style='color:#8e44ad;'>Cohort:</span> {', '.join(cohort)}")
    if comm_selected:
        filters_applied.append(f"<span style='color:#FF00FF;'>Communication:</span> {', '.join(comm_selected)}")

    if filters_applied:
        st.markdown("#### 🔎 Filters Applied:")
        for f in filters_applied:
            st.markdown(f"<p>{f}</p>", unsafe_allow_html=True)

    # Summary Table
    format_func = format_full_decimal if compact_view and compact_style == "Full Format (e.g. 2,57,08,228 Cr)" else (
        format_compact_decimal if compact_view else format_indian_number)

    display_df = summary.sort_values("Total Phone Numbers", ascending=False).copy()
    display_df["Total Phone Numbers"] = summary["Total Phone Numbers"].apply(format_func)
    display_df["Total Success"] = summary["Total Success"].apply(format_func)
    display_df["Success %"] = summary["Success %"].apply(lambda x: f"{x:.1f} %")

    if len(comm_selected) == 1 and comm_selected[0] == "OBD":
        def get_comment(pct):
            pct = int(round(pct))
            for low, high, comment in [
                (0, 10, "Campaigns not initiated properly"),
                (11, 20, "Run on only 30-40% of phone numbers"),
                (21, 30, "100% DND scrubbing"),
                (31, 40, "Only 1 retry"),
                (41, 60, "Run perfectly with 3 retries"),
                (61, 70, "Up to 5% fraud chance"),
                (71, 80, "Up to 10% fraud chance"),
                (81, 100, "Only the Success Campaign Reports")
            ]:
                if low <= pct <= high:
                    return comment
            return ""
        display_df["Comment"] = summary["Success %"].apply(get_comment)

    st.markdown("### 📋 Summary Table")
    display_df.index = range(1, len(display_df) + 1)
    st.dataframe(display_df, use_container_width=True)

    # Bar Chart
    chart_data = summary.copy().sort_values("Success %", ascending=False)
    chart_data["Success % Label"] = chart_data["Success %"].apply(lambda x: f"{x:.1f} %")

    fig = px.bar(
        chart_data,
        x=group_by,
        y="Success %",
        text="Success % Label",
        color="Success %",
        color_continuous_scale="Viridis",
        title=f"{group_by}-wise Success %"
    )

    fig.update_traces(
        texttemplate="<b>%{text}</b>",
        textposition="inside",
        insidetextanchor="end"
    )

    fig.update_layout(
        yaxis_title="Success %",
        xaxis_title=group_by,
        uniformtext_minsize=8,
        uniformtext_mode='hide'
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("📌 Not enough data to display summary or metrics.")
