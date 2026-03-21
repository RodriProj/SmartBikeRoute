import json
import psycopg2
from psycopg2.extras import RealDictCursor
from app.core.config import DB


def get_conn():
    return psycopg2.connect(**DB)


def calculate_route(startLat: float, startLon: float, endLat: float, endLon: float):
    q = """
    WITH
    start_v AS (
      SELECT id
      FROM ways_vertices_pgr
      ORDER BY the_geom <-> ST_SetSRID(ST_Point(%s, %s), 4326)
      LIMIT 1
    ),
    end_v AS (
      SELECT id
      FROM ways_vertices_pgr
      ORDER BY the_geom <-> ST_SetSRID(ST_Point(%s, %s), 4326)
      LIMIT 1
    ),
    route AS (
      SELECT * FROM pgr_dijkstra(
        'SELECT gid AS id, source, target, cost, reverse_cost FROM ways',
        (SELECT id FROM start_v),
        (SELECT id FROM end_v),
        directed := false
      )
    ),
    edges AS (
      SELECT w.the_geom
      FROM route r
      JOIN ways w ON r.edge = w.gid
      WHERE r.edge <> -1
    )
    SELECT
      ST_AsGeoJSON(ST_LineMerge(ST_Union(the_geom))) AS geojson,
      ST_Length(ST_Transform(ST_LineMerge(ST_Union(the_geom)), 3857)) AS length_m
    FROM edges;
    """

    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(q, (startLon, startLat, endLon, endLat))
            row = cur.fetchone()

    if not row or row["geojson"] is None:
        return {
            "type": "FeatureCollection",
            "features": [],
            "summary": {
                "distance_m": 0
            }
        }

    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": json.loads(row["geojson"])
            }
        ],
        "summary": {
            "distance_m": round(row["length_m"], 2)
        }
    }


def generate_personalized_route(request, profile_weights):
    route_geojson = calculate_route(
        startLat=request.startLat,
        startLon=request.startLon,
        endLat=request.endLat,
        endLon=request.endLon
    )

    estimated_time_min = None
    distance_m = route_geojson.get("summary", {}).get("distance_m", 0)

    if distance_m > 0:
        speed_kmh_by_profile = {
            "lazer": 12,
            "exercicio": 20,
            "competicao": 28
        }

        speed_kmh = speed_kmh_by_profile.get(request.profile_type, 15)
        estimated_time_min = round((distance_m / 1000) / speed_kmh * 60)

    return {
        "profile_type": request.profile_type,
        "preferences": {
            "target_distance_km": request.target_distance_km,
            "elevation_preference": request.elevation_preference,
            "scenic_preference": request.scenic_preference,
            "traffic_avoidance": request.traffic_avoidance,
            "loop": request.loop,
            "training_goal": request.training_goal
        },
        "applied_weights": profile_weights,
        "route_summary": {
            "distance_m": distance_m,
            "estimated_time_min": estimated_time_min
        },
        "route": route_geojson
    }