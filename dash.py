
import streamlit as st, pandas as pd, plotly.express as px, pytz, time,base64
from main_logo import  dashboard_logo, jarvis_logo, map_logo
from main_number_format import format_indian_number, format_compact_decimal
from streamlit_autorefresh import st_autorefresh
from collections import defaultdict
from datetime import datetime


jarvis_png = jarvis_logo()
bihar_map = map_logo()

comment_cols='Comments (by Gaurav Kumar)'
india_time = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

#### ------------ google sheet read function
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


def csv_read_drive(csv_file_url: str):
    try:
        url=f"https://drive.google.com/uc?id={csv_file_url}"
        df = pd.read_csv(url, on_bad_lines="skip")
        # df = pd.read_csv(csv_file_url)
        df.columns=df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"❌ Failed to fetch data: {e}")
        return None


###### ------------- Vendor-wise Comment Function 
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

        # Parse range like "0-19 %" or "81-100 %" or "0-35 %"
        try:
            numbers = [int(s.strip().replace("%", "")) for s in range_str.split("-")]
            if len(numbers) == 2 and numbers[0] <= pct <= numbers[1]:
                return remark
        except:
            continue

    return "-"
#######---------- --------- Def Function --------------------#############
#######---------- --------- Def Function --------------------#############

###### ----- data read ------------- Google Sheet  ------------
###### ----- data read ------------- Google Sheet  ------------

# dashboard_data      = "https://docs.google.com/spreadsheets/d/1PAmuXQHqkVE5r0OjMwyvlxDS-O4e8CzBo8auI4uVYCA/edit#gid=1379708796"
comment_remark      = "https://docs.google.com/spreadsheets/d/1PAmuXQHqkVE5r0OjMwyvlxDS-O4e8CzBo8auI4uVYCA/edit#gid=1826238917"
dashboard_data      = "1qON87wYekQB6WVHnSlvpYeKh1kN1g7NH"
# dashboard_data      = "Bihar_LSE_2024.csv"

### dashboard_data_columns=['State', 'Type of Communication', 'Vendor', 'Election Type', 'Cohort', 'Total Phone Numbers', 'Total Success']
# df = load_data(dashboard_data)

df=csv_read_drive(dashboard_data)
try:
    df = df.dropna(subset=['State'])
except:
    df
if df is None:
    st.stop()

### comment_remark_columns=['Type of Communication','Vendor','Percentage Range', 'Comment Remark']
remark_df = load_data(comment_remark)
if remark_df is None:
    st.stop()

###### ----- data read ------------- Google Sheet  ------------


######## ------------------ Header Desingn -----------------------------
## Page Config
st.set_page_config(page_title="Communication Dashboard", layout="wide", initial_sidebar_state='auto')
## Reduce top blank space using custom CSS
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem !important;
        }
    </style>
""", unsafe_allow_html=True)

######## ------------------ Header Desingn -----------------------------
st.set_page_config(page_title="Communication Dashboard", layout="wide", initial_sidebar_state='auto')
st.markdown("""
    <style>.block-container {padding-top: 1rem !important;}</style>
""", unsafe_allow_html=True)

##-- headr.html file --- 
with open("header.html", "r") as f:
    html_content = f.read()
html_content = html_content.replace("{{ jarvis_png }}", jarvis_png)
html_content = html_content.replace("{{ bihar_map }}", bihar_map)
st.markdown(html_content, unsafe_allow_html=True)


# st.markdown(f"""
#     <div style='margin-top: 1rem; display: flex; align-items: center; justify-content: space-between; padding: 0.1px 40px;'>
#         <div><img src='data:image/webp;base64,{jarvis_png}' width='55'/></div>
#         <div style='text-align: center; flex-grow: 1;'>
#             <span style='font-size: 30px; font-weight: bold;
#                 background: linear-gradient(90deg, #ff9900, #ff6600);
#                 -webkit-background-clip: text; color: transparent;
#                 text-shadow: 0 0 0 rgba(255,102,0,0.1);'>
#                 Bihar Communication Dashboard
#             </span>
#         </div>
#         <div></div>
#     </div>
# """, unsafe_allow_html=True)

######## ------------------ Header Desingn -----------------------------


######## ------------------ Page Line line Desingn -----------------------------
st.markdown(
    """
    <div style="
        height: 1.5px;
        background: linear-gradient(90deg, #ff9900, #ff6600);
        margin-top: 2px;
        margin-bottom: 19px;
        border-radius: 4px;">
    </div>
    """,
    unsafe_allow_html=True)
######## ------------------ Page Line line Desingn -----------------------------
######## ------------------ Page Line line Desingn -----------------------------


required_columns = ['State','District','PC No. & Name', 'AC No. & Name', 'Booth No.',
       'Type of Communication', 'Vendor', 'Election Type', 'Cohort', 'Gender',
       'Age', 'Type of Campaign', 'Total Phone Numbers', 'Total Success',
       'Data Type']
       
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    st.warning(f"⚠️ Some columns are missing in the sheet: {', '.join(missing_columns)}.")

with st.sidebar:
    comm_options = sorted(df["Type of Communication"].dropna().unique())
    comm_selected = st.pills("**Filter Communication Types**", comm_options, selection_mode="multi")


# Sidebar - Communication Filter
with st.sidebar:
    group_by = st.selectbox("📂 Analyze Data By", ["Vendor","Cohort","District","PC No. & Name", "AC No. & Name", "Booth No.",
                                                    "Type of Campaign" ,"Gender","Age"])
    show_remarks = st.toggle("Show Vendor-wise Remarks", value=False)

####--- 1 --- Sidebar - filters options -----
for key in ["election_filter","state_filter","vendor_filter", "cohort_filter","dist_filter","pc_filter",
            "ac_filter","booth_filter","gender_filter","age_filter","campaign_filter","data_type_filter"]:
    if key not in st.session_state:
        st.session_state[key] = []

with st.sidebar:
    if st.button("❌ Clear Filters"):
        st.session_state.election_filter = []
        st.session_state.state_filter = []
        st.session_state.vendor_filter = []
        st.session_state.cohort_filter = []
        st.session_state.dist_filter = []
        st.session_state.pc_filter = []
        st.session_state.ac_filter = []
        st.session_state.booth_filter = []
        st.session_state.gender_filter = []
        st.session_state.age_filter = []
        st.session_state.campaign_filter = []
        st.session_state.data_type_filter = []

# Dynamic options WITHOUT applying own filter
    def get_filtered_options(exclude_filter=None):
        temp_df = df.copy()
        if comm_selected:
            temp_df = temp_df[temp_df["Type of Communication"].isin(comm_selected)]
        if exclude_filter != "election" and st.session_state.election_filter:
            temp_df = temp_df[temp_df["Election Type"].isin(st.session_state.election_filter)]
        if exclude_filter != "state" and st.session_state.state_filter:
            temp_df = temp_df[temp_df["State"].isin(st.session_state.state_filter)]
        if exclude_filter != "vendor" and st.session_state.vendor_filter:
            temp_df = temp_df[temp_df["Vendor"].isin(st.session_state.vendor_filter)]
        if exclude_filter != "cohort" and st.session_state.cohort_filter:
            temp_df = temp_df[temp_df["Cohort"].isin(st.session_state.cohort_filter)]
        if exclude_filter != "dist" and st.session_state.pc_filter:
            temp_df = temp_df[temp_df["District"].isin(st.session_state.dist_filter)]
        if exclude_filter != "pc" and st.session_state.pc_filter:
            temp_df = temp_df[temp_df["PC No. & Name"].isin(st.session_state.pc_filter)]
        if exclude_filter != "ac" and st.session_state.ac_filter:
            temp_df = temp_df[temp_df["AC No. & Name"].isin(st.session_state.ac_filter)]
        if exclude_filter != "booth" and st.session_state.booth_filter:
            temp_df = temp_df[temp_df["Booth No."].isin(st.session_state.booth_filter)]
        if exclude_filter != "gender" and st.session_state.gender_filter:
            temp_df = temp_df[temp_df["Gender"].isin(st.session_state.gender_filter)]
        if exclude_filter != "age" and st.session_state.age_filter:
            temp_df = temp_df[temp_df["Age"].isin(st.session_state.age_filter)]
        if exclude_filter != "campaign" and st.session_state.campaign_filter:
            temp_df = temp_df[temp_df["Type of Campaign"].isin(st.session_state.campaign_filter)]

        return temp_df

election_options = sorted(get_filtered_options(exclude_filter="election")["Election Type"].dropna().unique())
state_options    = sorted(get_filtered_options(exclude_filter="state")["State"].dropna().unique())
vendor_options   = sorted(get_filtered_options(exclude_filter="vendor")["Vendor"].dropna().unique())
cohort_options   = sorted(get_filtered_options(exclude_filter="cohort")["Cohort"].dropna().unique())
district_options = sorted(get_filtered_options(exclude_filter="dist")["District"].dropna().unique())
pc_options       = sorted(get_filtered_options(exclude_filter="pc")["PC No. & Name"].dropna().unique())
ac_options       = sorted(get_filtered_options(exclude_filter="ac")["AC No. & Name"].dropna().unique())
booth_options    = sorted(get_filtered_options(exclude_filter="booth")["Booth No."].dropna().unique())
gender_options   = sorted(get_filtered_options(exclude_filter="gender")["Gender"].dropna().unique())
age_options      = sorted(get_filtered_options(exclude_filter="age")["Age"].dropna().unique())
campaign_options = sorted(get_filtered_options(exclude_filter="campaign")["Type of Campaign"].dropna().unique())

# 3. Validate defaults
valid_election_defaults     = [v for v in st.session_state.election_filter if v in election_options]
valid_state_defaults        = [v for v in st.session_state.state_filter if v in state_options]
valid_vendor_defaults       = [v for v in st.session_state.vendor_filter if v in vendor_options]
valid_cohort_defaults       = [v for v in st.session_state.cohort_filter if v in cohort_options]
valid_district_defaults     = [v for v in st.session_state.dist_filter if v in district_options]
valid_pc_defaults           = [v for v in st.session_state.pc_filter if v in pc_options]
valid_ac_defaults           = [v for v in st.session_state.ac_filter if v in ac_options]
valid_booth_defaults        = [v for v in st.session_state.booth_filter if v in booth_options]
valid_gender_defaults       = [v for v in st.session_state.gender_filter if v in gender_options]
valid_age_defaults          = [v for v in st.session_state.age_filter if v in age_options]
valid_campaign_defaults     = [v for v in st.session_state.campaign_filter if v in campaign_options]


if (
    not any([election_options, state_options, vendor_options, cohort_options,pc_options,ac_options,
            booth_options,gender_options,age_options,campaign_options]) or
    (st.session_state.election_filter and not valid_election_defaults) or
    (st.session_state.state_filter and not valid_state_defaults) or
    (st.session_state.vendor_filter and not valid_vendor_defaults) or
    (st.session_state.cohort_filter and not valid_cohort_defaults) or
    (st.session_state.dist_filter and not valid_district_defaults) or
    (st.session_state.pc_filter and not valid_pc_defaults) or
    (st.session_state.ac_filter and not valid_ac_defaults) or
    (st.session_state.booth_filter and not valid_booth_defaults) or
    (st.session_state.gender_filter and not valid_gender_defaults) or
    (st.session_state.age_filter and not valid_age_defaults) or
    (st.session_state.campaign_filter and not valid_campaign_defaults)

):
    st.error("❌ No data found. Please clear some sidebar filters to continue.")
    st.stop()

# -------------------- Filters in Single Line --------------------
with st.expander("**Apply Filters**",expanded=True,width='stretch',icon="🔽"):
    c0, c8 , c1, c2 = st.columns(4)
    c3, c4, c7, c5, c6 = st.columns(5)

    with c0:
        selected_vendors = st.multiselect("🏷️ Vendor", vendor_options, default=st.session_state.vendor_filter, key="vendor_filter")
    
    with c1:
        selected_district = st.multiselect("📍 District", district_options, default=st.session_state.dist_filter, key="dist_filter")

    with c2:
        selected_pcs = st.multiselect("🏛️ PC No. & Name", pc_options, default=st.session_state.pc_filter, key="pc_filter")

    with c3:
        selected_acs = st.multiselect("📌 AC No. & Name", ac_options, default=st.session_state.ac_filter, key="ac_filter")

    with c4:
        selected_booths = st.multiselect("🏠 Booth No.", booth_options, default=st.session_state.booth_filter, key="booth_filter")

    with c5:
        selected_genders = st.multiselect("⚧ Gender", gender_options, default=st.session_state.gender_filter, key="gender_filter")

    with c6:
        selected_ages = st.multiselect("🎂 Age", age_options, default=st.session_state.age_filter, key="age_filter")

    with c7:
        selected_campaign = st.multiselect("📢 Type of Campaign", campaign_options, default=st.session_state.campaign_filter, key="campaign_filter")

    with c8:
        selected_cohorts = st.multiselect("🎯 Cohort", cohort_options, default=st.session_state.cohort_filter, key="cohort_filter")

# st.markdown("---")  # separator line


#####--- 1 --- Sidebar - filters options -----



#########  sidebar Button  (Decimal Number Format ( e.g. 1.1 : K, L, Cr )---------
#########  sidebar Button  (Decimal Number Format ( e.g. 1.1 : K, L, Cr )---------
with st.sidebar:
    # st.markdown("---")
    compact_style = "comma"
    format_option = st.pills("Show Number Format As", ["Decimal Format ( e.g. 1.1 : K, L, Cr )"])
    if format_option:
        compact_style = "compact"
#########  sidebar Button  (Decimal Number Format ( e.g. 1.1 : K, L, Cr )---------
#########  sidebar Button  (Decimal Number Format ( e.g. 1.1 : K, L, Cr )---------



#### ----------    Apply Filters Mode -----------------
#### ----------    Apply Filters Mode -----------------
filtered_df = df.copy()
# if selected_elections:
#     filtered_df = filtered_df[filtered_df["Election Type"].isin(selected_elections)]
# if selected_states:
#     filtered_df = filtered_df[filtered_df["State"].isin(selected_states)]
if selected_vendors:
    filtered_df = filtered_df[filtered_df["Vendor"].isin(selected_vendors)]
if selected_cohorts:
    filtered_df = filtered_df[filtered_df["Cohort"].isin(selected_cohorts)]
if selected_district:
    filtered_df = filtered_df[filtered_df["District"].isin(selected_district)]
if selected_pcs:
    filtered_df = filtered_df[filtered_df["PC No. & Name"].isin(selected_pcs)]
if selected_acs:
    filtered_df = filtered_df[filtered_df["AC No. & Name"].isin(selected_acs)]
if selected_booths:
    filtered_df = filtered_df[filtered_df["Booth No."].isin(selected_booths)]
if selected_genders:
    filtered_df = filtered_df[filtered_df["Gender"].isin(selected_genders)]
if selected_ages:
    filtered_df = filtered_df[filtered_df["Age"].isin(selected_ages)]
if selected_campaign:
    filtered_df = filtered_df[filtered_df["Type of Campaign"].isin(selected_campaign)]
if comm_selected:
    filtered_df = filtered_df[filtered_df["Type of Communication"].isin(comm_selected)]

if filtered_df.empty:
    st.info("📌 No data found for selected filters.")
    st.stop()

num_unique_group_by_items = filtered_df[group_by].nunique()
filtered_vendors = ( filtered_df["Vendor"].dropna().str.strip().str.lower().unique().tolist() )

#### ----------    Apply Filters Mode -----------------
#### ----------    Apply Filters Mode -----------------


st.write("")


######---- Summary Table Add columns Success (%) and comment ------------------
######---- Summary Table Add columns Success (%) and comment ------------------

if not filtered_df.empty:
    # --- Define aggregation dictionary ---
    agg_dict = {
        "Total Phone Numbers": "sum",
        "Total Success": "sum",
        "Type of Communication": lambda x: ", ".join(sorted(set(x.dropna())))
    }

    # --- Group by dynamically ---
    summary = filtered_df.groupby(group_by, dropna=False).agg(agg_dict).reset_index()

    # Rename column for display
    summary.rename(columns={"Type of Communication": "Type of Communication(s)"}, inplace=True)

    # --- Calculate Success % ---
    summary["Success %"] = summary.apply(
        lambda row: (row["Total Success"] / row["Total Phone Numbers"] * 100)
        if row["Total Phone Numbers"] > 0 else 0,
        axis=1
    ).round(2)

    # --- Add Vendor-wise comment only if a single communication type is selected ---
    if isinstance(comm_selected, list) and len(comm_selected) == 1 and group_by == "Vendor":
        comm = comm_selected[0]
        summary[comment_cols] = summary.apply(
            lambda row: get_comment(row["Success %"], row["Vendor"], comm, remark_df),
            axis=1
        )        

######---- Summary Table Add columns Success (%) and comment ------------------
######---- Summary Table Add columns Success (%) and comment ------------------

    comm_type_map = (
        filtered_df.groupby(group_by)["Type of Communication"]
        .apply(lambda x: ", ".join(sorted(set(x.dropna()))))
        .reset_index()
        .rename(columns={"Type of Communication": "Type of Communication(s)"})
    )
    summary = pd.merge(summary, comm_type_map, on=group_by, how="left")
    if "Type of Communication(s)_x" in summary.columns:
        summary["Type of Communication(s)"] = summary["Type of Communication(s)_x"].fillna(summary["Type of Communication(s)_y"])
        summary.drop(columns=["Type of Communication(s)_x", "Type of Communication(s)_y"], inplace=True)

    cols = summary.columns.tolist()
    if "Type of Communication(s)" in cols:
        cols.insert(1, cols.pop(cols.index("Type of Communication(s)")))
        summary = summary[cols]




######### --- 📞 Total Phone Number ---------- ☑️ Total Success ----------- 📈 Oveall Success % -----------------------
    total_ph = filtered_df["Total Phone Numbers"].sum()
    total_succ = filtered_df["Total Success"].sum()
    overall_pct = (total_succ / total_ph * 100) if total_ph else 0

    col1, col2, col3 = st.columns(3)
    #---------Best --------------------------------
    with col1:
        st.markdown(f"""
        <div style='text-align:center; line-height:1.1; margin-bottom: 0px;'>
            <div style="font-size: 18px; font-weight: bold; color: Black  #1f4e79 ; margin-bottom: 0px;">
                📞 Total Phone Numbers
            </div>
            <div style='font-size: 26px; font-weight: Bold; color: steelblue;'>{format_compact_decimal(total_ph)}</div>
            <div style='font-size: 28px; font-weight: 600; color: steelblue;'>({format_indian_number(total_ph)})</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style='text-align:center; line-height:1.1; margin-bottom: 0px;'>
            <div style="font-size: 18px; font-weight: bold; color: Black #1f4e79 ; margin-bottom: 0px;">                            
                ☑️ Total Success
            </div>
            <div style='font-size: 26px; font-weight: Bold; color: orangered;'>{format_compact_decimal(total_succ)}</div>
            <div style='font-size: 28px; font-weight: 600; color: orangered;'>({format_indian_number(total_succ)})</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style='text-align:center; line-height:0.9; margin-bottom: 19px;'>
            <div style="font-size: 18px; font-weight: bold; color: Black #1f4e79; margin-bottom: 12px;">
                📈 Overall Success %
            </div>
            <div style='font-size: 40px; font-weight: 650; color:  #80C99F;'>{overall_pct:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)        #color:#83c28c

    st.write(' ')



###------ Applied Filters Display -------------
###------ Applied Filters Display -------------
    filtered_df = []
    def badge(label, color_bg, color_text):
        return (
            f"<span style='"
            f"background-color:{color_bg}; "
            f"color:{color_text}; "
            "padding:4px 8px; "
            "border-radius:6px; "
            "font-weight:600; "
            "font-size:14px;'>"
            f"{label}</span>"
        )
    
    if comm_selected:
        filtered_df.append(
            f'{badge("Communication :", "#d9fafa", "#00c5bb")} '
            f'<span style="font-weight:450;"> &nbsp;&nbsp; {"&nbsp;,&nbsp;&nbsp;&nbsp;".join(comm_selected)}</span>'
        )
    # if selected_elections:
    #     filtered_df.append(
    #         f'{badge("Election Type :", "#f2e5ff", "#7a24c9")} '
    #         f'<span style="font-weight:450;"> &nbsp;&nbsp; {"&nbsp;,&nbsp;&nbsp;&nbsp;".join(selected_elections)}</span>'
    #     )
    if selected_vendors:
        filtered_df.append(
            f'{badge("Vendors :", "#fff4e5", "#f39c12")} '
            f'<span style="font-weight:450;"> &nbsp;&nbsp; {"&nbsp;,&nbsp;&nbsp;&nbsp;".join(selected_vendors)}</span>'
        )
    if selected_cohorts:
        filtered_df.append(
            f'{badge("Cohorts :", "#ffe5ec", "#c20041")} '
            f'<span style="font-weight:450;"> &nbsp;&nbsp; {"&nbsp;,&nbsp;&nbsp;&nbsp;".join(selected_cohorts)}</span>'
        )
    # if selected_states:
    #     filtered_df.append(
    #         f'{badge("State :", "#dfefff", "#2980b9")} '
    #         f'<span style="font-weight:450;"> &nbsp;&nbsp; {"&nbsp;,&nbsp;&nbsp;&nbsp;".join(selected_states)}</span>'
    #     )

    if selected_district:
        filtered_df.append(
            f'{badge("District :", "#e8e5ff", "#000ba1")} '
            f'<span style="font-weight:450;"> &nbsp;&nbsp; {"&nbsp;,&nbsp;&nbsp;&nbsp;".join(selected_district)}</span>'
        )
    if selected_pcs:
        filtered_df.append(
            f'{badge("P C :", "#f2e5ff", "#5300a1")} '
            f'<span style="font-weight:450;"> &nbsp;&nbsp; {"&nbsp;,&nbsp;&nbsp;&nbsp;".join(selected_pcs)}</span>'
        )
    if selected_acs:
        filtered_df.append(
            f'{badge("AC :", "#fff4e5", "#db8802")} '
            f'<span style="font-weight:450;"> &nbsp;&nbsp; {"&nbsp;,&nbsp;&nbsp;&nbsp;".join(selected_acs)}</span>'
        )
    if selected_booths:
        filtered_df.append(
            f'{badge("Booth no. :", "#d9f6fc", "#4d86f0")} '
            f'<span style="font-weight:450;"> &nbsp;&nbsp; {"&nbsp;,&nbsp;,&nbsp;&nbsp;".join(map(str, selected_booths))}</span>'
        )
    if selected_genders:
        filtered_df.append(
            f'{badge("Gender :", "#fff4e5", "#d0902a")} '
            f'<span style="font-weight:450;"> &nbsp;&nbsp; {"&nbsp;,&nbsp;&nbsp;&nbsp;".join(selected_genders)}</span>'
        )
    if selected_ages:
        filtered_df.append(
            f'{badge("Age :", "#fae2e8", "#B0003B")} '
            f'<span style="font-weight:450;"> &nbsp;&nbsp; {"&nbsp;,&nbsp;&nbsp;&nbsp;".join(map(str, selected_ages))}</span>'
        )
    if selected_campaign:
        filtered_df.append(
            f'{badge("campaign Type :", "#f9dff7", "#84005c")} '
            f'<span style="font-weight:450;"> &nbsp;&nbsp; {"&nbsp;,&nbsp;&nbsp;&nbsp;".join(selected_campaign)}</span>'
        )

    if filtered_df:
        st.markdown("""
                    <div style="background-color:#f0f2f676; border-radius:200px; min-height: 100px, min-width: 100px;
                     display: flex; align-items: center; justify-content: center;">
                        <span style='color:Black; font-size:18px; font-weight:550;'>📑Filter Criteria</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        for f in filtered_df:
            st.markdown(f"<div style='margin-bottom:2px;'>{f}</div>", unsafe_allow_html=True)
        st.write("")
 #       st.write("")

###------ Applied Filters Display -------------
###------ Applied Filters Display -------------



###------ Display Bar Chart Summary Table ----------------
###------ Display Bar Chart Summary Table ----------------
# ------------------- Tab-based Chart Display ---------------------
    # Grouping type
    
    chart_data = summary.copy().sort_values("Success %", ascending=False)
    chart_data["Success %"] = chart_data["Success %"].apply(lambda x: f"{x:.0f} %")
    chart_data["Total Data (Compact)"] = chart_data["Total Phone Numbers"].apply(format_compact_decimal)
    chart_data["Total Success (Compact)"] = chart_data["Total Success"].apply(format_compact_decimal)

    custom_data_fields = ["Total Data (Compact)", "Total Success (Compact)", "Type of Communication(s)"]

###------ Display Bar Chart Summary Table ----------------
###------ Display Bar Chart Summary Table ----------------
# ensure Success numeric column exists (works even if you earlier formatted it as "80 %")
    if chart_data["Success %"].dtype == object or chart_data["Success %"].astype(str).str.contains("%").any():
        chart_data["Success_numeric"] = (
            chart_data["Success %"].astype(str).str.replace("%", "").str.strip().replace("", "0").astype(float))
    else:
        chart_data["Success_numeric"] = chart_data["Success %"].astype(float)

    # create a display text column (keeps "80 %" for showing on bars)
    chart_data["Success_display"] = chart_data["Success_numeric"].apply(lambda x: f"{x:.0f} %")

    # ensure Type of Communication(s) exists for hover (fallback handle)
    if "Type of Communication(s)" not in chart_data.columns:
        # try common merged names then fallback to '-'
        chart_data["Type of Communication(s)"] = chart_data.get("Type of Communication(s)_x",
                                                                chart_data.get("Type of Communication(s)_y", "-"))

    # custom data for hover (keep same order as hovertemplate indices)
    custom_data_fields = ["Total Data (Compact)", "Total Success (Compact)", "Type of Communication(s)"]

    # Create bar chart using numeric column for color (single color family shades)
    fig = px.bar(
        chart_data,
        x=group_by,
        y="Success_numeric",            # numeric heights (0..100)
        text="Success_display",         # text shown inside bars
        color="Success_numeric",        # color keyed to numeric value -> continuous shades
        color_continuous_scale=["#fff2e1", "#fd6a30"],  # light -> orsnged (change if needed)
#        color_continuous_scale=["#ffe8e1", "#e87d71"], # light -> red (change if needed)
        range_color=[100, 10],           # force range so shades are distinct
        custom_data=custom_data_fields
    )
    # hide the continuous colorbar if you don't want it displayed

    fig.update_coloraxes(showscale=False)
    # hovertemplate - customdata indices must match custom_data_fields order
    hovertemplate = (
        "Comm.Type: %{customdata[2]}<br>"
        "Total Data: %{customdata[0]}<br>"
        "Total Success: %{customdata[1]}<br>"
        "<extra></extra>"
    )

    fig.update_traces(
        texttemplate="<b>%{text}</b>",
        textposition="inside",
        insidetextanchor="middle",
        hovertemplate=hovertemplate,
        marker_line_width=0
    )

    fig.update_layout(
        title={
            "text": f"<span style='color:#387fc1;'><b>{num_unique_group_by_items}-{group_by} </b></span><span style='font-weight:normal;'> -  wise Success % Chart</span>",
            "y": 0.99, "x": 0.05, "xanchor": "left", "yanchor": "top"
        },
        title_font=dict(size=24),
        yaxis_title="Success %",
        xaxis_title=group_by,
        uniformtext_minsize=10,
        uniformtext_mode='hide',
        margin=dict(t=50, b=60),
        height=450,
        showlegend=True
    )

    ### make y-axis show percent ticks (and limit 0..100)
    # fig.update_yaxes(range=[0, 100], ticksuffix="%")

    st.plotly_chart(fig, use_container_width=True)

##$$$$$$$ -- perfect work--- Show Remarks Vendors only ---- sidebar vendors filter mode  ---
##$$$$$$$ -- perfect work--- Show Remarks Vendors only ---- sidebar vendors filter mode  ---
# Tabs: Conditionally show second tab
    if show_remarks:
        tab1, tab2 = st.tabs(["📊 Summary Table", "🗒️ Vendor-wise Remark Summary"])
    else:
        tab1, = st.tabs(["📊 Summary Table"])

    # ---------- TAB 1: Summary Table ----------
    with tab1:
        # st.markdown("##### 📋 Summary Table")
                
        if not summary.empty:
            # clean numeric columns
            summary["Total Phone Numbers"] = pd.to_numeric(summary["Total Phone Numbers"], errors='coerce')
            summary["Total Success"] = pd.to_numeric(summary["Total Success"], errors='coerce')
            summary["Success %"] = pd.to_numeric(summary["Success %"], errors='coerce')
            summary.index = range(1, len(summary) + 1)
        
            # reset index safely
            summary_display = summary.copy().reset_index(drop=True)
            summary_display.index = range(1, len(summary_display) + 1)
            
        
            # compact vs normal style
            if compact_style == "compact":
                st.dataframe(
                    summary_display.style.format({
                        "Total Phone Numbers": lambda x: format_compact_decimal(int(x)),
                        "Total Success": lambda x: format_compact_decimal(int(x)),
                        "Success %": "{:.0f} %"
                    }),
                    use_container_width=True   # ✅ safer
                )
            else:
                st.dataframe(
                    summary_display.style.format({
                        "Total Phone Numbers": lambda x: format_indian_number(int(x)),
                        "Total Success": lambda x: format_indian_number(int(x)),
                        "Success %": "{:.0f} %"
                    }),
                    use_container_width=True
                )
        else:
            st.info("📌 Not enough data to display summary or metrics.")

    # ---------- TAB 2: Vendor-wise Remark Summary ----------
    if show_remarks:
        with tab2:
            if isinstance(comm_selected, list) and len(comm_selected) > 0:
                comm_types_to_show = comm_selected
            else:
                comm_types_to_show = remark_df["Type of Communication"].dropna().unique()

            for comm_type in comm_types_to_show:
                comm_data = remark_df[remark_df["Type of Communication"].str.lower() == comm_type.lower()]
                comm_data = comm_data[comm_data["Vendor"].str.strip().str.lower().isin(filtered_vendors)]

                if comm_data.empty:
                    continue

                st.markdown(f"##### 📝 {comm_type} Vendor-wise Remarks")

                remark_signature_map = defaultdict(list)
                for vendor in comm_data["Vendor"].dropna().unique():
                    temp = comm_data[comm_data["Vendor"] == vendor]
                    pattern = tuple(zip(temp["Percentage Range"], temp["Comment Remark"]))
                    remark_signature_map[pattern].append(vendor)

                full_html = """
                    <style>
                    table.remark-table {
                        border-collapse: collapse;
                        width: 100%;
                        margin-bottom: 30px;
                        font-size: 12px;
                    }
                    table.remark-table th, table.remark-table td {
                        border: 1px solid #ccc !important;
                        padding: 4px !important;
                    }

                    /* Light mode defaults */
                    table.remark-table th {
                        background-color: #f0f0f0 !important;
                        color: #000000 !important;
                        text-align: center !important;
                    }
                    table.remark-table td.vendor-cell {
                        text-align: center !important;
                        vertical-align: middle !important;
                        font-weight: 600 !important;
                        white-space: pre-wrap !important;
                        background-color: #f9f9f9 !important;
                        color: #000000 !important;
                    }
                    table.remark-table td {
                        background-color: #ffffff !important;
                        color: #000000 !important;
                    }

                    /* Dark mode overrides */
                    @media (prefers-color-scheme: dark) {
                        table.remark-table th {
                            background-color: #333333 !important;
                            color: #ffffff !important;
                        }
                        table.remark-table td.vendor-cell {
                            background-color: #2a2a2a !important;
                            color: #ffffff !important;
                        }
                        table.remark-table td {
                            background-color: #1e1e1e !important;
                            color: #ffffff !important;
                        }
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


##$$$$$$$ -- perfect work--- Show Remarks Vendors only ---- sidebar vendors filter mode  ---
##$$$$$$$ -- perfect work--- Show Remarks Vendors only ---- sidebar vendors filter mode  ---



#########  sidebar Button  🔄 Click Refresh Dashboard Update & 🔴 Sign Out) ---------
#########  sidebar Button  🔄 Click Refresh Dashboard Update & 🔴 Sign Out) ---------

with st.sidebar:
### ---------- Dashboard Update 🔄 Click Refresh
    st.markdown("#### 📊 Dashboard Update")
    if st.button("🔄 Click Refresh"):
        st.cache_data.clear()
        st.rerun()


########### --------- auto refresh timer -------------
########### --------- auto refresh timer -------------

###------⏱️ 1 hour = 3600000 milliseconds
st_autorefresh(interval=3600000, key="auto_logout_refresh")

########### --------- auto refresh timer -------------
########### --------- auto refresh timer -------------

##-- chose colour for desing --
try:st.markdown(f"""<div style="{format(bg1='#e6ffea', bg2="#3697b2", border="#80C99F")}">  </div> """, unsafe_allow_html=True)
except:pass
##-- chose colour for desing --




