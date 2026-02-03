import json
from sqlalchemy import text
from db import SessionLocal, engine
from models import Base

# 1. Enable PostGIS & Create Tables (Init DB)
print("Creating tables...")
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    conn.commit()

Base.metadata.create_all(bind=engine)

# 2. Load Data
print("Loading GeoJSON...")
try:
    with open("../data/roads.geojson", encoding="utf-8") as f:
        geo = json.load(f)
except FileNotFoundError:
    print("Error: ../data/roads.geojson not found!")
    exit(1)

db = SessionLocal()

print(f"Importing {len(geo['features'])} roads...")
for f in geo["features"]:
    p = f["properties"]
    g = json.dumps(f["geometry"])

    db.execute(
        text("""
            INSERT INTO roads
            (road_id, road_name, city, road_weight, geom)
            VALUES
            (:road_id, :road_name, :city, :road_weight,
             ST_SetSRID(ST_GeomFromGeoJSON(:geom),4326))
            ON CONFLICT (road_id) DO UPDATE SET
            road_name = EXCLUDED.road_name,
            geom = EXCLUDED.geom
        """),
        {
            "road_id": p["road_id"],
            "road_name": p["road_name"],
            "city": p["city"],
            "road_weight": p["road_weight"],
            "geom": g
        }
    )

db.commit()
db.close()
print("Success! Database initialized and data imported.")
