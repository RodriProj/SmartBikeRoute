from typing import Tuple


# ---------------------------------------------------------------------------
# SQL helpers para multiplicadores contextuais
# ---------------------------------------------------------------------------

def _get_environment_multiplier_sql(environment_preference: str) -> str:
    """
    Ajusta o custo consoante a preferência de ambiente:
    - urbana
    - rural
    - mista
    """
    environment_map = {
        "urbana": """
            CASE
                WHEN osm_tag_key = 'highway'
                     AND osm_tag_value IN ('residential', 'living_street', 'pedestrian', 'tertiary', 'tertiary_link')
                    THEN 0.85
                WHEN osm_tag_key = 'highway'
                     AND osm_tag_value IN ('track', 'path')
                    THEN 1.20
                ELSE 1.00
            END
        """,
        "rural": """
            CASE
                WHEN osm_tag_key = 'highway'
                     AND osm_tag_value IN ('track', 'path', 'cycleway')
                    THEN 0.80
                WHEN osm_tag_key = 'highway'
                     AND osm_tag_value IN ('primary', 'primary_link', 'secondary', 'secondary_link')
                    THEN 1.25
                ELSE 1.00
            END
        """,
        "mista": "1.00",
    }

    return environment_map.get(environment_preference, "1.00")


def _get_surface_multiplier_sql(surface_preference: str) -> str:
    """
    Ajusta o custo consoante a preferência de piso.
    Como ainda não existe surface_type materializado, usamos aproximações por tipo de via.
    """
    surface_map = {
        "asfalto": """
            CASE
                WHEN osm_tag_key = 'highway'
                     AND osm_tag_value IN ('track', 'path')
                    THEN 1.30
                ELSE 1.00
            END
        """,
        "asfalto_ecovia": """
            CASE
                WHEN osm_tag_key = 'highway'
                     AND osm_tag_value IN ('cycleway', 'path', 'track')
                    THEN 0.95
                ELSE 1.00
            END
        """,
        "indiferente": "1.00",
    }

    return surface_map.get(surface_preference, "1.00")


def _get_green_area_multiplier_sql(green_area_weight: float) -> str:
    """
    Aproximação inicial para zonas verdes/natureza.
    Sem green_score materializado, favorecemos path/track/cycleway quando o peso é alto.
    """
    if green_area_weight >= 0.15:
        return """
            CASE
                WHEN osm_tag_key = 'highway'
                     AND osm_tag_value IN ('path', 'track', 'cycleway')
                    THEN 0.80
                ELSE 1.00
            END
        """

    if green_area_weight >= 0.05:
        return """
            CASE
                WHEN osm_tag_key = 'highway'
                     AND osm_tag_value IN ('path', 'track', 'cycleway')
                    THEN 0.90
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
                WHEN osm_tag_key = 'highway'
                     AND osm_tag_value IN ('pedestrian', 'path', 'cycleway', 'residential', 'living_street')
                    THEN 0.85
                ELSE 1.00
            END
        """

    if points_of_interest_weight >= 0.10:
        return """
            CASE
                WHEN osm_tag_key = 'highway'
                     AND osm_tag_value IN ('pedestrian', 'path', 'cycleway')
                    THEN 0.92
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
                WHEN osm_tag_key = 'highway'
                     AND osm_tag_value IN ('primary', 'primary_link', 'secondary', 'secondary_link', 'track')
                    THEN 1.35
                ELSE 1.00
            END
        """

    if difficulty_penalty >= 0.10:
        return """
            CASE
                WHEN osm_tag_key = 'highway'
                     AND osm_tag_value IN ('primary', 'primary_link', 'secondary', 'secondary_link')
                    THEN 1.15
                ELSE 1.00
            END
        """

    return "1.00"


def _get_intensity_multiplier_sql(intensity_value: float) -> str:
    """
    Ajuste genérico para intensidade.
    Quanto maior a intensidade, menor a penalização de vias mais exigentes.
    """
    if intensity_value >= 0.08:
        return """
            CASE
                WHEN osm_tag_key = 'highway'
                     AND osm_tag_value IN ('primary', 'primary_link', 'secondary', 'secondary_link', 'tertiary', 'tertiary_link')
                    THEN 0.90
                ELSE 1.00
            END
        """

    if intensity_value <= -0.01:
        return """
            CASE
                WHEN osm_tag_key = 'highway'
                     AND osm_tag_value IN ('primary', 'primary_link', 'secondary', 'secondary_link')
                    THEN 1.10
                ELSE 1.00
            END
        """

    return "1.00"


def _get_fluency_multiplier_sql(fluency_weight: float) -> str:
    """
    Ajuste para fluidez.
    Quanto maior a fluidez desejada, mais favorece vias mais contínuas.
    """
    if fluency_weight >= 0.25:
        return """
            CASE
                WHEN osm_tag_key = 'highway'
                     AND osm_tag_value IN ('primary', 'primary_link', 'secondary', 'secondary_link', 'tertiary', 'tertiary_link')
                    THEN 0.85
                WHEN osm_tag_key = 'highway'
                     AND osm_tag_value IN ('pedestrian', 'living_street', 'path')
                    THEN 1.15
                ELSE 1.00
            END
        """

    if fluency_weight >= 0.10:
        return """
            CASE
                WHEN osm_tag_key = 'highway'
                     AND osm_tag_value IN ('primary', 'primary_link', 'secondary', 'secondary_link', 'tertiary', 'tertiary_link')
                    THEN 0.93
                ELSE 1.00
            END
        """

    return "1.00"


# ---------------------------------------------------------------------------
# Base cost expressions por perfil
# ---------------------------------------------------------------------------

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

    base_case_sql = """
        CASE
            WHEN osm_tag_key = 'highway'
                 AND osm_tag_value IN ('cycleway', 'residential', 'living_street', 'pedestrian', 'path')
                THEN 0.60
            WHEN osm_tag_key = 'highway'
                 AND osm_tag_value IN ('tertiary', 'tertiary_link')
                THEN 0.90
            WHEN osm_tag_key = 'highway'
                 AND osm_tag_value IN ('secondary', 'secondary_link')
                THEN 1.80
            WHEN osm_tag_key = 'highway'
                 AND osm_tag_value IN ('primary', 'primary_link')
                THEN 3.20
            WHEN osm_tag_key = 'highway'
                 AND osm_tag_value IN ('motorway', 'motorway_link')
                THEN 10.00
            WHEN osm_tag_key = 'cycleway'
                 AND osm_tag_value IN ('lane', 'track', 'opposite_lane', 'opposite_track')
                THEN 0.50
            ELSE 1.20
        END
    """

    query = f"""
    SELECT
        gid AS id,
        source,
        target,
        (
            length_m
            * ({base_case_sql})
            * ({environment_sql})
            * ({surface_sql})
            * ({green_sql})
            * ({poi_sql})
            * ({difficulty_sql})
        ) / GREATEST(priority, 0.1) AS cost,

        (
            length_m
            * ({base_case_sql})
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
    effort_weight = session_profile.get("effort", 0.0)

    environment_sql = _get_environment_multiplier_sql(environment_preference)
    surface_sql = _get_surface_multiplier_sql(surface_preference)
    intensity_sql = _get_intensity_multiplier_sql(effort_weight)

    base_case_sql = """
        CASE
            WHEN osm_tag_key = 'highway'
                 AND osm_tag_value IN ('cycleway', 'path', 'track')
                THEN 0.85
            WHEN osm_tag_key = 'highway'
                 AND osm_tag_value IN ('residential', 'living_street', 'tertiary', 'tertiary_link')
                THEN 0.90
            WHEN osm_tag_key = 'highway'
                 AND osm_tag_value IN ('secondary', 'secondary_link')
                THEN 1.20
            WHEN osm_tag_key = 'highway'
                 AND osm_tag_value IN ('primary', 'primary_link')
                THEN 1.80
            WHEN osm_tag_key = 'highway'
                 AND osm_tag_value IN ('motorway', 'motorway_link')
                THEN 8.00
            ELSE 1.00
        END
    """

    query = f"""
    SELECT
        gid AS id,
        source,
        target,
        (
            (
                length_m
                * ({base_case_sql})
                * ({environment_sql})
                * ({surface_sql})
                * ({intensity_sql})
            ) / GREATEST(priority, 0.1)
        ) * 0.60
        +
        (
            (
                length_m
                * ({base_case_sql})
                * ({environment_sql})
                * ({surface_sql})
                * ({intensity_sql})
            ) / GREATEST(maxspeed_forward, 10)
        ) * 0.40 AS cost,

        (
            (
                length_m
                * ({base_case_sql})
                * ({environment_sql})
                * ({surface_sql})
                * ({intensity_sql})
            ) / GREATEST(priority, 0.1)
        ) * 0.60
        +
        (
            (
                length_m
                * ({base_case_sql})
                * ({environment_sql})
                * ({surface_sql})
                * ({intensity_sql})
            ) / GREATEST(maxspeed_backward, 10)
        ) * 0.40 AS reverse_cost
    FROM ways
    """

    return query, "exercicio_equilibra_conforto_e_desempenho"


def _build_competition_cost_query(session_profile: dict) -> Tuple[str, str]:
    surface_preference = session_profile.get("surface_preference", "indiferente")
    fluency_weight = session_profile.get("fluency", 0.0)
    speed_weight = session_profile.get("speed", 0.0)

    surface_sql = _get_surface_multiplier_sql(surface_preference)
    fluency_sql = _get_fluency_multiplier_sql(fluency_weight)
    intensity_sql = _get_intensity_multiplier_sql(speed_weight)

    base_case_sql = """
        CASE
            WHEN osm_tag_key = 'highway'
                 AND osm_tag_value IN ('primary', 'primary_link', 'secondary', 'secondary_link', 'tertiary', 'tertiary_link')
                THEN 0.70
            WHEN osm_tag_key = 'highway'
                 AND osm_tag_value IN ('residential', 'living_street', 'pedestrian', 'path')
                THEN 1.40
            WHEN osm_tag_key = 'highway'
                 AND osm_tag_value IN ('cycleway')
                THEN 1.20
            WHEN osm_tag_key = 'highway'
                 AND osm_tag_value IN ('motorway', 'motorway_link')
                THEN 5.00
            ELSE 1.00
        END
    """

    query = f"""
    SELECT
        gid AS id,
        source,
        target,
        (
            length_m
            * ({base_case_sql})
            * ({surface_sql})
            * ({fluency_sql})
            * ({intensity_sql})
        ) / GREATEST(maxspeed_forward, 10) AS cost,

        (
            length_m
            * ({base_case_sql})
            * ({surface_sql})
            * ({fluency_sql})
            * ({intensity_sql})
        ) / GREATEST(maxspeed_backward, 10) AS reverse_cost
    FROM ways
    """

    return query, "competicao_prioriza_fluidez_e_velocidade"


# ---------------------------------------------------------------------------
# API pública do serviço
# ---------------------------------------------------------------------------

def build_cost_query(profile_type: str, session_profile: dict) -> Tuple[str, str]:
    """
    Constrói a query SQL de custo por aresta consoante:
    - o perfil principal (lazer, exercício, competição)
    - o perfil final da sessão ajustado por preferências avançadas

    Retorna:
    - query SQL a usar no pgr_dijkstra
    - nome descritivo da estratégia de routing
    """
    if profile_type == "lazer":
        return _build_leisure_cost_query(session_profile)

    if profile_type == "competicao":
        return _build_competition_cost_query(session_profile)

    return _build_exercise_cost_query(session_profile)