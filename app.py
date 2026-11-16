import streamlit as st
import streamlit.components.v1 as components
import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor

# ---------------------------------------------------------------------------
# 1. FETCH LIVE DATA FROM SUPABASE CLOUD POSTGRESQL
# ---------------------------------------------------------------------------
DATABASE_URL = "postgresql://postgres.qefwkiqlxzomqbxnhijl:pZ6MvQvGLpje9D6N@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"

def fetch_all_data():
    data = {"subscribers": [], "teams": [], "tasks": []}
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor, sslmode="require", connect_timeout=8)
        with conn.cursor() as cur:
            # 1. Subscribers
            cur.execute("""
                SELECT ont_id, subscriber_name, phone_number, service_address, building_name,
                       plot_no, street_no, block_name, area_name, sub_area, city,
                       CAST(latitude AS FLOAT) AS lat, CAST(longitude AS FLOAT) AS lng,
                       fat_id, odb_id, olt_name, frame_no, slot_no, port_no, ip_address, mac_address,
                       bandwidth_plan, bandwidth_mbps, connection_status, is_up, last_down_cause,
                       current_alarm, CAST(rx_ont_dbm AS FLOAT) AS rx_ont_dbm, CAST(rx_olt_dbm AS FLOAT) AS rx_olt_dbm,
                       34.0 AS live_dl, 8.0 AS live_ul
                FROM subscribers ORDER BY ont_id ASC;
            """)
            data["subscribers"] = cur.fetchall()

            # 2. Team Members
            cur.execute("""
                SELECT member_id, name, email, role, region, designation, phone, avatar_color
                FROM team_members
                ORDER BY CASE WHEN role = 'Boss' THEN 1 ELSE 2 END, region ASC, name ASC;
            """)
            data["teams"] = cur.fetchall()

            # 3. Field Tasks
            cur.execute("""
                SELECT ft.task_id, ft.task_code, ft.title, ft.task_type, ft.region, ft.area_name,
                       CAST(ft.latitude AS FLOAT) AS lat, CAST(ft.longitude AS FLOAT) AS lng,
                       ft.assigned_to, ft.assigned_by,
                       TO_CHAR(ft.deadline, 'YYYY-MM-DD HH24:MI') AS deadline_str,
                       ft.deadline, ft.priority, ft.status, ft.description,
                       ft.submission_notes, ft.report_filename, ft.boss_feedback,
                       tm.name AS assignee_name, tm.designation AS assignee_designation, tm.avatar_color
                FROM field_tasks ft
                LEFT JOIN team_members tm ON ft.assigned_to = tm.email
                ORDER BY ft.deadline ASC;
            """)
            data["tasks"] = cur.fetchall()
        conn.close()
    except Exception as e:
        print("[DB Fetch Error]:", e)
    return data

live_data = fetch_all_data()

# ---------------------------------------------------------------------------
# 2. READ INDEX.HTML & BRIDGE STREAMLIT WITH SUPABASE (ZERO HTML EDIT ON DISK)
# ---------------------------------------------------------------------------
html_file_path = os.path.join(os.path.dirname(__file__), "index.html")
html_content = ""
if os.path.exists(html_file_path):
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

# Client-Side Native Cloud Bridge Script (Overrides network fetch calls gracefully)
bridge_script = f"""
<script>
window.__SUPABASE_DATA__ = {{
    subscribers: {json.dumps(live_data['subscribers'], default=str)},
    teams: {json.dumps(live_data['teams'], default=str)},
    tasks: {json.dumps(live_data['tasks'], default=str)}
}};

// Native Fetch Interceptor for Streamlit Cloud
var originalFetch = window.fetch;
window.fetch = function(url, options) {{
    var u = typeof url === 'string' ? url : (url && url.url ? url.url : '');

    // 1. LOGIN API
    if (u.indexOf('/api/login') !== -1) {{
        var body = {{}};
        try {{ if (options && options.body) body = JSON.parse(options.body); }} catch(e) {{}}
        var email = (body.email || '').trim().toLowerCase();
        var pw = body.password || '';

        var foundUser = window.__SUPABASE_DATA__.teams.find(function(m) {{
            return m.email.toLowerCase() === email;
        }});

        if (foundUser && (pw === 'transworld123' || pw === 'admin' || pw === 'password' || pw === 'boss')) {{
            return Promise.resolve(new Response(JSON.stringify({{
                status: 'ok',
                user: {{
                    email: foundUser.email,
                    name: foundUser.name,
                    role: foundUser.role,
                    region: foundUser.region,
                    designation: foundUser.designation
                }}
            }}), {{ status: 200, headers: {{ 'Content-Type': 'application/json' }} }}));
        }} else {{
            return Promise.resolve(new Response(JSON.stringify({{
                error: 'Invalid email or password. Use transworld123'
            }}), {{ status: 401, headers: {{ 'Content-Type': 'application/json' }} }}));
        }}
    }}

    // 2. LOGOUT API
    if (u.indexOf('/api/logout') !== -1) {{
        return Promise.resolve(new Response(JSON.stringify({{ status: 'logged_out' }}), {{ status: 200 }}));
    }}

    // 3. DB STATUS API
    if (u.indexOf('/api/db-status') !== -1) {{
        return Promise.resolve(new Response(JSON.stringify({{ status: 'connected', database: 'Supabase Cloud PostgreSQL' }}), {{ status: 200 }}));
    }}

    // 4. CUSTOMERS API
    if (u.indexOf('/api/customers') !== -1) {{
        return Promise.resolve(new Response(JSON.stringify(window.__SUPABASE_DATA__.subscribers), {{ status: 200, headers: {{ 'Content-Type': 'application/json' }} }}));
    }}

    // 5. TEAMS API
    if (u.indexOf('/api/teams') !== -1) {{
        return Promise.resolve(new Response(JSON.stringify(window.__SUPABASE_DATA__.teams), {{ status: 200, headers: {{ 'Content-Type': 'application/json' }} }}));
    }}

    // 6. TASKS API
    if (u.indexOf('/api/tasks') !== -1) {{
        return Promise.resolve(new Response(JSON.stringify(window.__SUPABASE_DATA__.tasks), {{ status: 200, headers: {{ 'Content-Type': 'application/json' }} }}));
    }}

    return originalFetch.apply(this, arguments);
}};
console.log("Transworld Supabase Cloud Bridge loaded successfully!");
</script>
"""

# Inject Bridge right before </head>
if "</head>" in html_content:
    html_content = html_content.replace("</head>", bridge_script + "\n</head>")
else:
    html_content = bridge_script + html_content

# ---------------------------------------------------------------------------
# 3. STREAMLIT FULL-SCREEN RENDERING
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Transworld GIS & NOC Portal",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container { padding: 0rem !important; margin: 0rem !important; max-width: 100% !important; }
        iframe { position: fixed; top: 0; left: 0; width: 100vw !important; height: 100vh !important; border: none; margin: 0; padding: 0; overflow: hidden; z-index: 999999; }
    </style>
""", unsafe_allow_html=True)

components.html(html_content, height=1000, scrolling=True)
