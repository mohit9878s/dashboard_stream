import streamlit as st
import pandas as pd
import plotly.express as px
from jarvis_logo import jarvis_logo
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import pytz
from collections import defaultdict


jarvis_png=jarvis_logo()
comment_cols='Comments (by Gaurav Kumar)'
india_time = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

# Wide layout ke liye
st.set_page_config( page_title="Mera Dashboard",    layout="wide" )

#### ------ Page Config View ------
st.set_page_config(page_title="Communication Dashboard", layout="wide", initial_sidebar_state='auto')
### Reduce top blank space using custom CSS
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem !important;
        }
    </style>
""", unsafe_allow_html=True)
#### ------ Page Config View ------


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

# Auto App refresh every 3 hours
st_autorefresh(interval=3 * 60 * 60 * 1000, key="datarefresh")

###### ----- data read ------------- Google Sheet  ------------
###### ----- data read ------------- Google Sheet  ------------
###### ----- data read ------------- Google Sheet  ------------
@st.cache_data(ttl=60)
def load_data(sheet_url):
    try:
        csv_export_url = sheet_url.replace("/edit#gid=", "/export?format=csv&gid=")
        df = pd.read_csv(csv_export_url)
        df.columns=df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"❌ Failed to fetch data: {e}")
        return None

dashboard_data = "https://docs.google.com/spreadsheets/d/1PAmuXQHqkVE5r0OjMwyvlxDS-O4e8CzBo8auI4uVYCA/edit#gid=1379708796"
### dashboard_data_columns=['State', 'Type of Communication', 'Vendor Name', 'Election Type', 'Cohort', 'Total Phone Numbers', 'Total Success']
df = load_data(dashboard_data)
if df is None:
    st.stop()


comment_remark = "https://docs.google.com/spreadsheets/d/1PAmuXQHqkVE5r0OjMwyvlxDS-O4e8CzBo8auI4uVYCA/edit#gid=1826238917"
### comment_remark_columns=['Type of Communication','Vendor','Percentage Range', 'Comment Remark']
remark_df = load_data(comment_remark)
if remark_df is None:
    st.stop()
###### ----- data read ------------- Google Sheet  ------------
###### ----- data read ------------- Google Sheet  ------------
###### ----- data read ------------- Google Sheet  ------------


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

with st.sidebar:
    # st.markdown("#### 🧾 Options")
    show_remarks = st.toggle("Show Vendor-wise Remarks", value=False)
    # st.warning("Please select **only one Communication Type (OBD or WhatsApp)** to view remarks.")


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

########-------- vendor comment function-------------
########-------- vendor comment function-------------
def get_comment(success_pct, vendor, comm_type, remark_df):
    vendor = vendor.strip().lower()
    comm_type = comm_type.strip().lower()
    pct = round(success_pct)

    # Filter for matching communication type
    df = remark_df[  remark_df["Type of Communication"].str.strip().str.lower() == comm_type  ]

    if df.empty:
        return "-"

    matched_rows = df[df["Vendor"].str.strip().str.lower() == vendor]

    if matched_rows.empty:
        return "-"

    for _, row in matched_rows.iterrows():
        range_str = row["Percentage Range"]
        remark = row["Comment Remark"]

        # Parse range like "0-20 %" or "81-100 %" or "0-35 %"
        try:
            numbers = [int(s.strip().replace("%", "")) for s in range_str.split("-")]
            if len(numbers) == 2 and numbers[0] <= pct <= numbers[1]:
                return remark
        except:
            continue

    return "-"
########-------- vendor comment function-------------
########-------- vendor comment function-------------


#### ----------    Apply Filters Mode -----------------
#### ----------    Apply Filters Mode -----------------
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
#### ----------    Apply Filters Mode -----------------
#### ----------    Apply Filters Mode -----------------


######---- Summary Table Add columns Success (%) and comment ------------------
######---- Summary Table Add columns Success (%) and comment ------------------
if not filtered_df.empty:
    group_by = st.selectbox("📂 Group Data By", ["Vendor Name", "State", "Cohort","Election Type"])
    summary = filtered_df.groupby(group_by)[["Total Phone Numbers", "Total Success"]].sum().reset_index()
    summary["Success %"] = summary.apply(lambda row: (row["Total Success"] / row["Total Phone Numbers"] * 100)
                                        if row["Total Phone Numbers"] > 0 else 0, axis=1).round(2)
    if isinstance(comm_selected, list) and len(comm_selected) == 1 and group_by == "Vendor Name":
        comm = comm_selected[0]
        summary[comment_cols] = summary.apply(
            lambda row: get_comment(row["Success %"], row["Vendor Name"], comm, remark_df),
            axis=1
        )
######---- Summary Table Add columns Success (%) and comment ------------------
######---- Summary Table Add columns Success (%) and comment ------------------



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


###------ Applied Filters Display -------------
###------ Applied Filters Display -------------
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
        st.markdown("###### 🔎 Filters Applied:")
        for f in filtered_df:
            st.markdown(f"<p>{f}</p>", unsafe_allow_html=True)
###------ Applied Filters Display -------------
###------ Applied Filters Display -------------

###------ Display Summary Table ----------------
###------ Display Summary Table ----------------
    st.markdown("###### 📋 Summary Table")
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
###------ Display Summary Table ----------------
###------ Display Summary Table ----------------

###------ Display Bar Chart Summary Table ----------------
###------ Display Bar Chart Summary Table ----------------
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

###------ Display Bar Chart Summary Table ----------------
###------ Display Bar Chart Summary Table ----------------

st.write("")

#################-------Best----- toggle enable all types of work view vendor remarks -----------------------------------
###########-------Display Vendors wise Comment remarks Summary -----------------------------------
###########-------Display Vendors wise Comment remarks Summary -----------------------------------
if show_remarks:
    # Decide what types of communication to show
    if isinstance(comm_selected, list) and len(comm_selected) > 0:
        comm_types_to_show = comm_selected  # Show selected only
    else:
        comm_types_to_show = remark_df["Type of Communication"].dropna().unique()

    for comm_type in comm_types_to_show:
        comm_data = remark_df[remark_df["Type of Communication"].str.lower() == comm_type.lower()]

        # ✅ Apply vendor filter if vendors are selected
        if selected_vendors:
            selected_vendors_clean = [v.strip().lower() for v in selected_vendors]
            comm_data = comm_data[comm_data["Vendor"].str.strip().str.lower().isin(selected_vendors_clean)]

        if comm_data.empty:
            continue

        st.markdown(f"##### 📋 {comm_type} Vendor-wise Remarks")

        # Group vendors with same remarks
        remark_signature_map = defaultdict(list)
        for vendor in comm_data["Vendor"].dropna().unique():
            temp = comm_data[comm_data["Vendor"] == vendor]
            pattern = tuple(zip(temp["Percentage Range"], temp["Comment Remark"]))
            remark_signature_map[pattern].append(vendor)

        # Build HTML Table
        full_html = """
        <style>
        table.remark-table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 30px;
            font-size: 15px;
        }
        table.remark-table th, table.remark-table td {
            border: 1px solid #ccc;
            padding: 4px;
        }
        table.remark-table th {
            background-color: #f0f0f0;
            text-align: center;
        }
        table.remark-table td.vendor-cell {
            text-align: center;
            vertical-align: middle;
            font-weight: 600;
            white-space: pre-wrap;
            background-color: #f9f9f9;
        }
        </style>
        <table class="remark-table">
        <thead>
        <tr>
            <th>Vendor</th>
            <th>Percentage Range</th>
            <th>Comment Remark</th>
        </tr>
        </thead>
        <tbody>
        """

        for pattern, vendor_list in remark_signature_map.items():
            vendor_html = ",<br>".join(vendor_list)
            rowspan = len(pattern)
            first = True
            for prange, comment in pattern:
                full_html += "<tr>"
                if first:
                    full_html += f'<td class="vendor-cell" rowspan="{rowspan}">{vendor_html}</td>'
                    first = False
                full_html += f"<td>{prange}</td><td>{comment}</td></tr>"

        full_html += "</tbody></table>"
        st.markdown(full_html, unsafe_allow_html=True)

else:
    st.write("")
###########-------Display Vendors wise Comment remarks Summary -----------------------------------
###########-------Display Vendors wise Comment remarks Summary -----------------------------------

