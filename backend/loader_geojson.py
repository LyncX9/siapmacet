import json
from sqlalchemy import text
from db import SessionLocal

with open("../data/roads.geojson", encoding="utf-8") as f:
    geo = json.load(f)

db = SessionLocal()

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
            ON CONFLICT (road_id) DO NOTHING
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
