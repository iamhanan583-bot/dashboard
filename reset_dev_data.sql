-- ############################################################################
-- #  WARNING - DEVELOPMENT ONLY - THIS FILE DELETES DATA                      #
-- #  It DROPS subscribers, live_telemetry, fat_boxes, odb_splitters, zones,   #
-- #  pop_stations, fiber_cables and commercial_parcels, then reloads sample   #
-- #  data. Do NOT run it on a database you want to keep.                      #
-- #  For normal setup use schema.sql (safe) + setup_tasks_db.py (seed tasks). #
-- ############################################################################

-- ============================================================================
-- TRANSWORLD TELECOM & NOC GIS - POSTGRESQL / PGADMIN 4 DATABASE SCHEMA
-- Database Name: transworld_gis
-- Author: Transworld GIS Core Network Engineering
-- ============================================================================

-- STEP 1: DROP OLD TABLES IF EXISTS (CLEAN SLATE)
DROP TABLE IF EXISTS live_telemetry CASCADE;
DROP TABLE IF EXISTS subscribers CASCADE;
DROP TABLE IF EXISTS commercial_parcels CASCADE;
DROP TABLE IF EXISTS fat_boxes CASCADE;
DROP TABLE IF EXISTS odb_splitters CASCADE;
DROP TABLE IF EXISTS fiber_cables CASCADE;
DROP TABLE IF EXISTS pop_stations CASCADE;
DROP TABLE IF EXISTS network_zones CASCADE;

-- ============================================================================
-- 1. NETWORK ZONES TABLE (Sectors / Regions)
-- ============================================================================
CREATE TABLE network_zones (
    zone_id SERIAL PRIMARY KEY,
    zone_name VARCHAR(100) NOT NULL,
    zone_code VARCHAR(20) UNIQUE NOT NULL,
    city VARCHAR(50) DEFAULT 'Islamabad',
    center_lat NUMERIC(10, 6) NOT NULL,
    center_lng NUMERIC(10, 6) NOT NULL,
    boundary_polygon JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 2. POP STATIONS TABLE (Point of Presence / Aggregation Nodes)
-- ============================================================================
CREATE TABLE pop_stations (
    pop_id SERIAL PRIMARY KEY,
    pop_code VARCHAR(50) UNIQUE NOT NULL,
    pop_name VARCHAR(150) NOT NULL,
    zone_id INT REFERENCES network_zones(zone_id),
    latitude NUMERIC(10, 6) NOT NULL,
    longitude NUMERIC(10, 6) NOT NULL,
    olt_capacity INT DEFAULT 8,
    active_olts INT DEFAULT 3,
    status VARCHAR(20) DEFAULT 'Active'
);

-- ============================================================================
-- 3. FIBER CABLES TABLE (Feeder, Distribution, Backhaul)
-- ============================================================================
CREATE TABLE fiber_cables (
    cable_id SERIAL PRIMARY KEY,
    cable_code VARCHAR(50) UNIQUE NOT NULL,
    cable_type VARCHAR(30) NOT NULL CHECK (cable_type IN ('Backhaul', 'Feeder', 'Distribution')),
    core_count INT NOT NULL DEFAULT 48,
    color_hex VARCHAR(10) DEFAULT '#ff2d2d',
    route_points JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'Operational',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 4. ODB / DC SPLITTERS TABLE (Optical Distribution Boxes)
-- ============================================================================
CREATE TABLE odb_splitters (
    odb_id VARCHAR(50) PRIMARY KEY,
    zone_id INT REFERENCES network_zones(zone_id),
    latitude NUMERIC(10, 6) NOT NULL,
    longitude NUMERIC(10, 6) NOT NULL,
    split_ratio VARCHAR(20) DEFAULT '1:8',
    total_ports INT DEFAULT 8,
    used_ports INT DEFAULT 6
);

-- ============================================================================
-- 5. FAT BOXES TABLE (Fiber Access Terminals)
-- ============================================================================
CREATE TABLE fat_boxes (
    fat_id VARCHAR(50) PRIMARY KEY,
    odb_id VARCHAR(50) REFERENCES odb_splitters(odb_id),
    latitude NUMERIC(10, 6) NOT NULL,
    longitude NUMERIC(10, 6) NOT NULL,
    capacity INT DEFAULT 16,
    active_customers INT DEFAULT 12,
    city VARCHAR(50) DEFAULT 'Islamabad'
);

-- ============================================================================
-- 6. SUBSCRIBERS TABLE (Customer ONTs & Network Topology)
-- ============================================================================
CREATE TABLE subscribers (
    ont_id VARCHAR(50) PRIMARY KEY,
    subscriber_name VARCHAR(150) NOT NULL,
    phone_number VARCHAR(30),
    service_address TEXT NOT NULL,
    building_name VARCHAR(100) DEFAULT 'Margala View Plaza',
    plot_no VARCHAR(20),
    street_no VARCHAR(20),
    block_name VARCHAR(20),
    area_name VARCHAR(100) NOT NULL,
    sub_area VARCHAR(100),
    city VARCHAR(50) DEFAULT 'Islamabad',
    latitude NUMERIC(10, 6) NOT NULL,
    longitude NUMERIC(10, 6) NOT NULL,
    fat_id VARCHAR(50) REFERENCES fat_boxes(fat_id),
    odb_id VARCHAR(50) REFERENCES odb_splitters(odb_id),
    olt_name VARCHAR(50) DEFAULT 'ISB-F11-OLT-5-1',
    frame_no INT DEFAULT 0,
    slot_no INT DEFAULT 5,
    port_no INT DEFAULT 1,
    ip_address VARCHAR(45) DEFAULT '10.142.20.105',
    mac_address VARCHAR(30) DEFAULT '48:D3:43:8A:2B:11',
    bandwidth_plan VARCHAR(30) NOT NULL DEFAULT '40MB',
    bandwidth_mbps INT NOT NULL DEFAULT 40,
    connection_status VARCHAR(30) NOT NULL DEFAULT 'Online' CHECK (connection_status IN ('Online', 'Powered Off', 'Link Down', 'GEM Packet Loss', 'Low Optical Power')),
    is_up BOOLEAN DEFAULT TRUE,
    last_down_cause VARCHAR(100) DEFAULT 'Power Off',
    current_alarm VARCHAR(100) DEFAULT 'Online',
    rx_ont_dbm NUMERIC(5, 2) DEFAULT -21.56,
    rx_olt_dbm NUMERIC(5, 2) DEFAULT -23.18,
    last_up_time TIMESTAMP DEFAULT '2026-09-28 23:34:27',
    last_down_time TIMESTAMP DEFAULT '2026-09-28 23:29:00',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 7. LIVE TELEMETRY TABLE (Real-Time Internet Speed Monitoring Engine)
-- ============================================================================
CREATE TABLE live_telemetry (
    telemetry_id BIGSERIAL PRIMARY KEY,
    ont_id VARCHAR(50) NOT NULL REFERENCES subscribers(ont_id) ON DELETE CASCADE,
    live_download_mbps NUMERIC(7, 2) NOT NULL,
    live_upload_mbps NUMERIC(7, 2) NOT NULL,
    bandwidth_utilization_pct INT NOT NULL,
    latency_ms NUMERIC(5, 2) DEFAULT 11.4,
    jitter_ms NUMERIC(4, 2) DEFAULT 0.8,
    packet_loss_pct NUMERIC(4, 2) DEFAULT 0.0,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast live telemetry querying
CREATE INDEX idx_telemetry_ont_time ON live_telemetry (ont_id, recorded_at DESC);

-- ============================================================================
-- 8. COMMERCIAL PARCELS TABLE (TFS Coverage & Plots)
-- ============================================================================
CREATE TABLE commercial_parcels (
    parcel_id SERIAL PRIMARY KEY,
    plot_no VARCHAR(50) NOT NULL,
    society_name VARCHAR(100) NOT NULL,
    zone_name VARCHAR(50) NOT NULL,
    coverage_status VARCHAR(50) DEFAULT 'Covered',
    gpon_status VARCHAR(50) DEFAULT 'Active GPON Ready',
    coordinates_json JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- POPULATE SEED DATA (EXACT TRANSWORLD GIS SIMULATION DATA)
-- ============================================================================

-- 1. Insert Network Zones
INSERT INTO network_zones (zone_name, zone_code, city, center_lat, center_lng) VALUES
('North Sector (Eden Valley & Margalla View)', 'ZONE_NORTH', 'Islamabad', 31.435700, 73.154900),
('Central Sector (Eden Garden)', 'ZONE_CENTRAL', 'Faisalabad', 31.424600, 73.144500),
('South Sector (Eden Executive Block)', 'ZONE_SOUTH', 'Faisalabad', 31.422400, 73.149000);

-- 2. Insert POP Station
INSERT INTO pop_stations (pop_code, pop_name, zone_id, latitude, longitude) VALUES
('POP-ISB-01', 'POP - Margalla View Plaza Central', 1, 31.435200, 73.153800),
('POP-FSD-02', 'POP - Eden Garden Hub', 2, 31.424100, 73.143900);

-- 3. Insert ODB Splitters
INSERT INTO odb_splitters (odb_id, zone_id, latitude, longitude) VALUES
('5108101', 1, 31.435800, 73.154500),
('5108102', 1, 31.436200, 73.155200),
('5108201', 2, 31.424800, 73.144800);

-- 4. Insert FAT Boxes
INSERT INTO fat_boxes (fat_id, odb_id, latitude, longitude) VALUES
('510810403', '5108101', 31.436050, 73.154820),
('510810404', '5108101', 31.435910, 73.154310),
('510820401', '5108201', 31.424930, 73.145100);

-- 5. Insert Real-World Subscribers
INSERT INTO subscribers (
    ont_id, subscriber_name, phone_number, service_address, building_name, plot_no, street_no, 
    block_name, area_name, sub_area, city, latitude, longitude, fat_id, odb_id, olt_name, 
    bandwidth_plan, bandwidth_mbps, connection_status, is_up, rx_ont_dbm, rx_olt_dbm
) VALUES
('510311144', 'Mr. Waseem Shahid', '0300-1234567', 'Office No: 13, Floor No: 0, Margala View Plaza, Commercial Area-Margala View Plaza', 'Margala View Plaza', '13', '3', 'Block A', 'Eden Valley & Margalla View', 'Commercial G-11', 'Islamabad', 31.436120, 73.154850, '510810403', '5108101', 'ISB-F11-OLT-5-1', '40MB', 40, 'Online', TRUE, -21.56, -23.18),
('510311145', 'Mr. Ahmed Khan', '0321-7654321', 'House No: 24, St 1, Block A, Eden Valley', 'Eden Valley Villas', '24', '1', 'Block A', 'Eden Valley & Margalla View', 'Sector 1', 'Islamabad', 31.436250, 73.155100, '510810403', '5108101', 'ISB-F11-OLT-5-1', '60MB', 60, 'Online', TRUE, -20.80, -22.40),
('510311146', 'Mr. Usman Malik', '0333-9876543', 'Plot 55, Street 4, Block B, Eden Garden', 'Eden Heights', '55', '4', 'Block B', 'Eden Garden', 'Sector 2', 'Faisalabad', 31.424750, 73.144600, '510820401', '5108201', 'FSD-E2-OLT-1-1', '20MB', 20, 'Low Optical Power', TRUE, -28.40, -29.10),
('510311147', 'Mr. Bilal Rana', '0345-1122334', 'Shop 7, Main Commercial Market, Eden Garden', 'Rana Center', '7', 'Main', 'Block C', 'Eden Garden', 'Commercial', 'Faisalabad', 31.424450, 73.144100, '510820401', '5108201', 'FSD-E2-OLT-1-1', '10MB', 10, 'Link Down', FALSE, -34.00, -35.20),
('510311148', 'Mr. Hamza Chaudhry', '0312-5544332', 'House 88, Street 2, Executive Block', 'Executive Enclave', '88', '2', 'Block E', 'Eden Garden Executive Block', 'Sector 3', 'Faisalabad', 31.422300, 73.149200, '510820401', '5108201', 'FSD-E3-OLT-2-1', '40MB', 40, 'Online', TRUE, -19.90, -21.30);

-- 6. Insert Live Telemetry Readings
INSERT INTO live_telemetry (ont_id, live_download_mbps, live_upload_mbps, bandwidth_utilization_pct, latency_ms) VALUES
('510311144', 36.40, 8.20, 91, 11.2),
('510311145', 54.80, 14.10, 91, 9.8),
('510311146', 12.10, 3.40, 60, 22.4),
('510311147', 0.00, 0.00, 0, 999.0),
('510311148', 31.60, 7.50, 79, 12.0);

-- ============================================================================
-- USEFUL QUERIES & VIEWS (For Dashboard & Reports)
-- ============================================================================

-- View: Active Customer Live Speeds & Status
CREATE OR REPLACE VIEW view_active_customer_telemetry AS
SELECT 
    s.ont_id,
    s.subscriber_name,
    s.service_address,
    s.city,
    s.area_name,
    s.olt_name,
    s.bandwidth_plan,
    s.bandwidth_mbps,
    s.connection_status,
    s.rx_ont_dbm,
    COALESCE(t.live_download_mbps, 0.0) AS current_download_mbps,
    COALESCE(t.live_upload_mbps, 0.0) AS current_upload_mbps,
    COALESCE(t.bandwidth_utilization_pct, 0) AS load_pct,
    COALESCE(t.latency_ms, 0.0) AS ping_latency_ms
FROM subscribers s
LEFT JOIN LATERAL (
    SELECT live_download_mbps, live_upload_mbps, bandwidth_utilization_pct, latency_ms
    FROM live_telemetry lt
    WHERE lt.ont_id = s.ont_id
    ORDER BY recorded_at DESC
    LIMIT 1
) t ON true;

-- View: Network NOC Health Summary
CREATE OR REPLACE VIEW view_noc_alarm_summary AS
SELECT 
    COUNT(*) FILTER (WHERE connection_status = 'Online') AS total_online,
    COUNT(*) FILTER (WHERE connection_status = 'Link Down') AS total_los,
    COUNT(*) FILTER (WHERE connection_status = 'Powered Off') AS total_power_off,
    COUNT(*) FILTER (WHERE connection_status = 'GEM Packet Loss') AS total_gem_loss,
    COUNT(*) FILTER (WHERE connection_status = 'Low Optical Power') AS total_low_optical,
    ROUND(AVG(rx_ont_dbm), 2) AS avg_optical_power_dbm
FROM subscribers;

-- ============================================================================
-- STORED PROCEDURE: RECORD LIVE CUSTOMER SPEED
-- Call this procedure from Python/Node backend to simulate or store live speed:
-- CALL record_speed_telemetry('510311144', 38.5, 9.1, 96, 10.5);
-- ============================================================================
CREATE OR REPLACE PROCEDURE record_speed_telemetry(
    p_ont_id VARCHAR,
    p_dl NUMERIC,
    p_ul NUMERIC,
    p_pct INT,
    p_lat NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO live_telemetry (ont_id, live_download_mbps, live_upload_mbps, bandwidth_utilization_pct, latency_ms)
    VALUES (p_ont_id, p_dl, p_ul, p_pct, p_lat);
END;
$$;


-- ============================================================================
-- 9. TEAM MEMBERS TABLE (Boss + Region-Wise Engineering Teams)
-- ============================================================================
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

-- ============================================================================
-- 10. FIELD TASKS TABLE (Role-Based Task Management & Field Dispatch)
-- ============================================================================
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

-- ============================================================================
-- 11. SEED DATA: 48 TEAM MEMBERS (North 25, Central 12, South 10, Boss)
-- ============================================================================
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Engr. Tariq Mehmood (Boss)', 'boss@transworld.com', 'Boss', 'All', 'Chief Operations Officer / Head of GIS & Planning', '0300-8889900', '#f59e0b') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Muhammad Ali', 'ali.north@transworld.com', 'Member', 'North', 'Senior GIS Surveyor', '0300-1110001', '#3b82f6') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Usman Khan', 'usman.north@transworld.com', 'Member', 'North', 'Network Planning Engineer', '0300-1110002', '#10b981') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Hamza Tariq', 'hamza.north@transworld.com', 'Member', 'North', 'BOQ Estimator Lead', '0300-1110003', '#8b5cf6') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Bilal Ahmed', 'bilal.north@transworld.com', 'Member', 'North', 'FTTH Field Technician', '0300-1110004', '#ec4899') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Asadullah', 'asad.north@transworld.com', 'Member', 'North', 'Database Specialist', '0300-1110005', '#06b6d4') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Zain ul Abideen', 'zain.north@transworld.com', 'Member', 'North', 'Optical Power Technician', '0300-1110006', '#f97316') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Faisal Raza', 'faisal.north@transworld.com', 'Member', 'North', 'Route Surveyor', '0300-1110007', '#14b8a6') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Kashif Nawaz', 'kashif.north@transworld.com', 'Member', 'North', 'OLT Integration Specialist', '0300-1110008', '#6366f1') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Naveed Akhtar', 'naveed.north@transworld.com', 'Member', 'North', 'Civil & Trench Lead', '0300-1110009', '#eab308') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Sana Sheikh', 'sana.north@transworld.com', 'Member', 'North', 'GIS Analyst', '0300-1110010', '#a855f7') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Ayesha Malik', 'ayesha.north@transworld.com', 'Member', 'North', 'Planning Engineer', '0300-1110011', '#ec4899') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Waleed Butt', 'waleed.north@transworld.com', 'Member', 'North', 'Field QA/QC Officer', '0300-1110012', '#3b82f6') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Imran Shahid', 'imran.north@transworld.com', 'Member', 'North', 'Fiber Splicing Lead', '0300-1110013', '#10b981') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Shahid Iqbal', 'shahid.north@transworld.com', 'Member', 'North', 'Survey Assistant', '0300-1110014', '#f59e0b') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Hassan Raza', 'hassan.north@transworld.com', 'Member', 'North', 'BOQ Assistant', '0300-1110015', '#06b6d4') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Omer Farooq', 'omer.north@transworld.com', 'Member', 'North', 'Fiber Line Technician', '0300-1110016', '#84cc16') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Danish Ali', 'danish.north@transworld.com', 'Member', 'North', 'ODB / FAT Technician', '0300-1110017', '#6366f1') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Fahad Mustafa', 'fahad.north@transworld.com', 'Member', 'North', 'GIS Drafter & Cartographer', '0300-1110018', '#14b8a6') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Haris Mehmood', 'haris.north@transworld.com', 'Member', 'North', 'Field Inspector', '0300-1110019', '#e11d48') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Rehan Ahmed', 'rehan.north@transworld.com', 'Member', 'North', 'Field Survey Specialist', '0300-1110020', '#3b82f6') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Saad Gill', 'saad.north@transworld.com', 'Member', 'North', 'Network Maintenance Tech', '0300-1110021', '#10b981') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Zubair Ansari', 'zubair.north@transworld.com', 'Member', 'North', 'Planning Technician', '0300-1110022', '#a855f7') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Kamran Mirza', 'kamran.north@transworld.com', 'Member', 'North', 'Field Supervisor', '0300-1110023', '#f59e0b') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Farhan Bhatti', 'farhan.north@transworld.com', 'Member', 'North', 'BOQ Surveyor', '0300-1110024', '#06b6d4') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Salman Javed', 'salman.north@transworld.com', 'Member', 'North', 'Spatial Database Administrator', '0300-1110025', '#8b5cf6') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Tariq Jameel', 'tariq.south@transworld.com', 'Member', 'South', 'South Regional Lead', '0300-2220001', '#f59e0b') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Arham Butt', 'arham.south@transworld.com', 'Member', 'South', 'Field Surveyor', '0300-2220002', '#3b82f6') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Babar Azam', 'babar.south@transworld.com', 'Member', 'South', 'GIS Specialist', '0300-2220003', '#10b981') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Dawood Khan', 'dawood.south@transworld.com', 'Member', 'South', 'Network Planner', '0300-2220004', '#06b6d4') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Ehsan Ullah', 'ehsan.south@transworld.com', 'Member', 'South', 'BOQ Estimator Lead', '0300-2220005', '#8b5cf6') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Ghalib Hussain', 'ghalib.south@transworld.com', 'Member', 'South', 'Fiber Technician', '0300-2220006', '#ec4899') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Habib Ur Rehman', 'habib.south@transworld.com', 'Member', 'South', 'Splicing Technician', '0300-2220007', '#14b8a6') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Irfan Ali', 'irfan.south@transworld.com', 'Member', 'South', 'Field Tech', '0300-2220008', '#6366f1') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Junaid Jamshed', 'junaid.south@transworld.com', 'Member', 'South', 'Survey Engineer', '0300-2220009', '#eab308') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Khalid Mehmood', 'khalid.south@transworld.com', 'Member', 'South', 'Database Technician', '0300-2220010', '#a855f7') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Mohammad Rizwan', 'rizwan.central@transworld.com', 'Member', 'Central', 'Central Regional Supervisor', '0300-3330001', '#f59e0b') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Adeel Qureshi', 'adeel.central@transworld.com', 'Member', 'Central', 'Field Route Surveyor', '0300-3330002', '#3b82f6') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Adnan Siddiqui', 'adnan.central@transworld.com', 'Member', 'Central', 'BOQ Quantity Analyst', '0300-3330003', '#10b981') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Azam Khan', 'azam.central@transworld.com', 'Member', 'Central', 'GIS Senior Engineer', '0300-3330004', '#06b6d4') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Abdul Basit', 'basit.central@transworld.com', 'Member', 'Central', 'Network Route Planner', '0300-3330005', '#8b5cf6') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Danyal Ahmed', 'danyal.central@transworld.com', 'Member', 'Central', 'Field Operations Tech', '0300-3330006', '#ec4899') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Ejaz Ahmed', 'ejaz.central@transworld.com', 'Member', 'Central', 'OLT Integration Specialist', '0300-3330007', '#14b8a6') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Faizan Sheikh', 'faizan.central@transworld.com', 'Member', 'Central', 'Survey Assistant', '0300-3330008', '#6366f1') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Ghufran Ali', 'ghufran.central@transworld.com', 'Member', 'Central', 'Fiber Splicing Lead', '0300-3330009', '#eab308') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Haider Ali', 'haider.central@transworld.com', 'Member', 'Central', 'Planning Assistant', '0300-3330010', '#a855f7') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Idrees Khan', 'idrees.central@transworld.com', 'Member', 'Central', 'Field Inspector', '0300-3330011', '#3b82f6') ON CONFLICT (email) DO NOTHING;
INSERT INTO team_members (name, email, role, region, designation, phone, avatar_color) VALUES ('Jawad Butt', 'jawad.central@transworld.com', 'Member', 'Central', 'Database Technician', '0300-3330012', '#10b981') ON CONFLICT (email) DO NOTHING;

-- ============================================================================
-- 12. SEED DATA: INITIAL FIELD DISPATCH TASKS
-- ============================================================================
