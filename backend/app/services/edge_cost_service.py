from typing import Tuple


def _get_environment_multiplier_sql(environment_preference: str) -> str:
    """
    Ajusta o custo consoante a preferência de ambiente:
    - urbana
    - rural
    - mista
    """
    if environment_preference == "urbana":
        return """
        CASE
            WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('residential', 'living_street', 'pedestrian', 'tertiary', 'tertiary_link') THEN 0.85
            WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('track', 'path') THEN 1.20
            ELSE 1.00
        END
        """

    if environment_preference == "rural":
        return """
        CASE
            WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('track', 'path', 'cycleway') THEN 0.80
            WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('primary', 'primary_link', 'secondary', 'secondary_link') THEN 1.25
            ELSE 1.00
        END
        """

    return "1.00"


def _get_surface_multiplier_sql(surface_preference: str) -> str:
    """
    Ajusta o custo consoante a preferência de piso.
    Como ainda não tens surface_type materializado, usamos aproximações por tipo de via.
    """
    if surface_preference == "asfalto":
        return """
        CASE
            WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('track', 'path') THEN 1.30
            ELSE 1.00
        END
        """

    if surface_preference == "asfalto_ecovia":
        return """
        CASE
            WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('cycleway', 'path', 'track') THEN 0.95
            ELSE 1.00
        END
        """

    return "1.00"


def _get_green_area_multiplier_sql(green_area_weight: float) -> str:
    """
    Aproximação inicial para zonas verdes/natureza.
    Sem green_score materializado, favorecemos path/track/cycleway quando o peso é alto.
    """
    if green_area_weight >= 0.15:
        return """
        CASE
            WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('path', 'track', 'cycleway') THEN 0.80
            ELSE 1.00
        END
        """

    if green_area_weight >= 0.05:
        return """
        CASE
            WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('path', 'track', 'cycleway') THEN 0.90
            ELSE 1.00
        END
        """

    return "1.00"


def _get_points_of_interest_multiplier_sql(points_of_interest_weight: float) -> str:
    """
    Aproximação inicial para pontos de interesse.
    Sem tabela dedicada de POIs, favorecemos pedestrian/path/cycleway/residential
    como proxy de zonas mais agradáveis e exploratórias.
    """
    if points_of_interest_weight >= 0.20:
        return """
        CASE
            WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('pedestrian', 'path', 'cycleway', 'residential', 'living_street') THEN 0.85
            ELSE 1.00
        END
        """

    if points_of_interest_weight >= 0.10:
        return """
        CASE
            WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('pedestrian', 'path', 'cycleway') THEN 0.92
            ELSE 1.00
        END
        """

    return "1.00"


def _get_difficulty_multiplier_sql(difficulty_penalty: float) -> str:
    """
    Penaliza vias potencialmente menos confortáveis para lazer muito fácil.
    """
    if difficulty_penalty >= 0.25:
        return """
        CASE
            WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('primary', 'primary_link', 'secondary', 'secondary_link', 'track') THEN 1.35
            ELSE 1.00
        END
        """

    if difficulty_penalty >= 0.10:
        return """
        CASE
            WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('primary', 'primary_link', 'secondary', 'secondary_link') THEN 1.15
            ELSE 1.00
        END
        """

    return "1.00"


def _build_leisure_cost_query(session_profile: dict) -> Tuple[str, str]:
    environment_preference = session_profile.get("environment_preference", "mista")
    surface_preference = session_profile.get("surface_preference", "indiferente")
    green_area_weight = session_profile.get("green_area", 0.0)
    points_of_interest_weight = session_profile.get("points_of_interest", 0.0)
    difficulty_penalty = session_profile.get("difficulty_penalty", 0.0)

    environment_sql = _get_environment_multiplier_sql(environment_preference)
    surface_sql = _get_surface_multiplier_sql(surface_preference)
    green_sql = _get_green_area_multiplier_sql(green_area_weight)
    poi_sql = _get_points_of_interest_multiplier_sql(points_of_interest_weight)
    difficulty_sql = _get_difficulty_multiplier_sql(difficulty_penalty)

    query = f"""
    SELECT
        gid AS id,
        source,
        target,
        (
            length_m
            * CASE
                WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('cycleway', 'residential', 'living_street', 'pedestrian', 'path') THEN 0.60
                WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('tertiary', 'tertiary_link') THEN 0.90
                WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('secondary', 'secondary_link') THEN 1.80
                WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('primary', 'primary_link') THEN 3.20
                WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('motorway', 'motorway_link') THEN 10.00
                WHEN osm_tag_key = 'cycleway' AND osm_tag_value IN ('lane', 'track', 'opposite_lane', 'opposite_track') THEN 0.50
                ELSE 1.20
              END
            * ({environment_sql})
            * ({surface_sql})
            * ({green_sql})
            * ({poi_sql})
            * ({difficulty_sql})
        ) / GREATEST(priority, 0.1) AS cost,

        (
            length_m
            * CASE
                WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('cycleway', 'residential', 'living_street', 'pedestrian', 'path') THEN 0.60
                WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('tertiary', 'tertiary_link') THEN 0.90
                WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('secondary', 'secondary_link') THEN 1.80
                WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('primary', 'primary_link') THEN 3.20
                WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('motorway', 'motorway_link') THEN 10.00
                WHEN osm_tag_key = 'cycleway' AND osm_tag_value IN ('lane', 'track', 'opposite_lane', 'opposite_track') THEN 0.50
                ELSE 1.20
              END
            * ({environment_sql})
            * ({surface_sql})
            * ({green_sql})
            * ({poi_sql})
            * ({difficulty_sql})
        ) / GREATEST(priority, 0.1) AS reverse_cost
    FROM ways
    """

    return query, "lazer_prioriza_conforto_ambiente_e_exploracao"


def _build_exercise_cost_query(session_profile: dict) -> Tuple[str, str]:
    environment_preference = session_profile.get("environment_preference", "mista")
    surface_preference = session_profile.get("surface_preference", "indiferente")

    environment_sql = _get_environment_multiplier_sql(environment_preference)
    surface_sql = _get_surface_multiplier_sql(surface_preference)

    query = f"""
    SELECT
        gid AS id,
        source,
        target,
        (
            (
                length_m
                * CASE
                    WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('cycleway', 'path', 'track') THEN 0.85
                    WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('residential', 'living_street', 'tertiary', 'tertiary_link') THEN 0.90
                    WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('secondary', 'secondary_link') THEN 1.20
                    WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('primary', 'primary_link') THEN 1.80
                    WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('motorway', 'motorway_link') THEN 8.00
                    ELSE 1.00
                  END
                * ({environment_sql})
                * ({surface_sql})
            ) / GREATEST(priority, 0.1)
        ) * 0.60
        +
        (
            (
                length_m
                * CASE
                    WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('cycleway', 'path', 'track') THEN 0.85
                    WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('residential', 'living_street', 'tertiary', 'tertiary_link') THEN 0.90
                    WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('secondary', 'secondary_link') THEN 1.20
                    WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('primary', 'primary_link') THEN 1.80
                    WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('motorway', 'motorway_link') THEN 8.00
                    ELSE 1.00
                  END
                * ({environment_sql})
                * ({surface_sql})
            ) / GREATEST(maxspeed_forward, 10)
        ) * 0.40 AS cost,

        (
            (
                length_m
                * CASE
                    WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('cycleway', 'path', 'track') THEN 0.85
                    WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('residential', 'living_street', 'tertiary', 'tertiary_link') THEN 0.90
                    WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('secondary', 'secondary_link') THEN 1.20
                    WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('primary', 'primary_link') THEN 1.80
                    WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('motorway', 'motorway_link') THEN 8.00
                    ELSE 1.00
                  END
                * ({environment_sql})
                * ({surface_sql})
            ) / GREATEST(priority, 0.1)
        ) * 0.60
        +
        (
            (
                length_m
                * CASE
                    WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('cycleway', 'path', 'track') THEN 0.85
                    WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('residential', 'living_street', 'tertiary', 'tertiary_link') THEN 0.90
                    WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('secondary', 'secondary_link') THEN 1.20
                    WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('primary', 'primary_link') THEN 1.80
                    WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('motorway', 'motorway_link') THEN 8.00
                    ELSE 1.00
                  END
                * ({environment_sql})
                * ({surface_sql})
            ) / GREATEST(maxspeed_backward, 10)
        ) * 0.40 AS reverse_cost
    FROM ways
    """

    return query, "exercicio_equilibra_conforto_e_desempenho"


def _build_competition_cost_query(session_profile: dict) -> Tuple[str, str]:
    surface_preference = session_profile.get("surface_preference", "indiferente")
    surface_sql = _get_surface_multiplier_sql(surface_preference)

    query = f"""
    SELECT
        gid AS id,
        source,
        target,
        (
            length_m
            * CASE
                WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('primary', 'primary_link', 'secondary', 'secondary_link', 'tertiary', 'tertiary_link') THEN 0.70
                WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('residential', 'living_street', 'pedestrian', 'path') THEN 1.40
                WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('cycleway') THEN 1.20
                WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('motorway', 'motorway_link') THEN 5.00
                ELSE 1.00
              END
            * ({surface_sql})
        ) / GREATEST(maxspeed_forward, 10) AS cost,

        (
            length_m
            * CASE
                WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('primary', 'primary_link', 'secondary', 'secondary_link', 'tertiary', 'tertiary_link') THEN 0.70
                WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('residential', 'living_street', 'pedestrian', 'path') THEN 1.40
                WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('cycleway') THEN 1.20
                WHEN osm_tag_key = 'highway' AND osm_tag_value IN ('motorway', 'motorway_link') THEN 5.00
                ELSE 1.00
              END
            * ({surface_sql})
        ) / GREATEST(maxspeed_backward, 10) AS reverse_cost
    FROM ways
    """

    return query, "competicao_prioriza_fluidez_e_velocidade"


def build_cost_query(profile_type: str, session_profile: dict) -> Tuple[str, str]:
    """
    Devolve a query SQL de custo por aresta e o nome da estratégia usada.
    """
    if profile_type == "lazer":
        return _build_leisure_cost_query(session_profile)

    if profile_type == "competicao":
        return _build_competition_cost_query(session_profile)

    return _build_exercise_cost_query(session_profile)