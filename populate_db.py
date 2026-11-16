import sys
from pathlib import Path
_root = Path(__file__).resolve().parent if Path(__file__).resolve().parent.name != 'scratch' else Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))
from db_config import DB_CONFIG
"""
Populate complete Transworld FTTH topology into PostgreSQL (pgAdmin 4)
Database: transworlddatabase
"""

import math
import psycopg2

AR = [
    {'n': 'North', 'nm': 'Eden Valley & Margalla View', 'lat': 31.4357, 'lng': 73.1549, 'c': '#3f51b5'},
    {'n': 'Central', 'nm': 'Eden Garden', 'lat': 31.4246, 'lng': 73.1445, 'c': '#43a047'},
    {'n': 'South', 'nm': 'Eden Garden Executive Block', 'lat': 31.4224, 'lng': 73.1490, 'c': '#fdd835'}
]

TH = -20
S = 19
def rnd():
    global S
    S = (S * 16807) % 2147483647
    return (S - 1) / 2147483646

def pt(a, u, v):
    t = TH * math.pi / 180
    x = u - 192
    y = v - 99
    lat = a['lat'] + (x * math.sin(t) + y * math.cos(t)) / 111320
    lng = a['lng'] + (x * math.cos(t) - y * math.sin(t)) / (111320 * math.cos(a['lat'] * math.pi / 180))
    return round(lat, 6), round(lng, 6)

FN = 'Waseem,Ahmed,Ali,Usman,Bilal,Hamza,Waleed,Imran,Asad,Zain,Faisal,Kashif,Naveed,Sana,Ayesha,Tariq'.split(',')
LN = 'Shahid,Khan,Butt,Malik,Rana,Chaudhry,Iqbal,Ansari,Sheikh,Raza,Mirza,Gill,Bhatti'.split(',')
PLANS = [10, 20, 40, 60]

def pick(lst):
    return lst[math.floor(rnd() * len(lst))]

def pad(n):
    return f"{n:02d}"

def populate():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    print("Connected to PostgreSQL successfully.")

    ont_id_base = 510311200
    subscribers_to_insert = []
    telemetry_to_insert = []

    for ai, a in enumerate(AR):
        sy = [54, 120, 186]
        for j in range(3):
            y = sy[j]
            for m in range(2):
                uo = 96 + 192 * m
                oid = f"5108{ai + 1}{pad(j)}{m}"
                olat, olng = pt(a, uo, y)
                cur.execute("""
                    INSERT INTO odb_splitters (odb_id, zone_id, latitude, longitude)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (odb_id) DO NOTHING;
                """, (oid, ai + 1, olat, olng))

                for q in range(2):
                    i = 2 * m + q
                    u0 = 4 + 96 * i
                    v0 = j * 66 + 6
                    fplat, fplng = pt(a, u0 + 44, y - 12)
                    fid = f"5108{ai + 1}{pad(j)}{pad(i)}3"

                    cur.execute("""
                        INSERT INTO fat_boxes (fat_id, odb_id, latitude, longitude)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (fat_id) DO NOTHING;
                    """, (fid, oid, fplat, fplng))

                    for k in range(4):
                        r = rnd()
                        s = 'Online' if r < 0.88 else ('Powered Off' if r < 0.92 else ('Link Down' if r < 0.95 else ('GEM Packet Loss' if r < 0.97 else 'Low Optical Power')))
                        pplat, pplng = pt(a, u0 + k * 18 + 4, v0 + 10 + (k % 2) * 8)
                        up = (s in ['Online', 'GEM Packet Loss', 'Low Optical Power'])
                        blk = chr(65 + ai * 2 + (i >> 1))
                        pl = 1 + math.floor(rnd() * 60)
                        plan = pick(PLANS)
                        ont_id_base += 1
                        ont_str = str(ont_id_base)

                        sub_name = f"Mr. {pick(FN)} {pick(LN)}"
                        addr = f"Office No: {pl}, Building Name: Margala View Plaza, Plot No: {pl}, Street No: {1 + j}, Block {blk}, {a['nm']}"
                        olt = f"ISB-F11-OLT-5-{j+1}"
                        rx_ont = -28.40 if s == 'Low Optical Power' else round(-(19 + rnd() * 5.5), 2)
                        rx_olt = round(-(21 + rnd() * 4), 2)

                        subscribers_to_insert.append((
                            ont_str, sub_name, f"0300-{1000000 + k*333}", addr, 'Margala View Plaza',
                            str(pl), str(1 + j), f"Block {blk}", a['nm'], f"Block {blk} Commercial",
                            'Islamabad', pplat, pplng, fid, oid, olt,
                            0, math.floor(rnd() * 8), math.floor(rnd() * 16),
                            f"10.142.{ai + 10}.{20 + (ont_id_base % 200)}",
                            f"48:D3:43:8A:2B:{pad(k)}",
                            f"{plan}MB", plan, s, up,
                            'Power Off' if s == 'Powered Off' else ('LOS' if s == 'Link Down' else 'None'),
                            'Online' if s == 'Online' else s,
                            rx_ont, rx_olt
                        ))

                        live_dl = round(plan * (0.35 + rnd() * 0.55), 1) if up else 0.0
                        live_ul = round(plan * 0.25 * (0.3 + rnd() * 0.5), 1) if up else 0.0
                        load_pct = min(100, round((live_dl / plan) * 100)) if up else 0

                        telemetry_to_insert.append((
                            ont_str, live_dl, live_ul, load_pct, round(9 + rnd() * 8, 1)
                        ))

    # Bulk insert subscribers
    for sub in subscribers_to_insert:
        cur.execute("""
            INSERT INTO subscribers (
                ont_id, subscriber_name, phone_number, service_address, building_name,
                plot_no, street_no, block_name, area_name, sub_area,
                city, latitude, longitude, fat_id, odb_id, olt_name,
                frame_no, slot_no, port_no, ip_address, mac_address,
                bandwidth_plan, bandwidth_mbps, connection_status, is_up,
                last_down_cause, current_alarm, rx_ont_dbm, rx_olt_dbm
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (ont_id) DO NOTHING;
        """, sub)

    # Bulk insert initial live telemetry
    for tel in telemetry_to_insert:
        cur.execute("""
            INSERT INTO live_telemetry (ont_id, live_download_mbps, live_upload_mbps, bandwidth_utilization_pct, latency_ms)
            VALUES (%s, %s, %s, %s, %s);
        """, tel)

    conn.commit()
    print(f"Successfully inserted {len(subscribers_to_insert)} subscribers and telemetry into pgAdmin 4 database!")
    conn.close()

if __name__ == '__main__':
    populate()
