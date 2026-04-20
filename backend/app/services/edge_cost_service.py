"""
Edge cost builder for pgr_dijkstra.

Each profile generates a SQL subquery with columns:
    id, source, target, cost, reverse_cost

Cost = length_m * (base_multiplier) * (preference_multipliers...) / divisor

Base multipliers per highway type encode how suitable a road type is for each
profile. Values < 1.0 favour the road; > 1.0 penalise it.

Highway types present in the Vila Real dataset (osm_tag_key = 'highway'):
    cycleway, residential, living_street, service, unclassified, tertiary,
    tertiary_link, secondary, secondary_link, primary, primary_link,
    trunk, trunk_link, motorway, motorway_link, pedestrian, footway,
    path, track, steps
"""

from typing import Tuple


# ---------------------------------------------------------------------------
# Shared multiplier helpers
# ---------------------------------------------------------------------------

def _environment_sql(env: str) -> str:
    if env == "urbana":
        return """
            CASE
                WHEN osm_tag_value IN ('residential','living_street','pedestrian','tertiary','tertiary_link','service')
                    THEN 0.85
                WHEN osm_tag_value IN ('track','path','footway')
                    THEN 1.20
                ELSE 1.00
            END"""
    if env == "rural":
        return """
            CASE
                WHEN osm_tag_value IN ('track','path','cycleway','unclassified')
                    THEN 0.80
                WHEN osm_tag_value IN ('primary','primary_link','secondary','secondary_link','trunk','trunk_link')
                    THEN 1.25
                ELSE 1.00
            END"""
    return "1.00"


def _surface_sql(surface: str) -> str:
    if surface == "asfalto":
        return """
            CASE
                WHEN osm_tag_value IN ('track','path','footway')
                    THEN 1.35
                WHEN osm_tag_value IN ('cycleway')
                    THEN 0.90
                ELSE 1.00
            END"""
    if surface == "asfalto_ecovia":
        return """
            CASE
                WHEN osm_tag_value IN ('cycleway','path','track')
                    THEN 0.90
                ELSE 1.00
            END"""
    return "1.00"


def _green_area_sql(weight: float) -> str:
    if weight >= 0.15:
        return """
            CASE
                WHEN osm_tag_value IN ('path','track','cycleway','footway')
                    THEN 0.80
                ELSE 1.00
            END"""
    if weight >= 0.05:
        return """
            CASE
                WHEN osm_tag_value IN ('path','track','cycleway')
                    THEN 0.90
                ELSE 1.00
            END"""
    return "1.00"


def _poi_sql(weight: float) -> str:
    if weight >= 0.20:
        return """
            CASE
                WHEN osm_tag_value IN ('pedestrian','path','cycleway','residential','living_street','service')
                    THEN 0.85
                ELSE 1.00
            END"""
    if weight >= 0.10:
        return """
            CASE
                WHEN osm_tag_value IN ('pedestrian','cycleway','path')
                    THEN 0.92
                ELSE 1.00
            END"""
    return "1.00"


def _difficulty_sql(penalty: float) -> str:
    """High penalty → avoid demanding roads (good for easy/leisure riders)."""
    if penalty >= 0.25:
        return """
            CASE
                WHEN osm_tag_value IN ('primary','primary_link','secondary','secondary_link','trunk','trunk_link')
                    THEN 1.40
                WHEN osm_tag_value IN ('track','path')
                    THEN 1.20
                ELSE 1.00
            END"""
    if penalty >= 0.10:
        return """
            CASE
                WHEN osm_tag_value IN ('primary','primary_link','secondary','secondary_link')
                    THEN 1.15
                ELSE 1.00
            END"""
    return "1.00"


def _intensity_sql(value: float) -> str:
    """High intensity → favour busier roads; low → avoid them."""
    if value >= 0.08:
        return """
            CASE
                WHEN osm_tag_value IN ('primary','primary_link','secondary','secondary_link','tertiary','tertiary_link')
                    THEN 0.90
                ELSE 1.00
            END"""
    if value <= -0.01:
        return """
            CASE
                WHEN osm_tag_value IN ('primary','primary_link','secondary','secondary_link')
                    THEN 1.10
                ELSE 1.00
            END"""
    return "1.00"


def _fluency_sql(weight: float) -> str:
    """High fluency → favour continuous roads; penalise slow/narrow ones."""
    if weight >= 0.25:
        return """
            CASE
                WHEN osm_tag_value IN ('primary','primary_link','secondary','secondary_link','tertiary','tertiary_link')
                    THEN 0.85
                WHEN osm_tag_value IN ('pedestrian','living_street','footway','steps','path')
                    THEN 1.20
                ELSE 1.00
            END"""
    if weight >= 0.10:
        return """
            CASE
                WHEN osm_tag_value IN ('primary','primary_link','secondary','secondary_link','tertiary','tertiary_link')
                    THEN 0.93
                WHEN osm_tag_value IN ('steps')
                    THEN 1.15
                ELSE 1.00
            END"""
    return "1.00"


# ---------------------------------------------------------------------------
# Profile cost queries
# ---------------------------------------------------------------------------

def _build_leisure_cost_query(session_profile: dict) -> Tuple[str, str]:
    """
    Lazer: prioriza segurança, conforto, ciclovias, zonas agradáveis e POIs.
    Evita fortemente trânsito intenso, troncos e motorways.
    Steps e footway são penalizados (ciclista não quer escadas).
    """
    env   = _environment_sql(session_profile.get("environment_preference", "mista"))
    surf  = _surface_sql(session_profile.get("surface_preference", "indiferente"))
    green = _green_area_sql(session_profile.get("green_area", 0.0))
    poi   = _poi_sql(session_profile.get("points_of_interest", 0.0))
    diff  = _difficulty_sql(session_profile.get("difficulty_penalty", 0.0))

    base = """
        CASE
            WHEN osm_tag_value = 'cycleway'                                    THEN 0.50
            WHEN osm_tag_value IN ('residential','living_street')              THEN 0.65
            WHEN osm_tag_value IN ('pedestrian','path')                        THEN 0.75
            WHEN osm_tag_value IN ('service','unclassified')                   THEN 0.85
            WHEN osm_tag_value IN ('tertiary','tertiary_link')                 THEN 0.95
            WHEN osm_tag_value IN ('track')                                    THEN 1.00
            WHEN osm_tag_value IN ('footway')                                  THEN 1.10
            WHEN osm_tag_value IN ('secondary','secondary_link')               THEN 1.80
            WHEN osm_tag_value IN ('primary','primary_link')                   THEN 3.20
            WHEN osm_tag_value IN ('trunk','trunk_link')                       THEN 6.00
            WHEN osm_tag_value IN ('motorway','motorway_link')                 THEN 12.00
            WHEN osm_tag_value = 'steps'                                       THEN 8.00
            ELSE 1.10
        END"""

    cost_expr = f"""
        (
            length_m
            * ({base})
            * ({env})
            * ({surf})
            * ({green})
            * ({poi})
            * ({diff})
        ) / GREATEST(priority, 0.1)"""

    query = f"""
    SELECT
        gid AS id,
        source,
        target,
        {cost_expr} AS cost,
        {cost_expr} AS reverse_cost
    FROM ways
    WHERE osm_tag_key = 'highway'
    """
    return query, "lazer_conforto_seguranca_exploracao"


def _build_exercise_cost_query(session_profile: dict) -> Tuple[str, str]:
    """
    Exercício: equilibra distância, esforço e segurança.
    Aceita vias mais exigentes que lazer mas evita motorway/trunk.
    Custo = 60% baseado em priority + 40% baseado em velocidade máxima.
    """
    env       = _environment_sql(session_profile.get("environment_preference", "mista"))
    surf      = _surface_sql(session_profile.get("surface_preference", "indiferente"))
    intensity = _intensity_sql(session_profile.get("effort", 0.0))

    base = """
        CASE
            WHEN osm_tag_value = 'cycleway'                                    THEN 0.70
            WHEN osm_tag_value IN ('path','track')                             THEN 0.80
            WHEN osm_tag_value IN ('residential','living_street','unclassified') THEN 0.85
            WHEN osm_tag_value IN ('service')                                  THEN 0.90
            WHEN osm_tag_value IN ('tertiary','tertiary_link')                 THEN 0.90
            WHEN osm_tag_value IN ('secondary','secondary_link')               THEN 1.10
            WHEN osm_tag_value IN ('primary','primary_link')                   THEN 1.60
            WHEN osm_tag_value IN ('trunk','trunk_link')                       THEN 4.00
            WHEN osm_tag_value IN ('motorway','motorway_link')                 THEN 9.00
            WHEN osm_tag_value IN ('footway','pedestrian')                     THEN 1.20
            WHEN osm_tag_value = 'steps'                                       THEN 6.00
            ELSE 1.00
        END"""

    adjusted = f"length_m * ({base}) * ({env}) * ({surf}) * ({intensity})"

    query = f"""
    SELECT
        gid AS id,
        source,
        target,
        (({adjusted}) / GREATEST(priority, 0.1)) * 0.60
            + (({adjusted}) / GREATEST(maxspeed_forward, 10)) * 0.40 AS cost,
        (({adjusted}) / GREATEST(priority, 0.1)) * 0.60
            + (({adjusted}) / GREATEST(maxspeed_backward, 10)) * 0.40 AS reverse_cost
    FROM ways
    WHERE osm_tag_key = 'highway'
    """
    return query, "exercicio_equilibrio_conforto_desempenho"


def _build_competition_cost_query(session_profile: dict) -> Tuple[str, str]:
    """
    Competição: prioriza fluidez e velocidade em vias contínuas asfaltadas.
    Ciclovias são neutras (não são longas o suficiente para competição).
    Evita pedestrian/steps/footway; motorway proibida.
    Custo baseado em velocidade máxima (tempo estimado de percurso).
    """
    surf    = _surface_sql(session_profile.get("surface_preference", "indiferente"))
    fluency = _fluency_sql(session_profile.get("fluency", 0.0))
    intensity = _intensity_sql(session_profile.get("speed", 0.0))

    base = """
        CASE
            WHEN osm_tag_value IN ('primary','primary_link')                   THEN 0.65
            WHEN osm_tag_value IN ('secondary','secondary_link')               THEN 0.70
            WHEN osm_tag_value IN ('tertiary','tertiary_link')                 THEN 0.80
            WHEN osm_tag_value IN ('trunk','trunk_link')                       THEN 0.90
            WHEN osm_tag_value IN ('unclassified','service')                   THEN 1.00
            WHEN osm_tag_value IN ('residential','living_street')              THEN 1.30
            WHEN osm_tag_value = 'cycleway'                                    THEN 1.10
            WHEN osm_tag_value IN ('track','path')                             THEN 1.50
            WHEN osm_tag_value IN ('footway','pedestrian')                     THEN 2.50
            WHEN osm_tag_value IN ('motorway','motorway_link')                 THEN 6.00
            WHEN osm_tag_value = 'steps'                                       THEN 10.00
            ELSE 1.20
        END"""

    cost_expr = f"""
        (
            length_m
            * ({base})
            * ({surf})
            * ({fluency})
            * ({intensity})
        ) / GREATEST(maxspeed_forward, 10)"""

    rev_cost_expr = f"""
        (
            length_m
            * ({base})
            * ({surf})
            * ({fluency})
            * ({intensity})
        ) / GREATEST(maxspeed_backward, 10)"""

    query = f"""
    SELECT
        gid AS id,
        source,
        target,
        {cost_expr} AS cost,
        {rev_cost_expr} AS reverse_cost
    FROM ways
    WHERE osm_tag_key = 'highway'
    """
    return query, "competicao_fluidez_velocidade"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_cost_query(profile_type: str, session_profile: dict) -> Tuple[str, str]:
    if profile_type == "lazer":
        return _build_leisure_cost_query(session_profile)
    if profile_type == "competicao":
        return _build_competition_cost_query(session_profile)
    return _build_exercise_cost_query(session_profile)
