
import streamlit as st, pandas as pd, plotly.express as px, pytz, time,base64
from logo import  dashboard_logo, jarvis_logo
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
from collections import defaultdict
import pydeck as pdk
import streamlit.components.v1 as components


jarvis_png  =   jarvis_logo()
comment_cols='Comments (by Gaurav Kumar)'
india_time = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')


####### --------- --------- Def Function --------------------#############
####### --------- --------- Def Function --------------------#############
####### --------- --------- Def Function --------------------#############

# dash_logo   =   st.markdown(f"""
#                                 <style>
#                                 .stApp {{
#                                     background-image: url("data:image/png;base64,{dashboard_logo()}");
#                                     background-repeat: no-repeat;
#                                     background-position: center;
#                                     background-size: 42%;
#                                     opacity: 10;  /* Adjust transparency here */
#                                 }}
#                                 </style>
#                             """, unsafe_allow_html=True)


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

###### ---------- Number Formating functions 
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

def format_compact_number(x):
    if x >= 1e7:
        return f"{x / 1e7:.2f} Cr"
    elif x >= 1e5:
        return f"{x / 1e5:.2f} L"
    elif x >= 1e3:
        return f"{x / 1e3:.2f} K"
    elif x == 0:
        return "0"
    else:
        return f"{x:.0f}"


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
########--------- --------- Def Function --------------------#############




###### ----- data read ------------- Google Sheet  ------------
###### ----- data read ------------- Google Sheet  ------------
###### ----- data read ------------- Google Sheet  ------------

dashboard_data      = "https://docs.google.com/spreadsheets/d/1PAmuXQHqkVE5r0OjMwyvlxDS-O4e8CzBo8auI4uVYCA/edit#gid=1379708796"
comment_remark      = "https://docs.google.com/spreadsheets/d/1PAmuXQHqkVE5r0OjMwyvlxDS-O4e8CzBo8auI4uVYCA/edit#gid=1826238917"
access_user_state   = "https://docs.google.com/spreadsheets/d/1PAmuXQHqkVE5r0OjMwyvlxDS-O4e8CzBo8auI4uVYCA/edit#gid=1217256347"


### dashboard_data_columns=['State', 'Type of Communication', 'Vendor', 'Election Type', 'Cohort', 'Total Phone Numbers', 'Total Success']
df = load_data(dashboard_data)
df = df.dropna(subset=['State'])
if df is None:
    st.stop()



### comment_remark_columns=['Type of Communication','Vendor','Percentage Range', 'Comment Remark']
remark_df = load_data(comment_remark)
if remark_df is None:
    st.stop()



### access_user_state_columns=["password", "access state", "mode"]
user_df = load_data(access_user_state)
user_df.columns = user_df.columns.str.strip().str.lower()
if user_df.empty:
    st.stop()

###### ----- data read ------------- Google Sheet  ------------
###### ----- data read ------------- Google Sheet  ------------
###### ----- data read ------------- Google Sheet  ------------




######## ------------------ Header Desingn -----------------------------
######## ------------------ Header Desingn -----------------------------
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

st.markdown(f"""
    <div style='margin-top: 1rem; display: flex; align-items: center; justify-content: space-between; padding: 0.1px 40px;'>
        <div><img src='data:image/webp;base64,{jarvis_png}' width='55'/></div>
        <div style='text-align: center; flex-grow: 1;'>
            <span style='font-size: 30px; font-weight: bold;
                background: linear-gradient(90deg, #ff9900, #ff6600);
                -webkit-background-clip: text; color: transparent;
                text-shadow: 0 0 0 rgba(255,102,0,0.1);'>
                Communication Dashboard
            </span>
        </div>
        <div></div>
    </div>
""", unsafe_allow_html=True)
######## ------------------ Header Desingn -----------------------------
######## ------------------ Header Desingn -----------------------------
######## ------------------ Header Desingn -----------------------------

######## ------------------ Page Line line Desingn -----------------------------
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


###### ----- Enter Acces Code for State Type  ------------- Communication Dashboard   ------------
###### ----- Enter Acces Code for State Type  ------------- Communication Dashboard   ------------
###### ----- Enter Acces Code for State Type  ------------- Communication Dashboard   ------------
access_map = {}
mode_map = {}
for _, row in user_df.iterrows():
    password = str(row["password"]).strip()
    state = str(row["access state"]).strip()
    mode = str(row["mode"]).strip().lower()

    if password in access_map:
        if access_map[password] != "ALL":
            access_map[password].add(state)
    else:
        if state.upper() == "ALL":
            access_map[password] = "ALL"
        else:
            access_map[password] = {state}

    mode_map[password] = mode

# Convert sets to lists
for key in access_map:
    if access_map[key] != "ALL":
        access_map[key] = list(access_map[key])

###### ✅ 3. Access Control (Before dashboard) ######
if "access_granted" not in st.session_state:
    st.session_state.access_granted = False
    st.session_state.access_code = ""
    st.session_state.allowed_states = []

#🔐 Login Form
# if "access_granted" not in st.session_state:
#     st.session_state.access_granted = False

if not st.session_state.access_granted:
    
    ## ✅ Background Image applied app
    ## Optional: Check if dash_logo exists
    if "dash_logo" in globals():
        pass                        # or st.image(dash_logo)

    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        #st.markdown("### 🔐 Enter Access Code to Continue")
        st.write("")
        st.write("")
        st.markdown("""
            <div style='text-align: center; flex-grow: 1;'>
                <span style='font-size: 32px; color: steelblue; font-weight: bold'>
                    🔐 Enter Access Code
                </span>
            </div>
        """, unsafe_allow_html=True)


        with st.form("login_form", clear_on_submit=True):
            access_code_input = st.text_input(
                "Access Code",
                type="password",
                placeholder="Enter your access code",
                value="",
                key="access_input_box"
            )        
            login_clicked = st.form_submit_button("Login")

    # Login check logic
        if login_clicked:
            if access_code_input in access_map:
                if mode_map.get(access_code_input, "enable") == "disable":
                    st.error("🚫 Your access is currently disabled. Please contact admin.")
                    st.stop()
                st.session_state.access_granted = True
                st.session_state.access_code = access_code_input
                st.session_state.allowed_states = access_map[access_code_input]
                st.success("✅ Access granted! Dashboard unlocked.")
                st.rerun()
            else:
                st.warning("🚫 Invalid access code.")
        st.stop()


# ✅ After login: continuously check mode and auto-logout if disabled
# ---------------------------------------------------------------
# Re-load Google Sheet to get latest mode info
mode_map = {str(row["password"]).strip(): str(row["mode"]).strip().lower() for _, row in user_df.iterrows()}
# Check if user’s mode is now disabled
access_code = st.session_state.access_code
current_mode = mode_map.get(access_code, "enable")

if current_mode == "disable":
    st.error("🚫 Your access has been disabled by admin. Logging out...")
    st.session_state.access_granted = False
    st.session_state.access_code = ""
    st.session_state.allowed_states = []
    time.sleep(1)
    st.rerun()


### Access already granted — filter and show dashboard
access_code = st.session_state.access_code
allowed_states = st.session_state.allowed_states

if allowed_states != "ALL":
    if isinstance(allowed_states, str):
        allowed_states = [allowed_states]
    df = df[df["State"].isin(allowed_states)]
###### ----- Enter Acces Code for State Type  ------------- Communication Dashboard   ------------
###### ----- Enter Acces Code for State Type  ------------- Communication Dashboard   ------------
###### ----- Enter Acces Code for State Type  ------------- Communication Dashboard   ------------


required_columns = ["State", "Vendor", "Type of Communication", "Cohort","Election Type" ,"Total Phone Numbers", "Total Success"]
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    st.warning(f"⚠️ Some columns are missing in the sheet: {', '.join(missing_columns)}.")

with st.sidebar:
    comm_options = sorted(df["Type of Communication"].dropna().unique())
    comm_selected = st.pills("**Filter Communication Types**", comm_options, selection_mode="multi")

# Sidebar - Communication Filter
with st.sidebar:
    group_by = st.selectbox("📂 Analyze Data By", ["Vendor", "State", "Cohort","Election Type"])
    show_remarks = st.toggle("Show Vendor-wise Remarks", value=False)
    # st.warning("Please select **only one Communication Type (OBD or WhatsApp)** to view remarks.")

   # st.markdown("### 📨 Type of Communication")
   # comm_options = sorted(df["Type of Communication"].dropna().unique())
   # comm_selected = st.pills("**Filter Communication Types**", comm_options, selection_mode="multi")


####--- 1 --- Sidebar - filters options -----
for key in ["election_filter","state_filter", "vendor_filter", "cohort_filter"]:
    if key not in st.session_state:
        st.session_state[key] = []

with st.sidebar:
    if st.button("❌ Clear Filters"):
        st.session_state.election_filter = []
        st.session_state.state_filter = []
        st.session_state.vendor_filter = []
        st.session_state.cohort_filter = []

    filtered_for_options = df.copy()
    if comm_selected:
        filtered_for_options = filtered_for_options[filtered_for_options["Type of Communication"].isin(comm_selected)]
    ##-- Step 2: Further filter based on selected values (respect other filters)
    if st.session_state.state_filter:
        filtered_for_options = filtered_for_options[filtered_for_options["State"].isin(st.session_state.state_filter)]
    if st.session_state.vendor_filter:
        filtered_for_options = filtered_for_options[filtered_for_options["Vendor"].isin(st.session_state.vendor_filter)]
    if st.session_state.cohort_filter:
        filtered_for_options = filtered_for_options[filtered_for_options["Cohort"].isin(st.session_state.cohort_filter)]
    if st.session_state.election_filter:
        filtered_for_options = filtered_for_options[filtered_for_options["Election Type"].isin(st.session_state.election_filter)]

    ##-- Now get dynamic values for filter options
    election_options = sorted(filtered_for_options["Election Type"].dropna().unique())
    state_options = sorted(filtered_for_options["State"].dropna().unique())
    vendor_options = sorted(filtered_for_options["Vendor"].dropna().unique())
    cohort_options = sorted(filtered_for_options["Cohort"].dropna().unique())

if not any([election_options, state_options, vendor_options, cohort_options]):
    st.error("❌ No data found. Please clear some sidebar filters to continue.")
    st.stop()

##-- Multiselect
with st.sidebar:
    with st.expander("🎛 **Apply Filters**",expanded=True):
        selected_elections =st.multiselect("🗓️ Election Type", election_options, default=st.session_state.election_filter, key="election_filter")
        selected_states =st.multiselect("📍 State", state_options, default=st.session_state.state_filter, key="state_filter")
        selected_vendors =st.multiselect("🏷️ Vendor", vendor_options, default=st.session_state.vendor_filter, key="vendor_filter")
        selected_cohorts =st.multiselect("🎯 Cohort", cohort_options, default=st.session_state.cohort_filter, key="cohort_filter")#####--- 1 --- Sidebar - filters options -----



#########  sidebar Button  (Decimal Number Format ( e.g. 1.1 : K, L, Cr )---------
#########  sidebar Button  (Decimal Number Format ( e.g. 1.1 : K, L, Cr )---------
with st.sidebar:
### ---------- Decimal Number Format ( e.g. 1.1 : K, L, Cr )
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
if selected_elections:
    filtered_df = filtered_df[filtered_df["Election Type"].isin(selected_elections)]
if selected_states:
    filtered_df = filtered_df[filtered_df["State"].isin(selected_states)]
if selected_vendors:
    filtered_df = filtered_df[filtered_df["Vendor"].isin(selected_vendors)]
if selected_cohorts:
    filtered_df = filtered_df[filtered_df["Cohort"].isin(selected_cohorts)]
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
    summary = filtered_df.groupby(group_by)[["Total Phone Numbers", "Total Success"]].sum().reset_index()
    summary["Success %"] = summary.apply(lambda row: (row["Total Success"] / row["Total Phone Numbers"] * 100)
                                            if row["Total Phone Numbers"] > 0 else 0, axis=1).round(2)


    if isinstance(comm_selected, list) and len(comm_selected) == 1 and group_by == "Vendor":
        comm = comm_selected[0]
        summary[comment_cols] = summary.apply(
            lambda row: get_comment(row["Success %"], row["Vendor"], comm, remark_df),
            axis=1
        )

    if group_by == "Vendor" and (not comm_selected or len(comm_selected) > 1):
        # Get comma-separated communication types per vendor
        comm_type_map = (
            filtered_df.groupby("Vendor")["Type of Communication"]
            .apply(lambda x: ", ".join(sorted(set(x.dropna()))))
            .reset_index()
            .rename(columns={"Type of Communication": "Type of Communication(s)"})
        )
        
        # Merge with summary
        summary = pd.merge(summary, comm_type_map, on="Vendor", how="left")
        
        # Reorder columns: Vendor, Type of Communication(s), then rest
        cols = summary.columns.tolist()
        if "Type of Communication(s)" in cols:
            cols.insert(1, cols.pop(cols.index("Type of Communication(s)")))
            summary = summary[cols]

######---- Summary Table Add columns Success (%) and comment ------------------
######---- Summary Table Add columns Success (%) and comment ------------------



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
            f"{badge('Communication :', '#d9fafa', '#00c2b8')} "
            f"<span style='font-weight:450;'> &nbsp;&nbsp; {'&nbsp;,&nbsp;&nbsp;&nbsp;'.join(comm_selected)}</span>")
    if selected_elections:
        filtered_df.append(
            f"{badge('Election Type :', '#f2e5ff', '#7a24c9')} "
            f"<span style='font-weight:450;'> &nbsp;&nbsp; {'&nbsp;,&nbsp;&nbsp;&nbsp;'.join(selected_elections)}</span>")
    if selected_vendors:
        filtered_df.append(
            f"{badge('Vendors :', '#fff4e5', '#f39c12')} "
            f"<span style='font-weight:450;'> &nbsp;&nbsp; {'&nbsp;,&nbsp;&nbsp;&nbsp;'.join(selected_vendors)}</span>")
    if selected_cohorts:
        filtered_df.append(
            f"{badge('Cohorts :', '#ffe5ec', '#c20041')} "
            f"<span style='font-weight:450;'> &nbsp;&nbsp; {'&nbsp;,&nbsp;&nbsp;&nbsp;'.join(selected_cohorts)}</span>")
    if selected_states:
        filtered_df.append(
            f"{badge('State :', '#e5f0fb', '#2980b9')} "
            f"<span style='font-weight:450;'> &nbsp;&nbsp; {'&nbsp;,&nbsp;&nbsp;&nbsp;'.join(selected_states)}</span>")    
    if filtered_df:
        st.markdown("""
                    <div style="background-color:#f0f2f676; border-radius:200px; min-height: 100px, min-width: 100px;
                     display: flex; align-items: center; justify-content: center;">
                        <span style='color:Black; font-size:18px; font-weight:550;'>📑Filter Criteria</span>
                    </div>
                    """, unsafe_allow_html=True)
        for f in filtered_df:
            st.markdown(f"<div style='margin-bottom:2px;'>{f}</div>", unsafe_allow_html=True)
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

    custom_data_fields = ["Total Data (Compact)", "Total Success (Compact)"]
    if "Type of Communication(s)" in chart_data.columns:
        custom_data_fields.append("Type of Communication(s)")

#     st.markdown(f"""
# <div style="background-color:#f0f2f6; border-radius:19px;
#             padding: 6px 12px; margin-bottom: 10px;
#             display: flex; align-items: center; justify-content: center;">
#     <span style='font-size:19px; font-weight:650;'>
#         📊 <span style='color:#387fc1; font-weight:700;'>{group_by}</span>
#         <span style='font-weight:600; '>-wise Success % Chart</span>
#     </span>
# </div>
# """, unsafe_allow_html=True)

    fig = px.bar(
        chart_data,
        x=group_by,
        y="Success %",
        text="Success %",
        color=group_by,
        color_continuous_scale="Viridis",
        custom_data=custom_data_fields
    )
    fig.update_layout(title=None)
    fig.update_layout(
    title={
        "text": f"""<span style='color:#387fc1;'><b>{num_unique_group_by_items}-{group_by} </b></span><span style='font-weight:normal;'> -  wise Success % Chart</span>""",
        "y": 0.97,
        "x": 0.05,  # 👈 Align left
        "xanchor": "left",
        "yanchor": "top"
    },
    title_font=dict(size=24),
    )


    hovertemplate = ""
    # If communication type exists, show it first
    if "Type of Communication(s)" in custom_data_fields:
        hovertemplate += "Comm.Type: %{customdata[2]}<br>"

    hovertemplate += (
        "Total Data: %{customdata[0]}<br>"
        "Total Success: %{customdata[1]}<br>"
        "<extra></extra>"
    )
    hovertemplate += "<extra></extra>"

    fig.update_traces(
        texttemplate="<b>%{text}</b>",
        textposition="inside",
        insidetextanchor="end",
        hovertemplate=hovertemplate
    )

    fig.update_layout(
        yaxis_title="Success %",
        xaxis_title=group_by,
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        margin=dict(t=40, b=50),
        height=400,
        showlegend=False
    )

    
    st.plotly_chart(fig, use_container_width=True)
###------ Display Bar Chart Summary Table ----------------
###------ Display Bar Chart Summary Table ----------------


# Tabs: Conditionally show second tab
    if show_remarks:
        tab1, tab2 = st.tabs(["📊 Summary Table", "🗒️ Vendor-wise Remark Summary"])
    else:
        tab1, = st.tabs(["📊 Summary Table"])

    # ---------- TAB 1: Summary Table ----------
    with tab1:
        # st.markdown("##### 📋 Summary Table")
        
        if not summary.empty:
            summary["Total Phone Numbers"] = pd.to_numeric(summary["Total Phone Numbers"], errors='coerce')
            summary["Total Success"] = pd.to_numeric(summary["Total Success"], errors='coerce')
            summary["Success %"] = pd.to_numeric(summary["Success %"], errors='coerce')
            summary.index = range(1, len(summary) + 1)
            if compact_style == "compact":
                st.dataframe(
                    summary.style.format({
                        "Total Phone Numbers": lambda x: format_compact_decimal(int(x)),
                        "Total Success": lambda x: format_compact_decimal(int(x)),
                        "Success %": "{:.0f} %"}),use_container_width=False)
            else:
                st.dataframe(
                    summary.style.format({
                        "Total Phone Numbers": lambda x: format_indian_number(int(x)),
                        "Total Success": lambda x: format_indian_number(int(x)),
                        "Success %": "{:.0f} %"}),use_container_width=False)  
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

                # full_html = """
                # <style>
                # table.remark-table {
                #     border-collapse: collapse;
                #     width: 100%;
                #     margin-bottom: 30px;
                #     font-size: 12px;
                # }
                # table.remark-table th, table.remark-table td {
                #     border: 1px solid #ccc;
                #     padding: 4px;
                # }
                # table.remark-table th {
                #     background-color: #f0f0f0;
                #     text-align: center;
                # }
                # table.remark-table td.vendor-cell {
                #     text-align: center;
                #     vertical-align: middle;
                #     font-weight: 600;
                #     white-space: pre-wrap;
                #     background-color: #f9f9f9;
                # }
                # </style>
                # <table class="remark-table">
                # <thead>
                # <tr>
                #     <th>Vendor</th>
                #     <th>Percentage Range</th>
                #     <th>Comment Remark</th>
                # </tr>
                # </thead>
                # <tbody>
                # """

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
##$$$$$$$ -- perfect work--- Show Remarks Vendors only ---- sidebar vendors filter mode  ---



#########  sidebar Button  🔄 Click Refresh Dashboard Update & 🔴 Sign Out) ---------
#########  sidebar Button  🔄 Click Refresh Dashboard Update & 🔴 Sign Out) ---------

with st.sidebar:
### ---------- Dashboard Update 🔄 Click Refresh
    st.markdown("#### 📊 Dashboard Update")
    if st.button("🔄 Click Refresh"):
        st.cache_data.clear()
        st.rerun()

### ---------- 🔴 Sign Out
if st.session_state.access_granted:
    if st.sidebar.button("Logout"):
        st.session_state.access_granted = False
        st.session_state.access_code = ""
        st.session_state.allowed_states = []
        st.rerun()

#########  sidebar Button  🔄 Click Refresh Dashboard Update & 🔴 Sign Out) ---------
#########  sidebar Button  🔄 Click Refresh Dashboard Update & 🔴 Sign Out) ---------


########### --------- auto refresh timer -------------
########### --------- auto refresh timer -------------
########### --------- auto refresh timer -------------

###------⏱️ 1 hour = 3600000 milliseconds
st_autorefresh(interval=3600000, key="auto_logout_refresh")

########### --------- auto refresh timer -------------
########### --------- auto refresh timer -------------
########### --------- auto refresh timer -------------

######------- chose colour for desing-----------
try:st.markdown(f"""<div style="{format(bg1='#e6ffea', bg2="#3697b2", border="#80C99F")}">  </div> """, unsafe_allow_html=True)
except:pass
######------- chose colour for desing-----------






