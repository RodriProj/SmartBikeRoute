import json
import psycopg2
from psycopg2.extras import RealDictCursor

from app.core.config import DB
from app.services.scoring_service import (
    calculate_estimated_time,
    calculate_distance_difference,
)


def get_conn():
    return psycopg2.connect(**DB)


def build_cost_query(profile_type: str) -> tuple[str, str]:
    """
    Constrói a query SQL de custo por aresta consoante o perfil.
    Devolve:
    - SQL string para o pgr_dijkstra
    - nome da estratégia usada
    """

    if profile_type == "lazer":
        return (
            """
            SELECT
                gid AS id,
                source,
                target,
                (
                    length_m
                    * CASE
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('cycleway', 'residential', 'living_street', 'pedestrian', 'path') THEN 0.6
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('tertiary', 'tertiary_link') THEN 0.9
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('secondary', 'secondary_link') THEN 1.8
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('primary', 'primary_link') THEN 3.0
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('motorway', 'motorway_link') THEN 10.0
                        WHEN osm_tag_key = 'cycleway' AND osm_tag_value IN ('lane', 'track', 'opposite_lane', 'opposite_track') THEN 0.5
                        ELSE 1.2
                      END
                ) / GREATEST(priority, 0.1) AS cost,

                (
                    length_m
                    * CASE
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('cycleway', 'residential', 'living_street', 'pedestrian', 'path') THEN 0.6
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('tertiary', 'tertiary_link') THEN 0.9
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('secondary', 'secondary_link') THEN 1.8
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('primary', 'primary_link') THEN 3.0
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('motorway', 'motorway_link') THEN 10.0
                        WHEN osm_tag_key = 'cycleway' AND osm_tag_value IN ('lane', 'track', 'opposite_lane', 'opposite_track') THEN 0.5
                        ELSE 1.2
                      END
                ) / GREATEST(priority, 0.1) AS reverse_cost
            FROM ways
            """,
            "lazer_prioriza_vias_calmas_e_ciclaveis",
        )

    if profile_type == "competicao":
        return (
            """
            SELECT
                gid AS id,
                source,
                target,
                (
                    length_m
                    * CASE
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('primary', 'primary_link', 'secondary', 'secondary_link', 'tertiary', 'tertiary_link') THEN 0.7
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('residential', 'living_street', 'pedestrian', 'path') THEN 1.4
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('cycleway') THEN 1.2
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('motorway', 'motorway_link') THEN 5.0
                        ELSE 1.0
                      END
                ) / GREATEST(maxspeed_forward, 10) AS cost,

                (
                    length_m
                    * CASE
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('primary', 'primary_link', 'secondary', 'secondary_link', 'tertiary', 'tertiary_link') THEN 0.7
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('residential', 'living_street', 'pedestrian', 'path') THEN 1.4
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('cycleway') THEN 1.2
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('motorway', 'motorway_link') THEN 5.0
                        ELSE 1.0
                      END
                ) / GREATEST(maxspeed_backward, 10) AS reverse_cost
            FROM ways
            """,
            "competicao_prioriza_fluidez_e_velocidade",
        )

    return (
        """
        SELECT
            gid AS id,
            source,
            target,
            (
                (
                    length_m
                    * CASE
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('cycleway', 'path', 'track') THEN 0.8
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('residential', 'living_street', 'tertiary', 'tertiary_link') THEN 0.9
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('secondary', 'secondary_link') THEN 1.2
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('primary', 'primary_link') THEN 1.8
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('motorway', 'motorway_link') THEN 8.0
                        ELSE 1.0
                      END
                ) / GREATEST(priority, 0.1)
            ) * 0.6
            +
            (
                (
                    length_m
                    * CASE
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('cycleway', 'path', 'track') THEN 0.8
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('residential', 'living_street', 'tertiary', 'tertiary_link') THEN 0.9
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('secondary', 'secondary_link') THEN 1.2
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('primary', 'primary_link') THEN 1.8
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('motorway', 'motorway_link') THEN 8.0
                        ELSE 1.0
                      END
                ) / GREATEST(maxspeed_forward, 10)
            ) * 0.4 AS cost,

            (
                (
                    length_m
                    * CASE
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('cycleway', 'path', 'track') THEN 0.8
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('residential', 'living_street', 'tertiary', 'tertiary_link') THEN 0.9
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('secondary', 'secondary_link') THEN 1.2
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('primary', 'primary_link') THEN 1.8
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('motorway', 'motorway_link') THEN 8.0
                        ELSE 1.0
                      END
                ) / GREATEST(priority, 0.1)
            ) * 0.6
            +
            (
                (
                    length_m
                    * CASE
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('cycleway', 'path', 'track') THEN 0.8
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('residential', 'living_street', 'tertiary', 'tertiary_link') THEN 0.9
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('secondary', 'secondary_link') THEN 1.2
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('primary', 'primary_link') THEN 1.8
                        WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('motorway', 'motorway_link') THEN 8.0
                        ELSE 1.0
                      END
                ) / GREATEST(maxspeed_backward, 10)
            ) * 0.4 AS reverse_cost
        FROM ways
        """,
        "exercicio_equilibra_conforto_e_desempenho",
    )


def calculate_route(
    startLat: float,
    startLon: float,
    endLat: float,
    endLon: float,
    profile_type: str = "lazer",
):
    """
    Calcula uma rota entre dois pontos usando um modelo de custo
    adaptado ao perfil do utilizador.
    """
    cost_query, routing_strategy_used = build_cost_query(profile_type)

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
            cur.execute(q, (startLon, startLat, endLon, endLat, cost_query))
            row = cur.fetchone()

    if not row or row["geojson"] is None:
        return {
            "type": "FeatureCollection",
            "features": [],
            "summary": {
                "distance_m": 0,
                "distance_km": 0,
                "routing_strategy_used": routing_strategy_used,
            },
        }

    distance_m = round(row["length_m"], 2)
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


def generate_personalized_route(request, session_profile):
    """
    Gera uma rota personalizada com base no perfil selecionado
    e nas preferências avançadas da sessão.
    """
    route_geojson = calculate_route(
        startLat=request.startLat,
        startLon=request.startLon,
        endLat=request.endLat,
        endLon=request.endLon,
        profile_type=request.profile_type,
    )

    route_summary = route_geojson.get("summary", {})
    distance_m = route_summary.get("distance_m", 0)
    distance_km = route_summary.get("distance_km", 0)
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
        "preferences": {
            "target_distance_km": request.target_distance_km,
            "elevation_preference": request.elevation_preference,
            "scenic_preference": request.scenic_preference,
            "traffic_avoidance": request.traffic_avoidance,
            "loop": request.loop,
            "training_goal": request.training_goal,
        },
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