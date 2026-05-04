import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import os

#-------------------------------------------------
# PASSWORD
#------------------------------------------------
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated=False

    if not st.session_state.authenticated:
        password = st.text_input(
            "Enter Password",
            type="password"
        )

        if st.button("Login"):
            if password == st.secrets["APP_PASSWORD"]:
                st.session_state.authenticated=True
                st.rerun()
            else:
                st.error("Incorrect password")

        st.stop()

check_password()


# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="IT Service Desk Dashboard",
    layout="wide",
    page_icon="📊"
)

# -------------------------------------------------
# GLOBAL THEME / COLORS
# -------------------------------------------------
custom_colors=[
"#38bdf8",
"#6366f1",
"#8b5cf6",
"#ec4899",
"#14b8a6",
"#f59e0b"
]

multi_colors=[
"#38bdf8",
"#60a5fa",
"#818cf8",
"#c084fc",
"#f472b6",
"#2dd4bf",
"#fbbf24",
"#fb7185",
"#22c55e",
"#e879f9",
"#06b6d4",
"#f97316",
"#14b8a6",
"#a78bfa",
"#3b82f6"
]

px.defaults.template="plotly_dark"
px.defaults.color_discrete_sequence=custom_colors


# -------------------------------------------------
# CHART STYLING FUNCTION (FIXED)
# -------------------------------------------------
def style_chart(fig):

    fig.update_layout(
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title_font=dict(size=22),
        font=dict(size=13),

        xaxis=dict(
            showgrid=False,
            zeroline=False
        ),

        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,.08)",
            zeroline=False
        ),

        bargap=.25,

        legend=dict(
            orientation="h",
            y=1.1
        ),
        showlegend=False,
    )

    return fig


# -------------------------------------------------
# CUSTOM CSS
# -------------------------------------------------
st.markdown("""
<style>
.main{
background:linear-gradient(135deg,#0f172a,#111827);
}

h1{
font-size:44px !important;
font-weight:800 !important;
background:linear-gradient(90deg,#38bdf8,#818cf8,#ec4899);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
text-shadow:0 0 25px rgba(59,130,246,.4);
}

div[data-testid="stMetric"]{
background:linear-gradient(
145deg,
rgba(30,41,59,.95),
rgba(15,23,42,.95)
);
padding:22px;
border-radius:22px;
border:1px solid rgba(96,165,250,.25);
box-shadow:
0 8px 30px rgba(0,0,0,.35),
0 0 12px rgba(59,130,246,.15);
transition:.4s;
cursor:pointer;
}

div[data-testid="stMetric"]:hover{
transform:translateY(-8px) scale(1.03);
box-shadow:
0 10px 35px rgba(0,0,0,.45),
0 0 22px rgba(56,189,248,.55),
0 0 40px rgba(99,102,241,.35);
}

div[data-testid="stMetricValue"]{
color:#38bdf8;
font-size:34px;
font-weight:800;
}

div[data-testid="stMetricLabel"]{
color:white;
font-weight:600;
}

[data-testid="stPlotlyChart"]{
background:rgba(255,255,255,.03);
padding:15px;
border-radius:20px;
box-shadow:0 0 18px rgba(59,130,246,.1);
}

section[data-testid="stSidebar"]{
background:linear-gradient(180deg,#111827,#0f172a);
}

.stDownloadButton button{
background:linear-gradient(90deg,#3b82f6,#8b5cf6);
color:white;
border:none;
border-radius:14px;
padding:12px 22px;
font-weight:700;
}
.tooltip {
    position: relative;
}

.tooltip .tooltiptext {
    visibility: hidden;
    background-color: #111827;
    color: #fff;
    border-radius: 6px;
    padding: 6px 10px;
    position: absolute;
    bottom: 120%;
    left: 50%;
    transform: translateX(-50%);
    opacity: 0;
    transition: opacity 0.3s;
    font-size: 13px;
    white-space: nowrap;
}

.tooltip:hover .tooltiptext {
    visibility: visible;
    opacity: 1;
}
</style>
""",unsafe_allow_html=True)

#---------------------------
# hover of kpi card
#--------------------------
def kpi_card(title, value):

    full_value = f"{value:,}"

    short_value = str(value)
    if len(short_value) > 4:
        short_value = short_value[:3] + "..."

    st.markdown(f"**{title}**")
    st.metric(
        label="",
        value=short_value,
        help=f"Full Value: {full_value}"
    )

    

# -------------------------------------------------
# TITLE
# -------------------------------------------------
st.title("📊 IT Service Desk Dashboard")

st.markdown('''
<h4 style="color:#94a3b8">
🚀 Real-Time Interactive Service Desk Analytics
</h4>
''',unsafe_allow_html=True)


# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
uploaded_file=st.sidebar.file_uploader(
"Upload CSV",
type=["csv"]
)

if uploaded_file is None:
    st.stop()

df=pd.read_csv(uploaded_file)

st.sidebar.success(
f"Loaded Records: {len(df)}"
)


# -------------------------------------------------
# COLUMN MAPPING
# -------------------------------------------------
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(r'[^a-z0-9]', '', regex=True)
)

# Rename  columns
mapping = {
    'requestid': 'ticket_id',
    'createdtime': 'created_date',
    'completedtime': 'closed_date',
    'site': 'location',
    'technician': 'technician',
    'prioritytype': 'priority',
    'category': 'issue_type',
    'resolution': 'resolution',
    'department': 'department'
}

df.rename(columns=mapping, inplace=True)

status_col = None

for col in df.columns:
    if 'status' in col:
        status_col = col
        break

if status_col:
    df.rename(columns={status_col: 'status'}, inplace=True)
else:
    st.error("❌ No STATUS column found in dataset")
    st.write("Columns found:", df.columns.tolist())
    st.stop()

df['status'] = (
    df['status']
    .astype(str)
    .str.strip()
    .str.lower()
)

df['status'] = df['status'].replace(['nan', 'none'], '')

# -------------------------------------------------
# DATES
# -------------------------------------------------
df["created_date"]=pd.to_datetime(
df["created_date"],
format="mixed",
dayfirst=True,
errors="coerce"
)

df["closed_date"]=pd.to_datetime(
df["closed_date"],
format="mixed",
dayfirst=True,
errors="coerce"
)

df["created_date"]=df["created_date"].fillna(pd.Timestamp.today())
df["closed_date"]=df["closed_date"].fillna(df["created_date"])

df["closure_days"]=(
df["closed_date"]-
df["created_date"]
).dt.total_seconds()/86400

df["closure_days"]=(
df["closure_days"]
.clip(lower=0)
.fillna(0)
)

#--------------------------------------------------
# CALENDER
#--------------------------------------------------
#--------------------------------------------------
# CALENDER (MONTH RANGE SELECTOR)
#--------------------------------------------------
st.sidebar.header("📅 Select Date ")

# Create Year and Month columns
df["year"] = df["created_date"].dt.year
df["month"] = df["created_date"].dt.month
df["month_name"] = df["created_date"].dt.strftime("%B")

# Unique values
years = sorted(df["year"].dropna().unique())
months = list(range(1, 13))

# Sidebar selectors
selected_year = st.sidebar.selectbox("Select Year", years)

col1, col2 = st.sidebar.columns(2)

start_month = col1.selectbox(
    "Start Month",
    months,
    format_func=lambda x: pd.to_datetime(str(x), format="%m").strftime("%B"),
    index=0
)

end_month = col2.selectbox(
    "End Month",
    months,
    format_func=lambda x: pd.to_datetime(str(x), format="%m").strftime("%B"),
    index=11
)

# Validation (important)
if start_month > end_month:
    st.sidebar.error("Start month should be before or equal to End month")

# Apply filter
df = df[
    (df["year"] == selected_year) &
    (df["month"] >= start_month) &
    (df["month"] <= end_month)
]
# -------------------------------------------------
# FILTERS
# -------------------------------------------------
st.sidebar.header("Filters")

# ----------------------------
# STATUS FILTER 
# ----------------------------

df['status'] = df['status'].fillna('').astype(str).str.strip().str.lower()
df['status'] = df['status'].replace(['nan', 'none'], '')


df['status_display'] = df['status'].apply(
    lambda x: 'Blank' if x == '' else x
)

status_vals = sorted(df['status_display'].astype(str).unique().tolist())

status_filter = st.sidebar.multiselect(
    "Status",
    status_vals,
    default=status_vals
)

selected_status = [
    '' if s == 'Blank' else s
    for s in status_filter
]

df_temp = df[df['status'].isin(selected_status)]

# ----------------------------
# DEPARTMENT FILTER 
# ----------------------------
all_depts = sorted(df_temp.department.dropna().unique())

dept = st.sidebar.multiselect(
    "Department",
    all_depts,
    default=all_depts
)

# ----------------------------
# APPLY FINAL FILTERS
# ----------------------------
df = df[
    (df.status.isin(selected_status)) &
    (df.department.isin(dept))
]


page=st.sidebar.radio(
"Navigate",
[
"Overview",
"Operational KPI",
"Trend Analysis",
"Problem Analysis",
"Productivity",
"Root Cause"
]
)


# -------------------------------------------------
# KPI CALCULATIONS
# -------------------------------------------------
total=len(df)
closed=(
df.status.astype(str)
.str.lower()
.eq("closed")
.sum()
)

pending=total-closed
avg_close=round(df.closure_days.mean(),2)
sla=round((df.closure_days<=2).mean()*100,2)

critical=len(
df[
df.priority.astype(str)
.str.lower()
.isin(["high","critical"])
]
)


# -------------------------------------------------
# PDF
# -------------------------------------------------
def generate_pdf():

    pdf=FPDF()
    pdf.add_page()
    pdf.set_font("Arial","B",18)

    pdf.cell(
    200,10,
    "IT Service Desk KPI Report",
    ln=True
    )

    pdf.ln(10)
    pdf.set_font("Arial","",14)

    metrics=[
    f"Total Tickets: {total}",
    f"Closed Tickets: {closed}",
    f"Pending Tickets: {pending}",
    f"Avg Closure Days: {avg_close}",
    f"SLA Compliance: {sla}%",
    f"Critical Tickets: {critical}"
    ]

    for item in metrics:
        pdf.cell(200,12,item,ln=True)

    filename="dashboard_report.pdf"
    pdf.output(filename)

    with open(filename,"rb") as f:
        return f.read()


csv=df.to_csv(index=False)
st.sidebar.download_button("Download CSV",csv,"filtered.csv")

pdf_bytes=generate_pdf()

st.sidebar.download_button(
"📄 Download PDF Report",
pdf_bytes,
file_name="dashboard_report.pdf",
mime="application/pdf"
)


# -------------------------------------------------
# OVERVIEW
# -------------------------------------------------
if page=="Overview":

    a,b,c,d,e,f=st.columns(6)
    with a:
        kpi_card("Total", total)
    with b:
        kpi_card("Closed", closed)
    with c:
        kpi_card("Pending", pending)
    with d:
        kpi_card("Avg Closure", avg_close)
    with e:
        kpi_card("SLA %", sla)
    with f:
        kpi_card("Critical", critical)

    st.markdown("---")

    col1,col2=st.columns(2)

    with col1:

        status_mix=df.status.value_counts()

        fig1=px.pie(
        values=status_mix.values,
        names=status_mix.index,
        hole=.62,
        title="Ticket Status Distribution",
        color_discrete_sequence=px.colors.qualitative.Bold
        )

        fig1.update_traces(
        textposition="inside",
        textinfo="percent",
        pull=[0.02]*len(status_mix)
        )

        st.plotly_chart(
        style_chart(fig1),
        use_container_width=True
        )

    with col2:

        priority_mix=df.priority.value_counts()

        fig2=px.bar(
        x=priority_mix.index,
        y=priority_mix.values,
        title="Priority Distribution"
        )

        fig2.update_traces(
        marker=dict(color=custom_colors)
        )

        st.plotly_chart(
        style_chart(fig2),
        use_container_width=True
        )


# -------------------------------------------------
# OPERATIONAL KPI
# -------------------------------------------------
elif page=="Operational KPI":

    r1,r2,r3=st.columns(3)
    r1.metric("Total Tickets",total)
    r2.metric("Closed Tickets",closed)
    r3.metric("Pending",pending)

    r4,r5,r6=st.columns(3)
    r4.metric("Avg Resolution",avg_close)
    r5.metric("SLA %",sla)
    r6.metric("Critical Tickets",critical)


# -------------------------------------------------
# TREND ANALYSIS
# -------------------------------------------------
elif page=="Trend Analysis":

    st.subheader("Daily Ticket Trend")

    daily=(
    df.groupby(
    df.created_date.dt.date
    ).size()
    .reset_index(name="Tickets")
    )

    fig=px.line(
    daily,
    x="created_date",
    y="Tickets",
    markers=True,
    title="Daily Ticket Trend"    
    )
    fig.update_traces(
        name="Tickets",
        showlegend=False
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Tickets"
    )    
    st.plotly_chart(
    style_chart(fig),
    use_container_width=True
    )


    st.subheader("Monthly Ticket Trend")

    monthly=(
    df.groupby(df["created_date"].dt.strftime("%Y-%m")
              )
    .size()
    .reset_index(name="Tickets")
    )
    monthly.columns=["Month","Tickets"]
    fig2=px.bar(
    monthly,
    x="Month",
    y="Tickets",
    title="Monthly Ticket Trend"
    )
    
    fig2.update_xaxes(title="Month")
    fig2.update_yaxes(title="Tickets")
    
    st.plotly_chart(
    style_chart(fig2),
    use_container_width=True
    )


    byhour=(
    df.groupby(df.created_date.dt.hour)
    .size()
    .reset_index(name="Count")
    .rename(columns={"created_date":"Hour"})
    )

    fig3=px.area(
    byhour,
    x="Hour",
    y="Count",
    title="Peak Hours"
    )

    st.plotly_chart(
    style_chart(fig3),
    use_container_width=True
    )


# -------------------------------------------------
# PROBLEM ANALYSIS
# -------------------------------------------------
elif page=="Problem Analysis":

    issues=df.issue_type.value_counts().head(15)

    fig=px.bar(
    x=issues.index,
    y=issues.values,
    title="Top Issues"
    )

    fig.update_traces(
    marker=dict(
    color=multi_colors,
    line=dict(color="rgba(255,255,255,0)",width=0)
    ))

    st.plotly_chart(style_chart(fig),use_container_width=True)


    dep=df.department.value_counts().head(10)

    fig2=px.bar(
    x=dep.index,
    y=dep.values,
    title="Department Volume"
    )

    fig2.update_traces(
    marker=dict(
    color=multi_colors,
    line=dict(color="rgba(255,255,255,0)",width=0)
    ))

    st.plotly_chart(style_chart(fig2),use_container_width=True)


    site=df.location.value_counts().head(10)

    fig3=px.bar(
    x=site.index,
    y=site.values,
    title="Site Issues"
    )

    fig3.update_traces(
    marker=dict(color=custom_colors)
    )

    st.plotly_chart(style_chart(fig3),use_container_width=True)


# -------------------------------------------------
# PRODUCTIVITY
# -------------------------------------------------
elif page=="Productivity":

    tech=(
    df.groupby("technician")
    .size()
    .reset_index(name="Tickets")
    .sort_values("Tickets",ascending=False)
    .head(15)
    )

    fig=px.bar(
    tech,
    x="technician",
    y="Tickets",
    title="Technician Productivity"
    )

    fig.update_traces(
    marker=dict(
    color=multi_colors,
    line=dict(color="rgba(255,255,255,0)",width=0)
    ))

    st.plotly_chart(style_chart(fig),use_container_width=True)


    res=(
    df.groupby("technician")["closure_days"]
    .mean()
    .reset_index()
    .sort_values("closure_days")
    .head(15)
    )

    fig2=px.bar(
    res,
    x="technician",
    y="closure_days",
    title="Average Resolution Time by Technician"
    )

    fig2.update_traces(
    marker=dict(
    color=multi_colors,
    line=dict(color="rgba(255,255,255,0)",width=0)
    ))

    st.plotly_chart(style_chart(fig2),use_container_width=True)


# -------------------------------------------------
# ROOT CAUSE
# -------------------------------------------------
elif page=="Root Cause":

    # ----------------------------
    # Root Cause from Resolution
    # ----------------------------

    printer_df=df[
        df["resolution"].astype(str)
        .str.contains("printer",case=False,na=False)
    ]

    login_df=df[
        df["resolution"].astype(str)
        .str.contains("login|password",case=False,na=False)
    ]

    network_df=df[
        df["resolution"].astype(str)
        .str.contains("network|internet|connectivity",case=False,na=False)
    ]


    printer=len(printer_df)
    login=len(login_df)
    network=len(network_df)


    a,b,c=st.columns(3)

    a.metric("Repeat Printer Failures",printer)
    b.metric("Frequent Login Issues",login)
    c.metric("Network Downtime",network)


    # Root Cause Frequency Chart
    root=pd.DataFrame({
    "Issue":[
        "Printer Failures",
        "Login Issues",
        "Network Downtime"
    ],
    "Count":[
        printer,
        login,
        network
    ]
    })

    fig=px.bar(
        root,
        x="Issue",
        y="Count",
        title="Root Cause Frequency"
    )

    st.plotly_chart(
        style_chart(fig),
        use_container_width=True
    )


    # ----------------------------
    # Repeat Printer Failures Trend
    # ----------------------------

    printer_trend=(
      printer_df.groupby(
      printer_df.created_date.dt.to_period("M")
      ).size()
      .reset_index(name="Count")
    )

    printer_trend["created_date"]=printer_trend["created_date"].astype(str)

    fig2=px.line(
        printer_trend,
        x="created_date",
        y="Count",
        markers=True,
        title="Repeat Printer Failures Trend"
    )

    st.plotly_chart(style_chart(fig2),use_container_width=True)



    # ----------------------------
    # Frequent Login Issues Trend
    # ----------------------------

    login_trend=(
      login_df.groupby(
      login_df.created_date.dt.to_period("M")
      ).size()
      .reset_index(name="Count")
    )

    login_trend["created_date"]=login_trend["created_date"].astype(str)

    fig3=px.line(
        login_trend,
        x="created_date",
        y="Count",
        markers=True,
        title="Frequent Login Issues Trend"
    )

    st.plotly_chart(style_chart(fig3),use_container_width=True)



    # ----------------------------
    # Network Downtime Trend
    # ----------------------------

    network_trend=(
      network_df.groupby(
      network_df.created_date.dt.to_period("M")
      ).size()
      .reset_index(name="Count")
    )

    network_trend["created_date"]=network_trend["created_date"].astype(str)

    fig4=px.line(
        network_trend,
        x="created_date",
        y="Count",
        markers=True,
        title="Network Downtime Trend"
    )

    st.plotly_chart(
      style_chart(fig4),
      use_container_width=True
    )
    

