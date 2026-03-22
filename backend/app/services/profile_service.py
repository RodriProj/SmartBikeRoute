from copy import deepcopy

from app.core.weights import PROFILE_WEIGHTS


SCENIC_ADJUSTMENT_MAP = {
    "baixa": -0.10,
    "media": 0.00,
    "alta": 0.15,
}

TRAFFIC_ADJUSTMENT_MAP = {
    "baixa": -0.10,
    "media": 0.00,
    "alta": 0.20,
}

ELEVATION_ADJUSTMENT_MAP = {
    "baixa": -0.15,
    "media": 0.00,
    "alta": 0.15,
}

INTENSITY_ADJUSTMENT_MAP = {
    "baixa": -0.05,
    "media": 0.00,
    "alta": 0.10,
}

ROUTE_FLUENCY_MAP = {
    "baixa": 0.05,
    "media": 0.15,
    "alta": 0.30,
}

DIFFICULTY_PENALTY_MAP = {
    "muito_facil": 0.30,
    "facil": 0.15,
    "moderada": 0.05,
}

POINTS_OF_INTEREST_MAP = {
    "baixa": 0.05,
    "media": 0.15,
    "alta": 0.25,
}

GREEN_AREA_MAP = {
    "baixa": 0.00,
    "media": 0.10,
    "alta": 0.20,
}


def _adjust_weight(weights: dict, key: str, delta: float) -> None:
    """
    Ajusta um peso numérico sem permitir valores negativos.
    """
    current_value = weights.get(key, 0.0)
    weights[key] = max(0.0, current_value + delta)


def _set_weight_from_map(weights: dict, key: str, selected_value: str, mapping: dict) -> None:
    """
    Define diretamente um peso/penalização com base num mapa de valores.
    """
    weights[key] = mapping.get(selected_value, weights.get(key, 0.0))


def _apply_common_preferences(weights: dict, request) -> None:
    """
    Aplica preferências transversais comuns aos 3 modos.
    """
    _adjust_weight(
        weights=weights,
        key="scenic",
        delta=SCENIC_ADJUSTMENT_MAP.get(request.scenic_preference, 0.0),
    )

    _adjust_weight(
        weights=weights,
        key="traffic_avoidance",
        delta=TRAFFIC_ADJUSTMENT_MAP.get(request.traffic_avoidance, 0.0),
    )

    _adjust_weight(
        weights=weights,
        key="elevation",
        delta=ELEVATION_ADJUSTMENT_MAP.get(request.elevation_preference, 0.0),
    )

    weights["environment_preference"] = request.environment_preference
    weights["surface_preference"] = request.surface_preference
    weights["target_distance_km"] = request.target_distance_km
    weights["loop"] = request.loop


def _apply_leisure_preferences(weights: dict, request) -> None:
    """
    Aplica regras específicas do modo lazer.
    """
    _set_weight_from_map(
        weights=weights,
        key="difficulty_penalty",
        selected_value=request.difficulty_level,
        mapping=DIFFICULTY_PENALTY_MAP,
    )

    _set_weight_from_map(
        weights=weights,
        key="points_of_interest",
        selected_value=request.points_of_interest_preference,
        mapping=POINTS_OF_INTEREST_MAP,
    )

    _set_weight_from_map(
        weights=weights,
        key="green_area",
        selected_value=request.green_area_preference,
        mapping=GREEN_AREA_MAP,
    )


def _apply_exercise_preferences(weights: dict, request) -> None:
    """
    Aplica regras específicas do modo exercício.
    """
    _adjust_weight(
        weights=weights,
        key="effort",
        delta=INTENSITY_ADJUSTMENT_MAP.get(request.intensity_preference, 0.0),
    )

    if request.training_goal == "queimar_gordura":
        _adjust_weight(weights, "distance_fit", 0.10)
        _adjust_weight(weights, "traffic_avoidance", 0.05)
        _adjust_weight(weights, "elevation", -0.05)

    elif request.training_goal == "ganhar_resistencia":
        _adjust_weight(weights, "distance_fit", 0.15)
        _adjust_weight(weights, "effort", 0.10)

    elif request.training_goal == "trabalhar_musculo":
        _adjust_weight(weights, "elevation", 0.20)
        _adjust_weight(weights, "effort", 0.15)

    elif request.training_goal == "recuperacao_ativa":
        _adjust_weight(weights, "traffic_avoidance", 0.10)
        _adjust_weight(weights, "scenic", 0.05)
        _adjust_weight(weights, "elevation", -0.15)
        weights["difficulty_penalty"] = 0.30

    elif request.training_goal == "treino_misto":
        _adjust_weight(weights, "distance_fit", 0.05)
        _adjust_weight(weights, "effort", 0.05)
        _adjust_weight(weights, "elevation", 0.05)


def _apply_competition_preferences(weights: dict, request) -> None:
    """
    Aplica regras específicas do modo competição.
    """
    _adjust_weight(
        weights=weights,
        key="speed",
        delta=INTENSITY_ADJUSTMENT_MAP.get(request.intensity_preference, 0.0),
    )

    _set_weight_from_map(
        weights=weights,
        key="fluency",
        selected_value=request.route_fluency,
        mapping=ROUTE_FLUENCY_MAP,
    )

    if request.training_goal == "velocidade":
        _adjust_weight(weights, "speed", 0.20)
        _adjust_weight(weights, "fluency", 0.10)

    elif request.training_goal == "ritmo_constante":
        _adjust_weight(weights, "fluency", 0.20)
        _adjust_weight(weights, "traffic_avoidance", 0.05)

    elif request.training_goal == "subida":
        _adjust_weight(weights, "elevation", 0.20)
        _adjust_weight(weights, "speed", 0.05)

    elif request.training_goal == "resistencia_competitiva":
        _adjust_weight(weights, "distance_fit", 0.15)
        _adjust_weight(weights, "fluency", 0.10)

    elif request.training_goal == "simulacao_prova":
        _adjust_weight(weights, "speed", 0.15)
        _adjust_weight(weights, "fluency", 0.15)
        _adjust_weight(weights, "distance_fit", 0.10)


def build_session_profile(request) -> dict:
    """
    Constrói o perfil final da sessão a partir:
    - do modo principal selecionado
    - das preferências transversais
    - das opções avançadas específicas do modo
    """
    weights = deepcopy(PROFILE_WEIGHTS.get(request.profile_type, {}))

    _apply_common_preferences(weights, request)

    if request.profile_type == "lazer":
        _apply_leisure_preferences(weights, request)

    elif request.profile_type == "exercicio":
        _apply_exercise_preferences(weights, request)

    elif request.profile_type == "competicao":
        _apply_competition_preferences(weights, request)

    return weights