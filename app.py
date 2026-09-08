import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import networkx as nx
from textwrap import dedent

try:
    from entity_extractor import extract_entities
except ImportError:
    def extract_entities(text):
        return {
            "PHONE": [],
            "EMAIL": [],
            "VEHICLE": []
        }


# =========================================================
# PAGE CONFIGURATION
# ---------------------------------------------------------
# Must be the first Streamlit command in the script.
# =========================================================

st.set_page_config(
    page_title="Criminal Network Analysis System",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# HTML HELPER
# ---------------------------------------------------------
# Every multi-line HTML string passed to st.markdown MUST
# go through this. dedent() strips the common leading
# whitespace, so it renders correctly no matter how deeply
# nested the surrounding Python block is. This is the fix
# for the "raw HTML printed as text" bug.
# =========================================================

def html(raw: str) -> str:
    return dedent(raw).strip()


def render(raw: str):
    st.markdown(html(raw), unsafe_allow_html=True)


# =========================================================
# GLOBAL STYLE — DOSSIER / CASE-FILE TERMINAL
# =========================================================

render("""
<style>

@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    --void:      #07080B;
    --panel:     #0E1116;
    --elevated:  #151A21;
    --hairline:  rgba(140, 160, 175, 0.14);
    --hairline-strong: rgba(140, 160, 175, 0.28);
    --text:      #C9D3DA;
    --muted:     #5B6570;
    --signal:    #4FA6AD;
    --priority:  #C6903F;
    --critical:  #A3453D;
}

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

.stApp {
    background: var(--void);
    color: var(--text);
    background-image:
        radial-gradient(circle at 12% 8%, rgba(79,166,173,0.05), transparent 32%),
        radial-gradient(circle at 90% 85%, rgba(198,144,63,0.035), transparent 35%);
}

/* faint grain instead of a HUD scanline sweep */
.stApp::after {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    opacity: 0.5;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='90' height='90'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.025'/%3E%3C/svg%3E");
    z-index: 999;
}

.block-container {
    padding-top: 1.8rem;
    padding-bottom: 3rem;
}

code, .mono {
    font-family: 'JetBrains Mono', monospace;
}

/* =========================================================
   SIDEBAR — CASE INDEX
   ========================================================= */

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #07080B 0%, #0A0D12 100%);
    border-right: 1px solid var(--hairline);
}

.rail-mark {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 2px;
    color: var(--signal);
    border: 1px solid var(--hairline-strong);
    display: inline-block;
    padding: 2px 7px;
    border-radius: 2px;
    margin-bottom: 10px;
}

.rail-title {
    font-size: 17px;
    font-weight: 600;
    color: #E4EAEE;
    letter-spacing: 0.3px;
    line-height: 1.3;
}

.rail-subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 1px;
    color: var(--muted);
    margin-top: 6px;
}

/* radio nav rows */
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12.5px;
    letter-spacing: 0.4px;
    color: var(--muted);
    padding: 3px 0;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    color: var(--text);
}

/* =========================================================
   HEADER
   ========================================================= */

.page-kicker {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 2px;
    color: var(--muted);
    margin-bottom: 4px;
}

.page-title {
    font-size: 27px;
    font-weight: 600;
    color: #EAF0F4;
    letter-spacing: 0.2px;
}

.page-subtitle {
    color: var(--muted);
    font-size: 13px;
    margin-top: 4px;
}

.hr-hair {
    border: none;
    border-top: 1px solid var(--hairline);
    margin: 18px 0 22px 0;
}

/* =========================================================
   METRIC CARDS
   ========================================================= */

div[data-testid="metric-container"] {
    background: var(--panel);
    border: 1px solid var(--hairline);
    border-left: 2px solid var(--signal);
    border-radius: 3px;
    padding: 16px 18px;
}

div[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-size: 10.5px !important;
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: 1px !important;
}

div[data-testid="stMetricValue"] {
    color: #E9EEF1 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* =========================================================
   DOSSIER PANEL
   ========================================================= */

.dossier {
    position: relative;
    background: var(--panel);
    border: 1px solid var(--hairline);
    border-radius: 3px;
    padding: 22px 22px 18px 22px;
    margin-bottom: 4px;
}

.dossier-tag {
    position: absolute;
    top: -10px;
    left: 16px;
    background: var(--void);
    padding: 0 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 1.5px;
    color: var(--signal);
}

.field-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 1px;
    color: var(--muted);
    margin-top: 12px;
}

.field-value {
    font-size: 14.5px;
    color: var(--text);
    margin-top: 2px;
}

/* priority chips */
.chip {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 1px;
    padding: 2px 8px;
    border-radius: 2px;
    border: 1px solid var(--hairline-strong);
}

.chip-high    { color: var(--critical); border-color: rgba(163,69,61,0.45); }
.chip-medium  { color: var(--priority); border-color: rgba(198,144,63,0.45); }
.chip-low     { color: var(--signal);   border-color: rgba(79,166,173,0.4); }

/* =========================================================
   SECTION LABEL (small, not shouty — used sparingly)
   ========================================================= */

.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 1.5px;
    color: #8CA0AB;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--hairline);
}

/* =========================================================
   STATUS LINE
   ========================================================= */

.status-row {
    display: flex;
    align-items: center;
    gap: 9px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #8CA0AB;
    margin: 7px 0;
}

.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--signal);
    box-shadow: 0 0 6px rgba(79,166,173,0.7);
}

/* =========================================================
   BUTTONS
   ========================================================= */

.stButton > button {
    width: 100%;
    background: var(--panel);
    color: #AEC4CB;
    border: 1px solid var(--hairline-strong);
    border-radius: 2px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    letter-spacing: 0.5px;
    transition: 0.18s;
}

.stButton > button:hover {
    border-color: var(--signal);
    color: #E8F2F3;
}

/* =========================================================
   INPUTS
   ========================================================= */

div[data-baseweb="select"] > div, .stTextInput input {
    background: var(--panel) !important;
    border-color: var(--hairline-strong) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
}

/* =========================================================
   DATAFRAME
   ========================================================= */

div[data-testid="stDataFrame"] {
    border: 1px solid var(--hairline);
    border-radius: 3px;
}

/* =========================================================
   ALERTS
   ========================================================= */

div[data-testid="stAlert"] {
    background: var(--panel);
    border: 1px solid var(--hairline);
    border-left: 2px solid var(--signal);
    border-radius: 2px;
    font-size: 13px;
    color: var(--text);
}

/* =========================================================
   CLEANUP
   ========================================================= */

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { background: transparent !important; }

</style>
""")


# =========================================================
# SIDEBAR
# =========================================================

render("""
<div class="rail-mark">◆ SIH26189</div>
<div class="rail-title">Criminal Network<br>Analysis</div>
<div class="rail-subtitle">CASE INDEX — MODULE SELECT</div>
""")

st.sidebar.markdown("<hr class='hr-hair'>", unsafe_allow_html=True)

page = st.sidebar.radio(
    "MODULES",
    [
        "Dashboard",
        "Investigations",
        "Entity Intelligence",
        "Network Analysis",
        "Phone Intelligence",
        "Reports",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown("<hr class='hr-hair'>", unsafe_allow_html=True)

render("""
<div class="status-row"><div class="status-dot"></div> system online</div>
<div class="field-label" style="margin-top:14px;">ENVIRONMENT</div>
<div class="field-value" style="font-family:'JetBrains Mono',monospace; font-size:11.5px; color:var(--muted);">
    secure sandbox<br>
    synthetic data mode<br>
    human review required
</div>
""")


# =========================================================
# SHARED DATA
# =========================================================

investigations = pd.DataFrame({
    "CASE ID": ["CASE-001", "CASE-002", "CASE-003", "CASE-004"],
    "INVESTIGATION": ["Organized Network", "Financial Activity", "Vehicle Network", "Phone Intelligence"],
    "ENTITIES": [34, 21, 18, 27],
    "PRIORITY": ["HIGH", "MEDIUM", "HIGH", "MEDIUM"],
    "STATUS": ["ACTIVE", "ACTIVE", "REVIEW", "ACTIVE"],
})

entities = pd.DataFrame({
    "ENTITY ID": ["P-001", "P-002", "P-003", "PH-001", "PH-002", "V-001", "L-001", "O-001", "E-001"],
    "ENTITY": [
        "Arjun Mehta", "Rohan Shah", "Vikram Rao",
        "+91-98XXXXXX21", "+91-97XXXXXX44", "MH-12-AB-4582",
        "Pune", "Alpha Logistics", "demo.contact@email.com",
    ],
    "TYPE": ["PERSON", "PERSON", "PERSON", "PHONE", "PHONE", "VEHICLE", "LOCATION", "ORGANIZATION", "EMAIL"],
    "CONNECTIONS": [8, 6, 5, 4, 3, 3, 7, 4, 2],
    "PRIORITY": ["HIGH", "HIGH", "MEDIUM", "HIGH", "MEDIUM", "MEDIUM", "LOW", "MEDIUM", "LOW"],
})

network_nodes = {
    "P-001": {"name": "Arjun Mehta", "type": "PERSON"},
    "P-002": {"name": "Rohan Shah", "type": "PERSON"},
    "P-003": {"name": "Vikram Rao", "type": "PERSON"},
    "PH-001": {"name": "+91-98XXXXXX21", "type": "PHONE"},
    "PH-002": {"name": "+91-97XXXXXX44", "type": "PHONE"},
    "V-001": {"name": "MH-12-AB-4582", "type": "VEHICLE"},
    "L-001": {"name": "Pune", "type": "LOCATION"},
    "O-001": {"name": "Alpha Logistics", "type": "ORGANIZATION"},
    "E-001": {"name": "demo.contact@email.com", "type": "EMAIL"},
}


network_edges = [
    {
        "source": "P-001",
        "target": "PH-001",
        "relationship": "USES PHONE",
        "evidence": "CDR record #CDR-1042",
        "source_type": "Call Detail Record",
        "date": "2026-08-14",
        "case_id": "CASE-001",
    },
    {
        "source": "P-001",
        "target": "V-001",
        "relationship": "USES VEHICLE",
        "evidence": "Surveillance report #SR-018",
        "source_type": "Surveillance Report",
        "date": "2026-08-15",
        "case_id": "CASE-001",
    },
    {
        "source": "P-001",
        "target": "L-001",
        "relationship": "LOCATED AT",
        "evidence": "Location record #LOC-031",
        "source_type": "Location Record",
        "date": "2026-08-16",
        "case_id": "CASE-001",
    },
    {
        "source": "P-001",
        "target": "O-001",
        "relationship": "ASSOCIATED WITH",
        "evidence": "Investigation report #IR-007",
        "source_type": "Investigation Report",
        "date": "2026-08-17",
        "case_id": "CASE-001",
    },
    {
        "source": "P-001",
        "target": "P-002",
        "relationship": "CONNECTED TO",
        "evidence": "CDR record #CDR-1098",
        "source_type": "Call Detail Record",
        "date": "2026-08-18",
        "case_id": "CASE-001",
    },
    {
        "source": "P-002",
        "target": "PH-002",
        "relationship": "USES PHONE",
        "evidence": "CDR record #CDR-1112",
        "source_type": "Call Detail Record",
        "date": "2026-08-18",
        "case_id": "CASE-001",
    },
    {
        "source": "P-002",
        "target": "L-001",
        "relationship": "LOCATED AT",
        "evidence": "Location record #LOC-044",
        "source_type": "Location Record",
        "date": "2026-08-19",
        "case_id": "CASE-002",
    },
    {
        "source": "P-002",
        "target": "P-003",
        "relationship": "CONNECTED TO",
        "evidence": "Interview report #INT-012",
        "source_type": "Interview Report",
        "date": "2026-08-20",
        "case_id": "CASE-002",
    },
    {
        "source": "P-003",
        "target": "V-001",
        "relationship": "USES VEHICLE",
        "evidence": "Surveillance report #SR-024",
        "source_type": "Surveillance Report",
        "date": "2026-08-20",
        "case_id": "CASE-002",
    },
    {
        "source": "P-003",
        "target": "E-001",
        "relationship": "LINKED EMAIL",
        "evidence": "Email record #EM-022",
        "source_type": "Email Record",
        "date": "2026-08-21",
        "case_id": "CASE-002",
    },
    {
        "source": "P-003",
        "target": "O-001",
        "relationship": "ASSOCIATED WITH",
        "evidence": "Investigation report #IR-011",
        "source_type": "Investigation Report",
        "date": "2026-08-21",
        "case_id": "CASE-002",
    },
]


entity_icons = {
    "PERSON": "◐", "PHONE": "◍", "LOCATION": "◈",
    "VEHICLE": "▦", "ORGANIZATION": "▣", "EMAIL": "◉",
}

relationship_map = {
    ("P-001", "PH-001"): "USES PHONE", ("P-001", "V-001"): "USES VEHICLE",
    ("P-001", "L-001"): "LOCATED AT", ("P-001", "O-001"): "ASSOCIATED WITH",
    ("P-001", "P-002"): "CONNECTED TO", ("P-002", "PH-002"): "USES PHONE",
    ("P-002", "L-001"): "LOCATED AT", ("P-002", "P-003"): "CONNECTED TO",
    ("P-003", "V-001"): "USES VEHICLE", ("P-003", "E-001"): "LINKED EMAIL",
    ("P-003", "O-001"): "ASSOCIATED WITH",
}


def chip(priority: str) -> str:
    cls = {"HIGH": "chip-high", "MEDIUM": "chip-medium", "LOW": "chip-low"}.get(priority, "chip-low")
    return f'<span class="chip {cls}">{priority}</span>'


def page_header(kicker: str, title: str, subtitle: str):
    render(f"""
    <div class="page-kicker">{kicker}</div>
    <div class="page-title">{title}</div>
    <div class="page-subtitle">{subtitle}</div>
    <hr class="hr-hair">
    """)


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    page_header(
        "OVERVIEW",
        "Criminal Network Analysis System",
        "Investigator decision-support · entity linking · network intelligence"
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("ACTIVE CASES", "12", "+2")
    with c2: st.metric("ENTITIES IDENTIFIED", "148", "+18")
    with c3: st.metric("NETWORK CONNECTIONS", "326", "+41")
    with c4: st.metric("HIGH-PRIORITY FLAGS", "17", "+3")

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([2, 1])

    with left:
        render('<div class="section-label">investigation activity — last 7 days</div>')

        days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        activity = [24, 37, 31, 52, 68, 61, 84]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=days, y=activity, mode="lines+markers",
            line=dict(width=2, color="#4FA6AD"),
            marker=dict(size=6, color="#4FA6AD"),
            fill="tozeroy", fillcolor="rgba(79,166,173,0.08)",
        ))
        fig.update_layout(
            height=280,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#5B6570", family="JetBrains Mono"),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(140,160,175,0.08)"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        render('<div class="section-label">pipeline status</div>')
        modules = [
            "Entity Extraction", "Relationship Discovery", "Network Analysis",
            "Phone Intelligence", "Pattern Detection", "Investigation Insights",
        ]
        rows = "".join(f'<div class="status-row"><div class="status-dot"></div>{m}</div>' for m in modules)
        render(f'<div class="dossier">{rows}</div>')

    st.markdown("<br>", unsafe_allow_html=True)
    render('<div class="section-label">active investigation feed</div>')
    st.dataframe(investigations, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    render('<div class="section-label">quick actions</div>')
    a, b, c, d = st.columns(4)
    with a: st.button("+ New investigation")
    with b: st.button("↑ Upload intelligence")
    with c: st.button("◈ Explore network")
    with d: st.button("▣ Generate report")

    render("""
    <div style="text-align:center; margin-top:40px; color:#3E4750; font-size:10px;
                font-family:'JetBrains Mono',monospace; letter-spacing:1.5px;">
        SIH26189 — PROTOTYPE BUILD — SYNTHETIC DATA — HUMAN REVIEW REQUIRED
    </div>
    """)

    st.stop()


# =========================================================
# INVESTIGATIONS
# =========================================================

if page == "Investigations":

    page_header("CASE MANAGEMENT", "Investigations", "Case selection · intelligence summary · actions")

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("TOTAL CASES", "12")
    with c2: st.metric("ACTIVE", "8")
    with c3: st.metric("UNDER REVIEW", "3")
    with c4: st.metric("HIGH PRIORITY", "4")

    st.markdown("<br>", unsafe_allow_html=True)
    render('<div class="section-label">select investigation</div>')

    selected_case = st.selectbox("Investigation", investigations["CASE ID"], label_visibility="collapsed")
    case = investigations[investigations["CASE ID"] == selected_case].iloc[0]

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([2, 1])

    with left:
        render(f"""
        <div class="dossier">
            <div class="dossier-tag">CASE FILE</div>
            <div class="field-value" style="font-family:'JetBrains Mono',monospace; font-size:18px; color:#E9EEF1;">
                {case["CASE ID"]}
            </div>
            <div class="field-label">INVESTIGATION TYPE</div>
            <div class="field-value">{case["INVESTIGATION"]}</div>
            <div class="field-label">ENTITIES IDENTIFIED</div>
            <div class="field-value">{case["ENTITIES"]}</div>
            <div class="field-label">PRIORITY</div>
            <div class="field-value">{chip(case["PRIORITY"])}</div>
            <div class="field-label">STATUS</div>
            <div class="field-value">{case["STATUS"]}</div>
        </div>
        """)

    with right:
        render('<div class="section-label">case actions</div>')
        st.button("◈ View case data")
        st.button("◍ Analyze network")
        st.button("◐ Entity intelligence")
        st.button("▣ Generate report")

    st.markdown("<br>", unsafe_allow_html=True)
    render('<div class="section-label">investigation database</div>')
    st.dataframe(investigations, use_container_width=True, hide_index=True)

    st.info("Demo environment — investigation records shown here use synthetic data for prototype development.")

    st.stop()


# =========================================================
# ENTITY INTELLIGENCE
# =========================================================

if page == "Entity Intelligence":

    # ============================================================
    # TEXT EXTRACTION
    # ============================================================

    render("""
    <div class="dossier">
        <div class="dossier-tag">TEXT EXTRACTION</div>
        <div class="section-label">Extract entities from intelligence text</div>
        <div class="field-label">SOURCE TEXT</div>
    </div>
    """)

    intelligence_text = st.text_area(
        "Paste intelligence text",
        height=180,
        placeholder=(
            "Example: Subject contacted +919876543210 using "
            "john@example.com. Vehicle MH12AB1234 was observed..."
        ),
        label_visibility="collapsed"
    )

    if intelligence_text.strip():

        extracted = extract_entities(intelligence_text)

        render("""
        <div class="section-label" style="margin-top:18px;">
            EXTRACTED ENTITIES
        </div>
        """)

        col1, col2, col3 = st.columns(3)

        with col1:
            render(f"""
            <div class="dossier">
                <div class="field-label">PHONE</div>
                <div class="field-value">
                    {len(extracted["PHONE"])}
                </div>
            </div>
            """)

        with col2:
            render(f"""
            <div class="dossier">
                <div class="field-label">EMAIL</div>
                <div class="field-value">
                    {len(extracted["EMAIL"])}
                </div>
            </div>
            """)

        with col3:
            render(f"""
            <div class="dossier">
                <div class="field-label">VEHICLE</div>
                <div class="field-value">
                    {len(extracted["VEHICLE"])}
                </div>
            </div>
            """)

        if any(extracted.values()):

            render("""
            <div class="section-label" style="margin-top:18px;">
                OBSERVED ENTITIES
            </div>
            """)

            observed_rows = []

            entity_prefix = {
                "PHONE": "PH",
                "EMAIL": "E",
                "VEHICLE": "V"
            }

            for entity_type, values in extracted.items():
                for index, value in enumerate(values, start=1):
                    observed_rows.append({
                        "ENTITY ID": f"OBS-{entity_prefix[entity_type]}-{index:03d}",
                        "ENTITY": value,
                        "TYPE": entity_type,
                        "STATUS": "NEW"
                    })

            observed_df = pd.DataFrame(observed_rows)

            # ---------------------------------------------------------
            # ENTITY RESOLUTION
            # ---------------------------------------------------------

            observed_df["MATCHED ENTITY ID"] = ""
            observed_df["RESOLUTION"] = "NEW"

            for index, row in observed_df.iterrows():

                matches = entities[
                    (entities["TYPE"] == row["TYPE"]) &
                    (
                        entities["ENTITY"].astype(str).str.lower()
                        == str(row["ENTITY"]).lower()
                    )
                ]

                if not matches.empty:
                    observed_df.at[index, "MATCHED ENTITY ID"] = (
                        matches.iloc[0]["ENTITY ID"]
                    )
                    observed_df.at[index, "RESOLUTION"] = "MATCHED"

            render("""
            <div class="section-label" style="margin-top:18px;">
                ENTITY RESOLUTION
            </div>
            """)

            st.dataframe(
                observed_df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.caption(
                "No supported entities detected in the supplied text."
            )


    # ============================================================
    # ENTITY DISCOVERY
    # ============================================================

    page_header(
        "ENTITY DISCOVERY",
        "Entity Intelligence",
        "Associations · connectivity · investigation priority"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("TOTAL ENTITIES", "148")

    with c2:
        st.metric("PERSONS", "42")

    with c3:
        st.metric("PHONE NUMBERS", "31")

    with c4:
        st.metric("HIGH PRIORITY", "17")


    # ============================================================
    # ENTITY SEARCH
    # ============================================================

    st.markdown("<br>", unsafe_allow_html=True)

    render(
        '<div class="section-label">entity search</div>'
    )

    entity_type = st.selectbox(
        "Filter by entity type",
        [
            "ALL",
            "PERSON",
            "PHONE",
            "VEHICLE",
            "LOCATION",
            "ORGANIZATION",
            "EMAIL",
        ],
    )

    filtered_entities = (
        entities
        if entity_type == "ALL"
        else entities[entities["TYPE"] == entity_type]
    )

    # ============================================================
    # IDENTIFIED ENTITIES
    # ============================================================

    st.markdown("<br>", unsafe_allow_html=True)

    render('<div class="section-label">identified entities</div>')

    st.dataframe(
        filtered_entities,
        use_container_width=True,
        hide_index=True
    )

    # ============================================================
    # ENTITY PROFILE
    # ============================================================

    st.markdown("<br>", unsafe_allow_html=True)

    render('<div class="section-label">entity profile</div>')

    if filtered_entities.empty:
        # Guard: an entity-type filter with no matches would otherwise
        # crash the selectbox / .iloc[0] lookup below.
        st.caption("No entities match this filter.")
        st.stop()

    selected_entity = st.selectbox(
        "Select entity",
        filtered_entities["ENTITY ID"],
        label_visibility="collapsed"
    )

    entity = entities[entities["ENTITY ID"] == selected_entity].iloc[0]

    left, right = st.columns([2, 1])

    # ============================================================
    # ENTITY PROFILE CARD
    # ============================================================

    with left:
        icon = entity_icons.get(entity["TYPE"], "●")

        # NOTE: no blank lines inside this block. A blank line here would
        # close the HTML block early (CommonMark HTML-block rules), and
        # Streamlit's markdown renderer would then print everything after
        # it as a literal, indented code block instead of rendering it —
        # this was the exact "raw tags showing as text" bug.
        render(f"""
        <div class="dossier">
            <div class="dossier-tag">ENTITY PROFILE</div>
            <div style="font-size:15px; color:var(--muted); font-family:'JetBrains Mono',monospace;">
                {icon}
            </div>
            <div class="field-value" style="font-size:19px; color:#E9EEF1; margin-top:4px;">
                {entity["ENTITY"]}
            </div>
            <div class="field-label">ENTITY ID</div>
            <div class="field-value">{entity["ENTITY ID"]}</div>
            <div class="field-label">TYPE</div>
            <div class="field-value">{entity["TYPE"]}</div>
            <div class="field-label">NETWORK CONNECTIONS</div>
            <div class="field-value">{entity["CONNECTIONS"]}</div>
            <div class="field-label">INVESTIGATION PRIORITY</div>
            <div class="field-value">{chip(entity["PRIORITY"])}</div>
        </div>
        """)

    # ============================================================
    # ASSOCIATIONS
    # ---------------------------------------------------------
    # Pulled from network_edges/network_nodes so this reflects the
    # entity actually selected above, instead of a static placeholder
    # list of generic category labels.
    # ============================================================

    with right:
        render('<div class="section-label">associations</div>')

        related_rows = []
        for edge in network_edges:
            if edge["source"] == selected_entity:
                other_id = edge["target"]
            elif edge["target"] == selected_entity:
                other_id = edge["source"]
            else:
                continue

            other = network_nodes.get(other_id)
            if not other:
                continue

            other_icon = entity_icons.get(other["type"], "●")
            related_rows.append(
                f'<div class="status-row"><div class="status-dot"></div>'
                f'{other_icon} {other["name"]} · {edge["relationship"]}</div>'
            )

        if related_rows:
            render(f'<div class="dossier">{"".join(related_rows)}</div>')
        else:
            render(
                '<div class="dossier">'
                '<div class="field-value" style="color:var(--muted);">'
                'No relationship records for this entity in the current network graph.'
                '</div></div>'
            )

    # ============================================================
    # ANALYTICAL DISCLAIMER
    # ============================================================

    st.info(
        "Priority indicates an analytical investigation flag based on "
        "observed relationships. It does not indicate guilt."
    )

    st.stop()

# =========================================================
# NETWORK ANALYSIS
# =========================================================

if page == "Network Analysis":

    page_header(
        "RELATIONSHIP MAPPING",
        "Network Analysis",
        "Entity linking · centrality · network intelligence"
    )

    # ---- case selector ----
    selected_case = st.selectbox(
        "Select Case",
        ["CASE-001", "CASE-002"],
        label_visibility="collapsed",
    )

    # ---- build graph ----
    G = nx.Graph()

    for node_id, info in network_nodes.items():
        G.add_node(
            node_id,
            name=info["name"],
            type=info["type"]
        )

    for edge in network_edges:
        if edge["case_id"] != selected_case:
            continue

        source = edge["source"]
        target = edge["target"]

        G.add_edge(
            source,
            target,
            relationship=edge["relationship"],
            evidence=edge["evidence"],
            source_type=edge["source_type"],
            date=edge["date"],
            case_id=edge["case_id"],
        )

    # ---- network metrics ----
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)

    # ---- entity selector ----
    entity_options = {}

    for node_id, info in network_nodes.items():
        icon = entity_icons.get(info["type"], "●")
        entity_options[
            f"{icon}  {info['name']}  ·  {info['type']}"
        ] = node_id

    render('<div class="section-label">investigate entity</div>')

    selected_label = st.selectbox(
        "Select entity to investigate",
        ["None"] + list(entity_options.keys()),
        label_visibility="collapsed"
    )

    selected_node = (
        entity_options.get(selected_label)
        if selected_label != "None"
        else None
    )

    highlighted_nodes = set()

    if selected_node:
        highlighted_nodes.add(selected_node)
        highlighted_nodes.update(G.neighbors(selected_node))

    # ---- layout ----
    pos = nx.spring_layout(G, seed=42, k=2.8, iterations=200)

    edge_x, edge_y = [], []
    for source, target in G.edges():
        x0, y0 = pos[source]; x1, y1 = pos[target]
        edge_x.extend([x0, x1, None]); edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y, mode="lines",
        line=dict(width=1, color="rgba(140,160,175,0.35)"),
        hoverinfo="none",
    )

    rel_x, rel_y, rel_text = [], [], []
    for source, target, data in G.edges(data=True):
        x0, y0 = pos[source]; x1, y1 = pos[target]
        rel_x.append((x0 + x1) / 2); rel_y.append((y0 + y1) / 2)
        rel_text.append(data["relationship"])

    relationship_trace = go.Scatter(
        x=rel_x, y=rel_y, mode="text", text=rel_text,
        textfont=dict(size=8, color="#5B6570", family="JetBrains Mono"),
        hoverinfo="none",
    )

    icon_x, icon_y, icon_text, icon_hover, icon_sizes, icon_colors = [], [], [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        info = G.nodes[node]
        icon = entity_icons.get(info["type"], "●")
        connections = G.degree(node)

        icon_x.append(x); icon_y.append(y); icon_text.append(icon)
        icon_hover.append(
            f"<b>{icon} {info['name']}</b><br>"
            f"Type: {info['type']}<br>"
            f"Direct connections: {connections}<br>"
            f"Degree centrality: {degree_centrality[node]:.2f}<br>"
            f"Betweenness centrality: {betweenness_centrality[node]:.2f}"
        )

        if selected_node:
            if node == selected_node:
                icon_sizes.append(30); icon_colors.append("#C6903F")
            elif node in highlighted_nodes:
                icon_sizes.append(24); icon_colors.append("#4FA6AD")
            else:
                icon_sizes.append(13); icon_colors.append("#3D4750")
        else:
            icon_sizes.append(18 + connections * 2); icon_colors.append("#4FA6AD")

    icon_trace = go.Scatter(
        x=icon_x, y=icon_y, mode="text", text=icon_text,
        textfont=dict(size=icon_sizes, color=icon_colors),
        hovertext=icon_hover, hoverinfo="text",
    )

    name_x, name_y, name_text = [], [], []
    for node in G.nodes():
        x, y = pos[node]
        name_x.append(x); name_y.append(y - 0.08)
        name_text.append(G.nodes[node]["name"])

    name_trace = go.Scatter(
        x=name_x, y=name_y, mode="text", text=name_text,
        textfont=dict(size=10, color="#8CA0AB", family="JetBrains Mono"),
        hoverinfo="none",
    )

    fig = go.Figure(data=[edge_trace, relationship_trace, icon_trace, name_trace])
    fig.update_layout(
        height=640,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        hoverlabel=dict(bgcolor="#0E1116", bordercolor="#4FA6AD", font_size=12, font_family="JetBrains Mono"),
    )

    st.plotly_chart(fig, use_container_width=True)

    # ---- network intelligence ----
    render('<div class="section-label">network intelligence</div>')

    most_connected = max(G.degree, key=lambda item: item[1])
    most_connected_name = network_nodes[most_connected[0]]["name"]

    network_bridge_id = max(betweenness_centrality, key=betweenness_centrality.get)
    network_bridge_name = network_nodes[network_bridge_id]["name"]

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("ENTITIES", G.number_of_nodes())
    with c2: st.metric("RELATIONSHIPS", G.number_of_edges())
    with c3: st.metric("MOST CONNECTED", most_connected_name, f"{most_connected[1]} direct links")
    with c4: st.metric("NETWORK BRIDGE", network_bridge_name)

    # ---- selected entity intelligence ----
    if selected_node:

        info = network_nodes[selected_node]
        icon = entity_icons.get(info["type"], "●")

        st.markdown("<br>", unsafe_allow_html=True)
        render('<div class="section-label">selected entity intelligence</div>')

        render(f"""
        <div class="dossier">
            <div class="dossier-tag">ENTITY</div>
            <div style="font-size:16px; color:var(--priority); font-family:'JetBrains Mono',monospace;">{icon}</div>
            <div class="field-value" style="font-size:19px; color:#E9EEF1; margin-top:4px;">
                {info["name"]}
            </div>
            <div class="field-label">{info["type"]} · NETWORK ENTITY</div>
        </div>
        """)

        m1, m2, m3 = st.columns(3)
        with m1: st.metric("DIRECT CONNECTIONS", G.degree(selected_node))
        with m2: st.metric("DEGREE CENTRALITY", f"{degree_centrality[selected_node]:.2f}")
        with m3: st.metric("BETWEENNESS", f"{betweenness_centrality[selected_node]:.2f}")

        render('<div class="section-label" style="margin-top:16px;">direct associations</div>')

        associations = []
        for neighbor in G.neighbors(selected_node):
            neighbor_info = network_nodes[neighbor]
            relation = G[selected_node][neighbor]["relationship"]
            associations.append({
                "Entity": neighbor_info["name"],
                "Type": neighbor_info["type"],
                "Relationship": relation,
            })

        if associations:
            st.dataframe(pd.DataFrame(associations), use_container_width=True, hide_index=True)
        else:
            st.caption("No direct associations available.")

        render('<div class="section-label" style="margin-top:16px;">relationship evidence</div>')

        evidence_records = []

        for neighbor in G.neighbors(selected_node):
            edge_data = G[selected_node][neighbor]

            neighbor_info = network_nodes[neighbor]

            evidence_records.append({
                "Entity": neighbor_info["name"],
                "Relationship": edge_data["relationship"],
                "Evidence": edge_data["evidence"],
                "Source": edge_data["source_type"],
                "Date": edge_data["date"],
            })

        if evidence_records:
            st.dataframe(
                pd.DataFrame(evidence_records),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("No evidence records attached.")

        connection_count = G.degree(selected_node)
        if connection_count >= 4:
            insight_text = "High network connectivity detected. This entity has multiple direct relationships within the available dataset."
        elif connection_count >= 2:
            insight_text = "Multiple network relationships detected. Review the associated entities and relationship context."
        else:
            insight_text = "Limited direct connectivity detected within the available dataset."

        st.info(insight_text + " Network connectivity is an analytical signal and does not establish criminal activity or guilt.")

    else:
        st.caption("Select an entity above to view its relationships, connectivity and analytical indicators.")

    render("""
    <div style="margin-top:22px; padding:11px 14px; border-left:2px solid #4FA6AD;
                background:#0E1116; color:#5B6570; font-size:10.5px;
                font-family:'JetBrains Mono',monospace; letter-spacing:0.5px;">
        SYNTHETIC DEMONSTRATION DATA · ANALYTICAL DECISION SUPPORT · HUMAN REVIEW REQUIRED
    </div>
    """)

    st.stop()


# =========================================================
# PHONE INTELLIGENCE
# =========================================================

if page == "Phone Intelligence":

    page_header(
        "SIGNAL METADATA",
        "Phone Intelligence",
        "Number lookup · network linkage · analytical metadata"
    )

    # Normalize the type before filtering so inconsistent casing or whitespace
    # in imported data does not make valid phone records disappear.
    phone_entities = entities[
        entities["TYPE"].astype(str).str.strip().str.upper() == "PHONE"
    ].copy()

    render("""
    <div class="dossier">
        <div class="dossier-tag">NUMBER LOOKUP</div>
        <div class="field-label">SELECT PHONE NUMBER</div>
        <div class="field-value" style="font-size:13px; color:var(--muted);">
            Select a phone entity from the current synthetic investigation dataset.
        </div>
    </div>
    """)

    if not phone_entities.empty:

        selected_phone = st.selectbox(
            "Select phone number",
            phone_entities["ENTITY"].tolist(),
            label_visibility="collapsed"
        )

        if st.button("ANALYZE NUMBER"):
            selected_row = phone_entities[
                phone_entities["ENTITY"] == selected_phone
            ].iloc[0]

            # Synthetic metadata for prototype/demo purposes
            phone_metadata = {
                "PH-001": {
                    "OPERATOR": "Demo Telecom",
                    "REGION": "Maharashtra",
                    "NUMBER TYPE": "Mobile",
                    "FIRST OBSERVED": "2026-08-14",
                    "LAST OBSERVED": "2026-08-18",
                },
                "PH-002": {
                    "OPERATOR": "Demo Telecom",
                    "REGION": "Maharashtra",
                    "NUMBER TYPE": "Mobile",
                    "FIRST OBSERVED": "2026-08-18",
                    "LAST OBSERVED": "2026-08-20",
                },
            }

            metadata = phone_metadata.get(
                selected_row["ENTITY ID"],
                {
                    "OPERATOR": "Unknown",
                    "REGION": "Unknown",
                    "NUMBER TYPE": "Unknown",
                    "FIRST OBSERVED": "Unknown",
                    "LAST OBSERVED": "Unknown",
                }
            )

            render(f"""
            <div class="dossier" style="margin-top:18px;">
                <div class="dossier-tag">PHONE METADATA</div>
                <div class="field-label">ENTITY ID</div>
                <div class="field-value">{selected_row["ENTITY ID"]}</div>
                <div class="field-label" style="margin-top:14px;">PHONE NUMBER</div>
                <div class="field-value">{selected_row["ENTITY"]}</div>
                <div class="field-label" style="margin-top:14px;">NUMBER TYPE</div>
                <div class="field-value">{metadata["NUMBER TYPE"]}</div>
                <div class="field-label" style="margin-top:14px;">OPERATOR</div>
                <div class="field-value">{metadata["OPERATOR"]}</div>
                <div class="field-label" style="margin-top:14px;">REGION</div>
                <div class="field-value">{metadata["REGION"]}</div>
                <div class="field-label" style="margin-top:14px;">FIRST OBSERVED</div>
                <div class="field-value">{metadata["FIRST OBSERVED"]}</div>
                <div class="field-label" style="margin-top:14px;">LAST OBSERVED</div>
                <div class="field-value">{metadata["LAST OBSERVED"]}</div>
                <div class="field-label" style="margin-top:14px;">NETWORK CONNECTIONS</div>
                <div class="field-value">{selected_row["CONNECTIONS"]}</div>
                <div class="field-label" style="margin-top:14px;">ANALYTICAL PRIORITY</div>
                <div class="field-value">{selected_row["PRIORITY"]}</div>
            </div>
            """)

    else:

        render("""
        <div class="dossier">
            <div class="dossier-tag">NO DATA</div>
            <div class="field-value">
                No phone entities are currently available in the synthetic dataset.
            </div>
        </div>
        """)

    st.stop()


# =========================================================
# REPORTS
# =========================================================

if page == "Reports":

    page_header(
        "CASE OUTPUT",
        "Reports",
        "Investigation summary · analytical findings · report preparation"
    )

    render("""
    <div class="dossier">
        <div class="dossier-tag">REPORT WORKSPACE</div>
        <div class="field-label">PURPOSE</div>
        <div class="field-value">
            Prepare a structured analytical summary from the
            current investigation dataset.
        </div>
        <div class="field-label" style="margin-top:14px;">DATA STATUS</div>
        <div class="field-value">Synthetic / demonstration dataset</div>
        <div class="field-label" style="margin-top:14px;">OUTPUT STATUS</div>
        <div class="field-value">Draft</div>
    </div>
    """)

    render('<div class="section-label" style="margin-top:26px;">REPORT TYPE</div>')

    report_type = st.selectbox(
        "Report type",
        [
            "Investigation Summary",
            "Entity Intelligence Report",
            "Network Analysis Report",
            "Phone Intelligence Report",
        ],
        label_visibility="collapsed"
    )

    if st.button("GENERATE REPORT"):

        total_entities = len(entities)
        total_relationships = len(network_edges)
        high_priority = len(entities[entities["PRIORITY"] == "HIGH"])
        entity_types = entities["TYPE"].value_counts()

        render('<div class="section-label" style="margin-top:26px;">GENERATED REPORT</div>')

        render(f"""
        <div class="dossier" style="margin-top:14px;">
            <div class="dossier-tag">INVESTIGATION SUMMARY</div>
            <div class="field-label">CASE REFERENCE</div>
            <div class="field-value">CASE-001</div>
            <div class="field-label" style="margin-top:14px;">REPORT TYPE</div>
            <div class="field-value">{report_type}</div>
            <div class="field-label" style="margin-top:14px;">TOTAL ENTITIES</div>
            <div class="field-value">{total_entities}</div>
            <div class="field-label" style="margin-top:14px;">IDENTIFIED RELATIONSHIPS</div>
            <div class="field-value">{total_relationships}</div>
            <div class="field-label" style="margin-top:14px;">HIGH-PRIORITY ENTITIES</div>
            <div class="field-value">{high_priority}</div>
        </div>
        """)

        render('<div class="section-label" style="margin-top:26px;">ENTITY DISTRIBUTION</div>')

        # Each row is built as a single line — a blank/whitespace-only line
        # between rows would otherwise split the surrounding HTML block
        # (see the render() blocks elsewhere in this file for why).
        distribution_rows = "".join(
            f"<tr><td>{entity_type}</td><td>{count}</td></tr>"
            for entity_type, count in entity_types.items()
        )

        render(f"""
        <div class="dossier" style="margin-top:14px;">
            <div class="dossier-tag">ENTITY BREAKDOWN</div>
            <table style="width:100%; border-collapse:collapse; font-family:'JetBrains Mono', monospace; font-size:12px;">
                <thead>
                    <tr>
                        <th style="text-align:left; padding:8px 0;">TYPE</th>
                        <th style="text-align:left; padding:8px 0;">COUNT</th>
                    </tr>
                </thead>
                <tbody>
                    {distribution_rows}
                </tbody>
            </table>
        </div>
        """)

        render(f"""
        <div class="dossier" style="margin-top:20px;">
            <div class="dossier-tag">ANALYTICAL NOTICE</div>
            <div class="field-value" style="font-size:12px; color:var(--muted);">
                This report summarizes analytical signals contained within the
                synthetic investigation dataset. Relationships and priority
                levels do not establish criminal activity or guilt.
            </div>
        </div>
        """)

    st.stop()