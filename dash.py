
import streamlit as st
import pandas as pd
import plotly.express as px
from jarvis_logo import jarvis_logo
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import pytz


jarvis_png=jarvis_logo()
comment_cols='Comments (by Gaurav Kumar)'
india_time = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

# Wide layout ke liye
st.set_page_config(
    page_title="Mera Dashboard",
    layout="wide"
)

# CSS to hide only GitHub button
hide_github_only = """
    <style>
    /* Hide only GitHub/Fork button from top-right */
    a[href^="https://github.com"] {
        visibility: hidden;
    }
    </style>
"""
st.markdown(hide_github_only, unsafe_allow_html=True)



#### ------ Page View ------
### Page Config
st.set_page_config(page_title="Communication Dashboard", layout="wide", initial_sidebar_state='auto')
### Reduce top blank space using custom CSS
st.markdown("""
    <style>
        .block-container {
            padding-top: 0.8rem !important;
        }
    </style>
""", unsafe_allow_html=True)
#### ------ Page View ------



##### ------ Header UI jarvis logo  Communication Dashboard ----------
st.markdown(f"""
    <div style='margin-top: 1rem; display: flex; align-items: center; justify-content: space-between; padding: 0.1px 20px;'>
        <div><img src='data:image/webp;base64,{jarvis_png}' width='55'/></div>
        <div style='text-align: center; flex-grow: 1;'>
            <span style='font-size: 28px; font-weight: bold;
                background: linear-gradient(90deg, #ff9900, #ff6600);
                -webkit-background-clip: text; color: transparent;
                text-shadow: 0 0 0 rgba(255,102,0,0.1);'>
                Communication Dashboard
            </span>
        </div>
        <div></div>
    </div>
""", unsafe_allow_html=True)
##### ------ Header UI jarvis logo  Communication Dashboard ----------


##### ------ Excel csv file read -------------
# @st.cache_data(ttl=60)      # Load Excel with auto-refresh every 60 seconds
# def load_data():
#     try:
#         df = pd.read_csv(r"data.csv")
#         required = ["State", "Vendor Name", "Type of Communication", "Cohort", "Total Phone Numbers", "Total Success"]
#         if not all(col in df.columns for col in required):
#             st.error("Excel file missing required columns.")
#             return None
#         return df
#     except Exception as e:
#         st.error(f"Error loading Excel: {e}")
#         return None
# df = load_data()
# if df is None:
#     st.stop()
##### ------ Excel csv file read -------------

###### -------- Google Sheet read ------------
sheet_url = "https://docs.google.com/spreadsheets/d/1PAmuXQHqkVE5r0OjMwyvlxDS-O4e8CzBo8auI4uVYCA/edit#gid=1379708796"
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
###### -------- Google Sheet read ------------


# Auto App refresh every 3 hours
st_autorefresh(interval=3 * 60 * 60 * 1000, key="datarefresh")

# Required columns check
required_columns = ["State", "Vendor Name", "Type of Communication", "Cohort","Election Type" ,"Total Phone Numbers", "Total Success"]
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    st.warning(f"⚠️ Some columns are missing in the sheet: {', '.join(missing_columns)}.")


# Sidebar - Communication Filter
with st.sidebar:
    st.markdown("### 📨 Type of Communication")
    comm_options = sorted(df["Type of Communication"].dropna().unique())
    select_all = st.checkbox("Select All Communication Types")
    comm_selected = comm_options if select_all else st.pills("Filter Communication Types", comm_options, selection_mode="multi")


####--- 1 --- Sidebar - Other filters -----
for key in ["election_filter","state_filter", "vendor_filter", "cohort_filter"]:
    if key not in st.session_state:
        st.session_state[key] = []
with st.sidebar:
    with st.expander("🎛️ Apply Filters", expanded=True):
        if st.button("❌ Clear Filters"):
            st.session_state.election_filter = []
            st.session_state.state_filter = []
            st.session_state.vendor_filter = []
            st.session_state.cohort_filter = []
        election_options = sorted(df["Election Type"].dropna().unique())    
        state_options = sorted(df["State"].dropna().unique())
        vendor_options = sorted(df["Vendor Name"].dropna().unique())
        cohort_options = sorted(df["Cohort"].dropna().unique())
        selected_elections = st.multiselect("🗓️ Election Type", election_options, default=st.session_state.election_filter, key="election_filter")
        selected_states = st.multiselect("📍 State", state_options, default=st.session_state.state_filter, key="state_filter")
        selected_vendors = st.multiselect("🏷️ Vendor", vendor_options, default=st.session_state.vendor_filter, key="vendor_filter")
        selected_cohorts = st.multiselect("🎯 Cohort", cohort_options, default=st.session_state.cohort_filter, key="cohort_filter")
#####--- 1 --- Sidebar - Other filters -----

########---- 2 --- check box Select All & unselect -------
# with st.sidebar:
#     with st.expander("🎛️ Apply Filters", expanded=True):
#         # ------------ 📍 State Filter ------------
#         state_options = sorted(df["State"].dropna().unique())
#         if "selected_states" not in st.session_state:
#             st.session_state.selected_states = []
#         if "select_all_states" not in st.session_state:
#             st.session_state.select_all_states = False
#         def toggle_states():
#             if st.session_state.select_all_states:
#                 st.session_state.selected_states = state_options
#             else:
#                 st.session_state.selected_states = []
#         st.checkbox(" Select All States", value=st.session_state.select_all_states, key="select_all_states", on_change=toggle_states)
#         selected_states = st.multiselect("📍 State", state_options, default=st.session_state.selected_states, key="state_multi")
#         st.session_state.selected_states = selected_states
#         # ------------ 🏷️ Vendor Filter ------------
#         vendor_options = sorted(df["Vendor Name"].dropna().unique())
#         if "selected_vendors" not in st.session_state:
#             st.session_state.selected_vendors = []
#         if "select_all_vendors" not in st.session_state:
#             st.session_state.select_all_vendors = False
#         def toggle_vendors():
#             if st.session_state.select_all_vendors:
#                 st.session_state.selected_vendors = vendor_options
#             else:
#                 st.session_state.selected_vendors = []
#         st.checkbox(" Select All Vendors", value=st.session_state.select_all_vendors, key="select_all_vendors", on_change=toggle_vendors)
#         selected_vendors = st.multiselect("🏷️ Vendor", vendor_options, default=st.session_state.selected_vendors, key="vendor_multi")
#         st.session_state.selected_vendors = selected_vendors
#         # ------------ 🎯 Cohort Filter ------------
#         cohort_options = sorted(df["Cohort"].dropna().unique())
#         if "selected_cohorts" not in st.session_state:
#             st.session_state.selected_cohorts = []
#         if "select_all_cohorts" not in st.session_state:
#             st.session_state.select_all_cohorts = False
#         def toggle_cohorts():
#             if st.session_state.select_all_cohorts:
#                 st.session_state.selected_cohorts = cohort_options
#             else:
#                 st.session_state.selected_cohorts = []
#         st.checkbox(" Select All Cohorts", value=st.session_state.select_all_cohorts, key="select_all_cohorts", on_change=toggle_cohorts)
#         selected_cohorts = st.multiselect("🎯 Cohort", cohort_options, default=st.session_state.selected_cohorts, key="cohort_multi")
#         st.session_state.selected_cohorts = selected_cohorts
########---- 2 --- check box Select All & unselect -------



#########  Number Decimal Format & Dashboard Update ---------
with st.sidebar:
    st.markdown("---")
    compact_style = "comma"
    format_option = st.pills("Show Number Format As", ["Decimal Format ( e.g. 1.1 : K, L, Cr )"])
    if format_option:
        compact_style = "compact"


    st.markdown("#### 📊 Dashboard Update")
    if st.button("🔄 Click Refresh"):
        st.cache_data.clear()
        st.rerun()
#########  Number Decimal Format & Dashboard Update ---------




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
def get_comment(success_pct, vendor, comm_type):
    vendor = vendor.strip().lower()
    comm_type = comm_type.strip().lower()
    pct = round(success_pct)


    rr_vendors = ["rr communication", "go2market", "half circle", "cosmic", "inbox media"]
    sarv_vendors = ["sarv", "jio"]
    riddhi_vendors = ["riddhi tech"]
    netcore_vendors = ["netcore"]
    whatsapp_vendors = ["vphone", "inbox media"]


    if comm_type == "obd":
        if vendor in rr_vendors:
            if 0 <= pct <= 35:
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


    elif comm_type == "whatsapp":
        if vendor in whatsapp_vendors:
            if 0 <= pct <= 30:
                return "Runs on only 50% Data"
            elif 31 <= pct <= 50:
                return "Run on only 75% Data"
            elif 51 <= pct <= 82:
                return "Runs perfectly"
            elif 83 <= pct <= 90:
                return "5% chances of fraud"
            elif 91 <= pct <= 100:
                return "10% chances of fraud"
    return "-"


#### -----    Apply Filters
filtered_df = df.copy()

if selected_elections:
    filtered_df = filtered_df[filtered_df["Election Type"].isin(selected_elections)]
if selected_states:
    filtered_df = filtered_df[filtered_df["State"].isin(selected_states)]
if selected_vendors:
    filtered_df = filtered_df[filtered_df["Vendor Name"].isin(selected_vendors)]
if selected_cohorts:
    filtered_df = filtered_df[filtered_df["Cohort"].isin(selected_cohorts)]
if comm_selected:
    filtered_df = filtered_df[filtered_df["Type of Communication"].isin(comm_selected)]




######---- Summary Table Add columns Success (%) and comment -----
if not filtered_df.empty:
    group_by = st.selectbox("📂 Group Data By", ["Vendor Name", "State", "Cohort","Election Type"])
    summary = filtered_df.groupby(group_by)[["Total Phone Numbers", "Total Success"]].sum().reset_index()
    summary["Success %"] = summary.apply(lambda row: (row["Total Success"] / row["Total Phone Numbers"] * 100)
                                        if row["Total Phone Numbers"] > 0 else 0, axis=1).round(2)


    # Apply accurate comment logic only when grouped by Vendor Name and communication selected
    if len(comm_selected) == 1 and comm_selected[0] in ["OBD","WhatsApp"] and group_by == "Vendor Name":      #"WhatsApp"
        summary[comment_cols] = summary.apply(lambda row: get_comment(row["Success %"], row["Vendor Name"], comm_selected[0]), axis=1)


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


### --- Applied Filters Display ----
    filtered_df = []
    if selected_elections:
        filtered_df.append(f"<span style='color:#EF6C00;'>Election Type:</span> {', '.join(selected_elections)}")
    if selected_states:
        filtered_df.append(f"<span style='color:#2980b9;'>State:</span> {', '.join(selected_states)}")
    if selected_vendors:
        filtered_df.append(f"<span style='color:#f39c12;'>Vendors:</span> {', '.join(selected_vendors)}")
    if selected_cohorts:
        filtered_df.append(f"<span style='color:#8e44ad;'>Cohorts:</span> {', '.join(selected_cohorts)}")
    if comm_selected:
        filtered_df.append(f"<span style='color:#FF00FF;'>Communication:</span> {', '.join(comm_selected)}")
    if filtered_df:
        st.markdown("#### 🔎 Filters Applied:")
        for f in filtered_df:
            st.markdown(f"<p>{f}</p>", unsafe_allow_html=True)
### --- Applied Filters Display ----




    st.markdown("### 📋 Summary Table")
    display_df = summary.copy()
    if compact_style == "compact":
        display_df["Total Phone Numbers"] = summary["Total Phone Numbers"].apply(format_compact_decimal)
        display_df["Total Success"] = summary["Total Success"].apply(format_compact_decimal)
    else:
        display_df["Total Phone Numbers"] = summary["Total Phone Numbers"].apply(format_indian_number)
        display_df["Total Success"] = summary["Total Success"].apply(format_indian_number)


    display_df["Success %"] = summary["Success %"].apply(lambda x: f"{x:.0f} %")
    if comment_cols in summary.columns:
        display_df[comment_cols] = summary[comment_cols]


    display_df.index = range(1, len(display_df) + 1)
    st.dataframe(display_df, use_container_width=True)


    # Chart
    chart_data = summary.copy().sort_values("Success %", ascending=False)
    chart_data["Success %"] = chart_data["Success %"].apply(lambda x: f"{x:.0f} %")




    chart_data["Total Data (Compact)"] = chart_data["Total Phone Numbers"].apply(format_compact_decimal)
    chart_data["Total Success (Compact)"] = chart_data["Total Success"].apply(format_compact_decimal)




    fig = px.bar(
        chart_data,
        x=group_by,
        y="Success %",
        text="Success %",
        color=group_by,
        color_continuous_scale="Viridis",
        title=f"{group_by}-wise Success %",
        custom_data=["Total Data (Compact)", "Total Success (Compact)"]
    )


    fig.update_traces(
        texttemplate="<b>%{text}</b>",
        textposition="inside",
        insidetextanchor="end",
        hovertemplate=
            group_by + ": %{x}<br>" +
            "Success %: %{y}<br>" +
            "Total Data: %{customdata[0]}<br>" +
            "Total Success: %{customdata[1]}<extra></extra>"
    )


    fig.update_layout(
        yaxis_title="Success %",
        xaxis_title=group_by,
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        margin=dict(t=40, b=50),  # Top & bottom padding
        height=400,                # Custom height
        showlegend=False
    )


    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("📌 Not enough data to display summary or metrics.")




