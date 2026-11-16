import streamlit as st
import streamlit.components.v1 as components
import os

# Streamlit Page Config - Full width layout
st.set_page_config(
    page_title="Transworld GIS & NOC Portal",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit chrome
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container { padding: 0rem !important; margin: 0rem !important; max-width: 100% !important; }
        iframe { position: fixed; top: 0; left: 0; width: 100vw !important; height: 100vh !important; border: none; margin: 0; padding: 0; overflow: hidden; z-index: 999999; }
    </style>
""", unsafe_allow_html=True)

# Read index.html
html_file_path = os.path.join(os.path.dirname(__file__), "index.html")
html_content = ""
if os.path.exists(html_file_path):
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

# ---------------------------------------------------------------------------
# LIVE SUPABASE 2-WAY FULL SYNC ENGINE (REST API)
# ---------------------------------------------------------------------------
SUPABASE_URL = "https://qefwkiqlxzomqbxnhijl.supabase.co"
SUPABASE_KEY = "sb_publishable_nJjqcuejEJnXphyT9v1PCQ_WjP_YC4s"

supabase_bridge = f"""
<script>
(function() {{
    var SB_URL = "{SUPABASE_URL}/rest/v1";
    var SB_KEY = "{SUPABASE_KEY}";
    var SB_HEADERS = {{
        "apikey": SB_KEY,
        "Authorization": "Bearer " + SB_KEY,
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }};

    var originalFetch = window.fetch;

    window.fetch = function(url, options) {{
        var u = typeof url === 'string' ? url : (url && url.url ? url.url : '');
        var opts = options || {{}};
        var method = (opts.method || 'GET').toUpperCase();

        // 1. LOGIN API
        if (u.indexOf('/api/login') !== -1) {{
            var body = {{}};
            try {{ if (opts.body) body = JSON.parse(opts.body); }} catch(e) {{}}
            var email = (body.email || '').trim().toLowerCase();
            var pw = body.password || '';

            return originalFetch(SB_URL + "/team_members?email=ilike." + encodeURIComponent(email) + "&select=*", {{
                headers: SB_HEADERS
            }})
            .then(function(res) {{ return res.json(); }})
            .then(function(users) {{
                if (users && users.length > 0) {{
                    var user = users[0];
                    if (pw === 'transworld123' || pw === 'admin' || pw === 'password' || pw === 'boss' || pw === '123456') {{
                        return new Response(JSON.stringify({{
                            status: 'ok',
                            user: {{
                                email: user.email,
                                name: user.name,
                                role: user.role,
                                region: user.region,
                                designation: user.designation || ''
                            }}
                        }}), {{ status: 200, headers: {{ 'Content-Type': 'application/json' }} }});
                    }}
                }}
                return new Response(JSON.stringify({{ error: "Invalid email or password" }}), {{ status: 401, headers: {{ 'Content-Type': 'application/json' }} }});
            }})
            .catch(function(err) {{
                return new Response(JSON.stringify({{ error: "Database error: " + err.message }}), {{ status: 500 }});
            }});
        }}

        // 2. LOGOUT API
        if (u.indexOf('/api/logout') !== -1) {{
            return Promise.resolve(new Response(JSON.stringify({{ status: 'logged_out' }}), {{ status: 200 }}));
        }}

        // 3. DB STATUS
        if (u.indexOf('/api/db-status') !== -1) {{
            return Promise.resolve(new Response(JSON.stringify({{ status: 'connected', database: 'Supabase Cloud PostgreSQL' }}), {{ status: 200 }}));
        }}

        // 4. GET CUSTOMERS
        if (u.indexOf('/api/customers') !== -1) {{
            return originalFetch(SB_URL + "/subscribers?select=*,latitude,longitude&order=ont_id.asc", {{ headers: SB_HEADERS }})
            .then(function(res) {{ return res.json(); }})
            .then(function(rows) {{
                var mapped = (rows || []).map(function(s) {{
                    return {{
                        ont_id: s.ont_id,
                        subscriber_name: s.subscriber_name,
                        phone_number: s.phone_number,
                        service_address: s.service_address,
                        building_name: s.building_name,
                        plot_no: s.plot_no,
                        street_no: s.street_no,
                        block_name: s.block_name,
                        area_name: s.area_name,
                        sub_area: s.sub_area,
                        city: s.city,
                        lat: parseFloat(s.latitude),
                        lng: parseFloat(s.longitude),
                        fat_id: s.fat_id,
                        odb_id: s.odb_id,
                        olt_name: s.olt_name,
                        frame_no: s.frame_no,
                        slot_no: s.slot_no,
                        port_no: s.port_no,
                        ip_address: s.ip_address,
                        mac_address: s.mac_address,
                        bandwidth_plan: s.bandwidth_plan,
                        bandwidth_mbps: s.bandwidth_mbps,
                        connection_status: s.connection_status,
                        is_up: s.is_up,
                        last_down_cause: s.last_down_cause,
                        current_alarm: s.current_alarm,
                        rx_ont_dbm: parseFloat(s.rx_ont_dbm || -21.5),
                        rx_olt_dbm: parseFloat(s.rx_olt_dbm || -23.1),
                        live_dl: (s.is_up ? 34.0 : 0.0),
                        live_ul: (s.is_up ? 8.0 : 0.0)
                    }};
                }});
                return new Response(JSON.stringify(mapped), {{ status: 200, headers: {{ 'Content-Type': 'application/json' }} }});
            }});
        }}

        // 5. GET TEAMS
        if (u.indexOf('/api/teams') !== -1) {{
            return originalFetch(SB_URL + "/team_members?select=*&order=region.asc,name.asc", {{ headers: SB_HEADERS }})
            .then(function(res) {{ return res.json(); }})
            .then(function(rows) {{
                return new Response(JSON.stringify(rows || []), {{ status: 200, headers: {{ 'Content-Type': 'application/json' }} }});
            }});
        }}

        // 6. GET FIELD TASKS
        if (u.indexOf('/api/tasks') !== -1 && method === 'GET') {{
            return originalFetch(SB_URL + "/field_tasks?select=*,team_members(name,designation,avatar_color)&order=deadline.asc", {{ headers: SB_HEADERS }})
            .then(function(res) {{ return res.json(); }})
            .then(function(rows) {{
                var mapped = (rows || []).map(function(t) {{
                    var tm = t.team_members || {{}};
                    return {{
                        task_id: t.task_id,
                        task_code: t.task_code,
                        title: t.title,
                        task_type: t.task_type,
                        region: t.region,
                        area_name: t.area_name,
                        lat: parseFloat(t.latitude),
                        lng: parseFloat(t.longitude),
                        assigned_to: t.assigned_to,
                        assigned_by: t.assigned_by,
                        deadline_str: (t.deadline || '').replace('T', ' ').slice(0, 16),
                        deadline: t.deadline,
                        priority: t.priority,
                        status: t.status,
                        description: t.description,
                        submission_notes: t.submission_notes,
                        report_filename: t.report_filename,
                        boss_feedback: t.boss_feedback,
                        assignee_name: tm.name || t.assigned_to,
                        assignee_designation: tm.designation || '',
                        avatar_color: tm.avatar_color || '#3b82f6'
                    }};
                }});
                return new Response(JSON.stringify(mapped), {{ status: 200, headers: {{ 'Content-Type': 'application/json' }} }});
            }});
        }}

        // 7. CREATE NEW TASK (POST to Supabase)
        if (u.indexOf('/api/tasks/create') !== -1 && method === 'POST') {{
            var body = {{}};
            try {{ body = JSON.parse(opts.body); }} catch(e) {{}}
            var rndNum = Math.floor(1000 + Math.random() * 9000);
            var taskCode = "TSK-" + (body.region ? body.region.slice(0, 3).toUpperCase() : "NOR") + "-" + rndNum;
            var payload = {{
                task_code: taskCode,
                title: body.title,
                task_type: body.task_type || "Survey Task",
                region: body.region || "North",
                area_name: body.area_name || "",
                latitude: body.latitude,
                longitude: body.longitude,
                assigned_to: body.assigned_to,
                assigned_by: "boss@transworld.com",
                deadline: body.deadline,
                priority: body.priority || "Medium",
                status: "Pending",
                description: body.description || ""
            }};

            return originalFetch(SB_URL + "/field_tasks", {{
                method: "POST",
                headers: SB_HEADERS,
                body: JSON.stringify(payload)
            }})
            .then(function(res) {{ return res.json(); }})
            .then(function(inserted) {{
                var created = (inserted && inserted.length > 0) ? inserted[0] : payload;
                return new Response(JSON.stringify({{ status: "created", task: created }}), {{ status: 200 }});
            }});
        }}

        // 8. UPDATE TASK STATUS (MEMBER START / SUBMIT to Supabase)
        if (u.indexOf('/api/tasks/update-status') !== -1 && method === 'POST') {{
            var body = {{}};
            try {{ body = JSON.parse(opts.body); }} catch(e) {{}}
            var patch = {{
                status: body.status,
                submission_notes: body.submission_notes || null,
                report_filename: body.report_filename || null,
                submitted_at: new Date().toISOString()
            }};

            return originalFetch(SB_URL + "/field_tasks?task_id=eq." + body.task_id, {{
                method: "PATCH",
                headers: SB_HEADERS,
                body: JSON.stringify(patch)
            }})
            .then(function() {{
                return new Response(JSON.stringify({{ status: "updated", task_id: body.task_id, new_status: body.status }}), {{ status: 200 }});
            }});
        }}

        // 9. BOSS REVIEW & DECISION (Accept / Reject to Supabase)
        if (u.indexOf('/api/tasks/review') !== -1 && method === 'POST') {{
            var body = {{}};
            try {{ body = JSON.parse(opts.body); }} catch(e) {{}}
            var patch = {{
                status: body.decision,
                boss_feedback: body.boss_feedback || "",
                reviewed_at: new Date().toISOString()
            }};

            return originalFetch(SB_URL + "/field_tasks?task_id=eq." + body.task_id, {{
                method: "PATCH",
                headers: SB_HEADERS,
                body: JSON.stringify(patch)
            }})
            .then(function() {{
                return new Response(JSON.stringify({{ status: "reviewed", task_id: body.task_id, decision: body.decision }}), {{ status: 200 }});
            }});
        }}

        return originalFetch.apply(this, arguments);
    }};
    console.log("Transworld Supabase Real-Time Engine Active!");
}})();
</script>
"""

if "</head>" in html_content:
    html_content = html_content.replace("</head>", supabase_bridge + "\n</head>")
else:
    html_content = supabase_bridge + html_content

components.html(html_content, height=1000, scrolling=True)
