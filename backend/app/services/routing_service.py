import json
from typing import Any, Dict

import psycopg2
from psycopg2.extras import RealDictCursor

from app.core.config import DB
from app.services.edge_cost_service import build_cost_query
from app.services.scoring_service import (
    calculate_distance_difference,
    calculate_estimated_time,
)


def get_conn():
    return psycopg2.connect(**DB)


def _build_empty_route_result(routing_strategy_used: str) -> Dict[str, Any]:
    return {
        "type": "FeatureCollection",
        "features": [],
        "summary": {
            "distance_m": 0.0,
            "distance_km": 0.0,
            "routing_strategy_used": routing_strategy_used,
        },
    }


def _build_preferences_snapshot(request) -> Dict[str, Any]:
    return {
        "target_distance_km": request.target_distance_km,
        "loop": request.loop,
        "elevation_preference": request.elevation_preference,
        "scenic_preference": request.scenic_preference,
        "traffic_avoidance": request.traffic_avoidance,
        "difficulty_level": request.difficulty_level,
        "points_of_interest_preference": request.points_of_interest_preference,
        "environment_preference": request.environment_preference,
        "surface_preference": request.surface_preference,
        "green_area_preference": request.green_area_preference,
        "intensity_preference": request.intensity_preference,
        "route_fluency": request.route_fluency,
        "training_goal": request.training_goal,
    }


def calculate_route(
    startLat: float,
    startLon: float,
    endLat: float,
    endLon: float,
    profile_type: str,
    session_profile: dict,
) -> Dict[str, Any]:
    """
    Calcula uma rota entre dois pontos usando um modelo de custo adaptado
    ao perfil principal e às preferências da sessão.
    """
    cost_query, routing_strategy_used = build_cost_query(
        profile_type=profile_type,
        session_profile=session_profile,
    )

    sql = """
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
        SELECT *
        FROM pgr_dijkstra(
            %s,
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
            cur.execute(sql, (startLon, startLat, endLon, endLat, cost_query))
            row = cur.fetchone()

    if not row or row["geojson"] is None:
        return _build_empty_route_result(routing_strategy_used)

    length_m_raw = row.get("length_m") or 0
    distance_m = round(float(length_m_raw), 2)
    distance_km = round(distance_m / 1000, 2)

    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": json.loads(row["geojson"]),
            }
        ],
        "summary": {
            "distance_m": distance_m,
            "distance_km": distance_km,
            "routing_strategy_used": routing_strategy_used,
        },
    }


def generate_personalized_route(request, session_profile: dict) -> Dict[str, Any]:
    """
    Gera uma rota personalizada com base no perfil selecionado e no perfil
    final da sessão já ajustado pelas preferências avançadas.
    """
    route_geojson = calculate_route(
        startLat=request.startLat,
        startLon=request.startLon,
        endLat=request.endLat,
        endLon=request.endLon,
        profile_type=request.profile_type,
        session_profile=session_profile,
    )

    route_summary = route_geojson.get("summary", {})
    distance_m = route_summary.get("distance_m", 0.0)
    distance_km = route_summary.get("distance_km", 0.0)
    routing_strategy_used = route_summary.get("routing_strategy_used")

    estimated_time_min = calculate_estimated_time(
        distance_km=distance_km,
        profile_type=request.profile_type,
    )

    distance_difference_km = calculate_distance_difference(
        actual_distance_km=distance_km,
        target_distance_km=request.target_distance_km,
    )

    return {
        "profile_type": request.profile_type,
        "session_profile": session_profile,
        "preferences": _build_preferences_snapshot(request),
        "route_summary": {
            "distance_m": distance_m,
            "distance_km": distance_km,
            "estimated_time_min": estimated_time_min,
            "target_distance_km": request.target_distance_km,
            "distance_difference_km": distance_difference_km,
            "routing_strategy_used": routing_strategy_used,
        },
        "route": route_geojson,
    }