import sys
from pathlib import Path
_root = Path(__file__).resolve().parent if Path(__file__).resolve().parent.name != 'scratch' else Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))
from db_config import DB_CONFIG
"""
Database Setup & Seed Script for Role-Based Task Management & Field Dispatch System
Database: transworlddatabase
"""

import psycopg2
from datetime import datetime, timedelta

def setup_tasks_schema():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    print("[1/3] Creating tables: team_members & field_tasks...")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS team_members (
        member_id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(150) UNIQUE NOT NULL,
        role VARCHAR(30) NOT NULL DEFAULT 'Member', -- 'Boss' or 'Member'
        region VARCHAR(50) NOT NULL, -- 'North', 'Central', 'South', 'All'
        designation VARCHAR(100),
        phone VARCHAR(30),
        avatar_color VARCHAR(10) DEFAULT '#2b8be6',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS field_tasks (
        task_id SERIAL PRIMARY KEY,
        task_code VARCHAR(30) UNIQUE NOT NULL,
        title VARCHAR(200) NOT NULL,
        task_type VARCHAR(50) NOT NULL, -- 'Survey Task', 'Database Task', 'Planning Task', 'BOQ Task'
        region VARCHAR(50) NOT NULL, -- 'North', 'Central', 'South'
        area_name VARCHAR(150),
        latitude NUMERIC(10, 6),
        longitude NUMERIC(10, 6),
        assigned_to VARCHAR(150) REFERENCES team_members(email) ON UPDATE CASCADE ON DELETE SET NULL,
        assigned_by VARCHAR(150) DEFAULT 'boss@transworld.com',
        deadline TIMESTAMP NOT NULL,
        priority VARCHAR(20) DEFAULT 'Medium', -- 'Critical', 'High', 'Medium', 'Low'
        status VARCHAR(30) DEFAULT 'Pending', -- 'Pending', 'In Progress', 'Submitted for Review', 'Accepted', 'Rejected'
        description TEXT,
        submission_notes TEXT,
        report_filename VARCHAR(255),
        boss_feedback TEXT,
        submitted_at TIMESTAMP,
        reviewed_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_tasks_region ON field_tasks (region);
    CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to ON field_tasks (assigned_to);
    CREATE INDEX IF NOT EXISTS idx_tasks_status ON field_tasks (status);
    """)
    conn.commit()

    print("[2/3] Seeding Team Directory (Boss + 25 North + 10 South + 12 Central)...")
    members = [
        # Boss / Management
        ('Engr. Tariq Mehmood (Boss)', 'boss@transworld.com', 'Boss', 'All', 'Chief Operations Officer / Head of GIS & Planning', '0300-8889900', '#f59e0b'),

        # North Team (25 members as requested)
        ('Muhammad Ali', 'ali.north@transworld.com', 'Member', 'North', 'Senior GIS Surveyor', '0300-1110001', '#3b82f6'),
        ('Usman Khan', 'usman.north@transworld.com', 'Member', 'North', 'Network Planning Engineer', '0300-1110002', '#10b981'),
        ('Hamza Tariq', 'hamza.north@transworld.com', 'Member', 'North', 'BOQ Estimator Lead', '0300-1110003', '#8b5cf6'),
        ('Bilal Ahmed', 'bilal.north@transworld.com', 'Member', 'North', 'FTTH Field Technician', '0300-1110004', '#ec4899'),
        ('Asadullah', 'asad.north@transworld.com', 'Member', 'North', 'Database Specialist', '0300-1110005', '#06b6d4'),
        ('Zain ul Abideen', 'zain.north@transworld.com', 'Member', 'North', 'Optical Power Technician', '0300-1110006', '#f97316'),
        ('Faisal Raza', 'faisal.north@transworld.com', 'Member', 'North', 'Route Surveyor', '0300-1110007', '#14b8a6'),
        ('Kashif Nawaz', 'kashif.north@transworld.com', 'Member', 'North', 'OLT Integration Specialist', '0300-1110008', '#6366f1'),
        ('Naveed Akhtar', 'naveed.north@transworld.com', 'Member', 'North', 'Civil & Trench Lead', '0300-1110009', '#eab308'),
        ('Sana Sheikh', 'sana.north@transworld.com', 'Member', 'North', 'GIS Analyst', '0300-1110010', '#a855f7'),
        ('Ayesha Malik', 'ayesha.north@transworld.com', 'Member', 'North', 'Planning Engineer', '0300-1110011', '#ec4899'),
        ('Waleed Butt', 'waleed.north@transworld.com', 'Member', 'North', 'Field QA/QC Officer', '0300-1110012', '#3b82f6'),
        ('Imran Shahid', 'imran.north@transworld.com', 'Member', 'North', 'Fiber Splicing Lead', '0300-1110013', '#10b981'),
        ('Shahid Iqbal', 'shahid.north@transworld.com', 'Member', 'North', 'Survey Assistant', '0300-1110014', '#f59e0b'),
        ('Hassan Raza', 'hassan.north@transworld.com', 'Member', 'North', 'BOQ Assistant', '0300-1110015', '#06b6d4'),
        ('Omer Farooq', 'omer.north@transworld.com', 'Member', 'North', 'Fiber Line Technician', '0300-1110016', '#84cc16'),
        ('Danish Ali', 'danish.north@transworld.com', 'Member', 'North', 'ODB / FAT Technician', '0300-1110017', '#6366f1'),
        ('Fahad Mustafa', 'fahad.north@transworld.com', 'Member', 'North', 'GIS Drafter & Cartographer', '0300-1110018', '#14b8a6'),
        ('Haris Mehmood', 'haris.north@transworld.com', 'Member', 'North', 'Field Inspector', '0300-1110019', '#e11d48'),
        ('Rehan Ahmed', 'rehan.north@transworld.com', 'Member', 'North', 'Field Survey Specialist', '0300-1110020', '#3b82f6'),
        ('Saad Gill', 'saad.north@transworld.com', 'Member', 'North', 'Network Maintenance Tech', '0300-1110021', '#10b981'),
        ('Zubair Ansari', 'zubair.north@transworld.com', 'Member', 'North', 'Planning Technician', '0300-1110022', '#a855f7'),
        ('Kamran Mirza', 'kamran.north@transworld.com', 'Member', 'North', 'Field Supervisor', '0300-1110023', '#f59e0b'),
        ('Farhan Bhatti', 'farhan.north@transworld.com', 'Member', 'North', 'BOQ Surveyor', '0300-1110024', '#06b6d4'),
        ('Salman Javed', 'salman.north@transworld.com', 'Member', 'North', 'Spatial Database Administrator', '0300-1110025', '#8b5cf6'),

        # South Team (10 members as requested)
        ('Tariq Jameel', 'tariq.south@transworld.com', 'Member', 'South', 'South Regional Lead', '0300-2220001', '#f59e0b'),
        ('Arham Butt', 'arham.south@transworld.com', 'Member', 'South', 'Field Surveyor', '0300-2220002', '#3b82f6'),
        ('Babar Azam', 'babar.south@transworld.com', 'Member', 'South', 'GIS Specialist', '0300-2220003', '#10b981'),
        ('Dawood Khan', 'dawood.south@transworld.com', 'Member', 'South', 'Network Planner', '0300-2220004', '#06b6d4'),
        ('Ehsan Ullah', 'ehsan.south@transworld.com', 'Member', 'South', 'BOQ Estimator Lead', '0300-2220005', '#8b5cf6'),
        ('Ghalib Hussain', 'ghalib.south@transworld.com', 'Member', 'South', 'Fiber Technician', '0300-2220006', '#ec4899'),
        ('Habib Ur Rehman', 'habib.south@transworld.com', 'Member', 'South', 'Splicing Technician', '0300-2220007', '#14b8a6'),
        ('Irfan Ali', 'irfan.south@transworld.com', 'Member', 'South', 'Field Tech', '0300-2220008', '#6366f1'),
        ('Junaid Jamshed', 'junaid.south@transworld.com', 'Member', 'South', 'Survey Engineer', '0300-2220009', '#eab308'),
        ('Khalid Mehmood', 'khalid.south@transworld.com', 'Member', 'South', 'Database Technician', '0300-2220010', '#a855f7'),

        # Central Team (12 members)
        ('Mohammad Rizwan', 'rizwan.central@transworld.com', 'Member', 'Central', 'Central Regional Supervisor', '0300-3330001', '#f59e0b'),
        ('Adeel Qureshi', 'adeel.central@transworld.com', 'Member', 'Central', 'Field Route Surveyor', '0300-3330002', '#3b82f6'),
        ('Adnan Siddiqui', 'adnan.central@transworld.com', 'Member', 'Central', 'BOQ Quantity Analyst', '0300-3330003', '#10b981'),
        ('Azam Khan', 'azam.central@transworld.com', 'Member', 'Central', 'GIS Senior Engineer', '0300-3330004', '#06b6d4'),
        ('Abdul Basit', 'basit.central@transworld.com', 'Member', 'Central', 'Network Route Planner', '0300-3330005', '#8b5cf6'),
        ('Danyal Ahmed', 'danyal.central@transworld.com', 'Member', 'Central', 'Field Operations Tech', '0300-3330006', '#ec4899'),
        ('Ejaz Ahmed', 'ejaz.central@transworld.com', 'Member', 'Central', 'OLT Integration Specialist', '0300-3330007', '#14b8a6'),
        ('Faizan Sheikh', 'faizan.central@transworld.com', 'Member', 'Central', 'Survey Assistant', '0300-3330008', '#6366f1'),
        ('Ghufran Ali', 'ghufran.central@transworld.com', 'Member', 'Central', 'Fiber Splicing Lead', '0300-3330009', '#eab308'),
        ('Haider Ali', 'haider.central@transworld.com', 'Member', 'Central', 'Planning Assistant', '0300-3330010', '#a855f7'),
        ('Idrees Khan', 'idrees.central@transworld.com', 'Member', 'Central', 'Field Inspector', '0300-3330011', '#3b82f6'),
        ('Jawad Butt', 'jawad.central@transworld.com', 'Member', 'Central', 'Database Technician', '0300-3330012', '#10b981')
    ]

    for m in members:
        cur.execute("""
            INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO UPDATE SET
                name = EXCLUDED.name,
                role = EXCLUDED.role,
                region = EXCLUDED.region,
                designation = EXCLUDED.designation,
                phone = EXCLUDED.phone;
        """, m)

    print("[3/3] Seeding Initial Field Tasks with Real Locations...")
    now = datetime.now()
    tasks = [
        # North Tasks
        (
            'TSK-NOR-0101', 'Route Survey for Feeder Fiber Expansion', 'Survey Task', 'North',
            'Eden Valley Block B', 31.436500, 73.155400, 'ali.north@transworld.com', 'boss@transworld.com',
            now + timedelta(days=2), 'High', 'Pending',
            'Conduct physical survey of street 3 to 7 for new 48-core feeder route. Mark pole positions and civil underground duct possibilities.',
            None, None, None, None, None
        ),
        (
            'TSK-NOR-0102', 'BOQ Estimation for 4 New FAT Boxes', 'BOQ Task', 'North',
            'Eden Valley Commercial', 31.435800, 73.154200, 'hamza.north@transworld.com', 'boss@transworld.com',
            now + timedelta(days=1), 'Critical', 'In Progress',
            'Prepare Bill of Quantity (BOQ) for 4 FAT-16 boxes, 1:8 splitters, 400m drop fiber cables, clamp sets, and suspension brackets.',
            'Initial site visit complete. Measuring drop cable distances now.', None, None, None, None
        ),
        (
            'TSK-NOR-0103', 'Database Audit & OLT Port Alignment', 'Database Task', 'North',
            'POP - Margalla View Plaza', 31.435200, 73.153800, 'asad.north@transworld.com', 'boss@transworld.com',
            now - timedelta(hours=3), 'Medium', 'Submitted for Review',
            'Cross check pgAdmin subscribers table with Huawei OLT-5 slot 1-4 port assignments. Ensure ONT MAC addresses match.',
            'Audit completed. 149 subscriber records aligned with OLT-5 slot 1/2. Report attached with CSV reconciliation.', 'audit_report_olt5.csv', None, now - timedelta(hours=1), None
        ),
        (
            'TSK-NOR-0104', 'FTTH Ring Redundancy Network Planning', 'Planning Task', 'North',
            'Sector G-11 North Grid', 31.437200, 73.156800, 'usman.north@transworld.com', 'boss@transworld.com',
            now - timedelta(days=1), 'High', 'Accepted',
            'Design backhaul protection ring connecting POP-ISB-01 with secondary sub-ring to avoid single point of fiber cuts.',
            'Detailed CAD / GIS diagram submitted. Ring capacity verified for 10Gbps uplink.', 'ring_planning_v2.pdf', 'Great work. Ring architecture approved for Q1 implementation.', now - timedelta(days=1, hours=3), now - timedelta(hours=5)
        ),

        # South Tasks
        (
            'TSK-SOU-0201', 'Civil Trenching Route Survey', 'Survey Task', 'South',
            'Eden Garden Executive Block', 31.422400, 73.149000, 'arham.south@transworld.com', 'boss@transworld.com',
            now + timedelta(days=3), 'Medium', 'Pending',
            'Inspect road crossing on Main Boulevard Executive Block for micro-trenching depth approval from housing authority.',
            None, None, None, None, None
        ),
        (
            'TSK-SOU-0202', 'BOQ Preparation for Executive Block Phase 2', 'BOQ Task', 'South',
            'Executive Block Phase 2', 31.421800, 73.148200, 'ehsan.south@transworld.com', 'boss@transworld.com',
            now + timedelta(days=2), 'High', 'In Progress',
            'Calculate required quantities of 24-core distribution cables, joint enclosures, and terminal accessories.',
            'Drafting quantities in Excel format based on survey drawings.', None, None, None, None
        ),

        # Central Tasks
        (
            'TSK-CEN-0301', 'High Optical Attenuation Investigation', 'Survey Task', 'Central',
            'Eden Garden Sector 2', 31.424600, 73.144500, 'adeel.central@transworld.com', 'boss@transworld.com',
            now + timedelta(hours=14), 'Critical', 'Pending',
            'Three customers reporting -28.4 dBm low optical power on ODB-5108201. Perform OTDR test from FAT-510820401 to locate macrobend.',
            None, None, None, None, None
        ),
        (
            'TSK-CEN-0302', 'GIS Parcel Spatial Layer Update', 'Database Task', 'Central',
            'Eden Garden Commercial Market', 31.425100, 73.145300, 'azam.central@transworld.com', 'boss@transworld.com',
            now - timedelta(hours=2), 'Medium', 'Submitted for Review',
            'Update 96 commercial parcel boundaries with newly assigned plot numbers from society administration.',
            'All 96 polygon coordinates updated and validated in PostGIS. Attached GeoJSON export.', 'eden_commercial_parcels.geojson', None, now - timedelta(minutes=45), None
        )
    ]

    for t in tasks:
        cur.execute("""
            INSERT INTO field_tasks (
                task_code, title, task_type, region, area_name, latitude, longitude,
                assigned_to, assigned_by, deadline, priority, status, description,
                submission_notes, report_filename, boss_feedback, submitted_at, reviewed_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (task_code) DO NOTHING;
        """, t)

    conn.commit()
    print("[SUCCESS] All team tables, 48 team members, and real field tasks seeded into PostgreSQL!")
    conn.close()

if __name__ == '__main__':
    setup_tasks_schema()
