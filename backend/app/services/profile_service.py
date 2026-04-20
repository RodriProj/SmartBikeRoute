"""
Constrói o session_profile final a partir das preferências do utilizador.

O session_profile é um dict passado ao edge_cost_service para gerar
a query de custo. Contém:
- pesos numéricos (ex: green_area, difficulty_penalty, effort, speed, fluency)
- preferências string (environment_preference, surface_preference)
- metadados (target_distance_km, loop)
"""

from copy import deepcopy

from app.core.weights import PROFILE_WEIGHTS


# ---------------------------------------------------------------------------
# Mapas de ajuste (delta aplicado ao peso base)
# ---------------------------------------------------------------------------

SCENIC_DELTA = {"baixa": -0.10, "media": 0.00, "alta": 0.15}
TRAFFIC_DELTA = {"baixa": -0.10, "media": 0.00, "alta": 0.20}
ELEVATION_DELTA = {"baixa": -0.15, "media": 0.00, "alta": 0.15}
INTENSITY_DELTA = {"baixa": -0.05, "media": 0.00, "alta": 0.10}

# Valores absolutos (substituem o peso base diretamente)
FLUENCY_VALUES = {"baixa": 0.05, "media": 0.15, "alta": 0.30}
DIFFICULTY_VALUES = {"muito_facil": 0.30, "facil": 0.15, "moderada": 0.05}
POI_VALUES = {"baixa": 0.05, "media": 0.15, "alta": 0.25}
GREEN_VALUES = {"baixa": 0.00, "media": 0.10, "alta": 0.20}


def _delta(weights: dict, key: str, amount: float) -> None:
    """Aplica delta aditivo com piso em 0."""
    weights[key] = max(0.0, weights.get(key, 0.0) + amount)


def _set(weights: dict, key: str, value: float) -> None:
    """Define valor absoluto."""
    weights[key] = value


# ---------------------------------------------------------------------------
# Preferências comuns a todos os perfis
# ---------------------------------------------------------------------------

def _apply_common(weights: dict, request) -> None:
    _delta(weights, "scenic", SCENIC_DELTA.get(request.scenic_preference, 0.0))
    _delta(weights, "traffic_avoidance", TRAFFIC_DELTA.get(request.traffic_avoidance, 0.0))
    _delta(weights, "elevation", ELEVATION_DELTA.get(request.elevation_preference, 0.0))
    weights["environment_preference"] = request.environment_preference
    weights["surface_preference"] = request.surface_preference
    weights["target_distance_km"] = request.target_distance_km
    weights["loop"] = request.loop


# ---------------------------------------------------------------------------
# Preferências específicas por perfil
# ---------------------------------------------------------------------------

def _apply_leisure(weights: dict, request) -> None:
    _set(weights, "difficulty_penalty", DIFFICULTY_VALUES.get(request.difficulty_level, 0.15))
    _set(weights, "points_of_interest", POI_VALUES.get(request.points_of_interest_preference, 0.15))
    _set(weights, "green_area", GREEN_VALUES.get(request.green_area_preference, 0.10))


def _apply_exercise(weights: dict, request) -> None:
    _delta(weights, "effort", INTENSITY_DELTA.get(request.intensity_preference, 0.0))

    goal = request.training_goal
    if goal == "queimar_gordura":
        _delta(weights, "distance_fit", 0.10)
        _delta(weights, "traffic_avoidance", 0.05)
        _delta(weights, "elevation", -0.05)
    elif goal == "ganhar_resistencia":
        _delta(weights, "distance_fit", 0.15)
        _delta(weights, "effort", 0.10)
    elif goal == "trabalhar_musculo":
        _delta(weights, "elevation", 0.20)
        _delta(weights, "effort", 0.15)
    elif goal == "recuperacao_ativa":
        _delta(weights, "traffic_avoidance", 0.10)
        _delta(weights, "scenic", 0.05)
        _delta(weights, "elevation", -0.20)
        _set(weights, "difficulty_penalty", 0.30)
    elif goal == "treino_misto":
        _delta(weights, "distance_fit", 0.05)
        _delta(weights, "effort", 0.05)
        _delta(weights, "elevation", 0.05)


def _apply_competition(weights: dict, request) -> None:
    _delta(weights, "speed", INTENSITY_DELTA.get(request.intensity_preference, 0.0))
    _set(weights, "fluency", FLUENCY_VALUES.get(request.route_fluency, 0.15))

    goal = request.training_goal
    if goal == "velocidade":
        _delta(weights, "speed", 0.20)
        _delta(weights, "fluency", 0.10)
    elif goal == "ritmo_constante":
        _delta(weights, "fluency", 0.20)
        _delta(weights, "traffic_avoidance", 0.05)
    elif goal == "subida":
        _delta(weights, "elevation", 0.20)
        _delta(weights, "speed", 0.05)
    elif goal == "resistencia_competitiva":
        _delta(weights, "distance_fit", 0.15)
        _delta(weights, "fluency", 0.10)
    elif goal == "simulacao_prova":
        _delta(weights, "speed", 0.15)
        _delta(weights, "fluency", 0.15)
        _delta(weights, "distance_fit", 0.10)


# ---------------------------------------------------------------------------
# Ponto de entrada público
# ---------------------------------------------------------------------------

def build_session_profile(request) -> dict:
    weights = deepcopy(PROFILE_WEIGHTS.get(request.profile_type, {}))
    _apply_common(weights, request)

    if request.profile_type == "lazer":
        _apply_leisure(weights, request)
    elif request.profile_type == "exercicio":
        _apply_exercise(weights, request)
    elif request.profile_type == "competicao":
        _apply_competition(weights, request)

    return weights
