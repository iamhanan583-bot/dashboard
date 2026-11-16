-- ============================================================================
-- TRANSWORLD GIS & NOC - SAFE SCHEMA (schema.sql)
-- Safe to run many times: it only CREATES what is missing. It never drops or
-- deletes anything. For a full wipe use reset_dev_data.sql (development only).
-- ============================================================================

-- ============================================================================
-- 1. NETWORK ZONES TABLE (Sectors / Regions)
-- ============================================================================
CREATE TABLE IF NOT EXISTS network_zones (
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
CREATE TABLE IF NOT EXISTS pop_stations (
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
CREATE TABLE IF NOT EXISTS fiber_cables (
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
CREATE TABLE IF NOT EXISTS odb_splitters (
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
CREATE TABLE IF NOT EXISTS fat_boxes (
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
CREATE TABLE IF NOT EXISTS subscribers (
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
CREATE TABLE IF NOT EXISTS live_telemetry (
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
CREATE INDEX IF NOT EXISTS idx_telemetry_ont_time ON live_telemetry (ont_id, recorded_at DESC);

-- ============================================================================
-- 8. COMMERCIAL PARCELS TABLE (TFS Coverage & Plots)
-- ============================================================================
CREATE TABLE IF NOT EXISTS commercial_parcels (
    parcel_id SERIAL PRIMARY KEY,
    plot_no VARCHAR(50) NOT NULL,
    society_name VARCHAR(100) NOT NULL,
    zone_name VARCHAR(50) NOT NULL,
    coverage_status VARCHAR(50) DEFAULT 'Covered',
    gpon_status VARCHAR(50) DEFAULT 'Active GPON Ready',
    coordinates_json JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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
-- LOGIN: password hashes (bcrypt). Set them with scratch/set_all_passwords.py
-- ============================================================================
ALTER TABLE team_members ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);

-- ============================================================================
-- TASK CODES: sequence used by server.py (never repeats, even after deletes)
-- ============================================================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relkind = 'S' AND relname = 'task_code_seq') THEN
        EXECUTE format(
            'CREATE SEQUENCE task_code_seq START WITH %s',
            GREATEST(150, COALESCE((SELECT MAX(task_id) FROM field_tasks), 100) + 1)
        );
    END IF;
END $$;
