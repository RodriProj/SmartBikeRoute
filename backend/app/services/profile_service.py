from copy import deepcopy

from app.core.weights import PROFILE_WEIGHTS


PREFERENCE_BONUS_MAP = {
    "baixa": -0.10,
    "media": 0.00,
    "alta": 0.10,
}

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
    current_value = weights.get(key, 0)
    weights[key] = max(0, current_value + delta)


def _set_weight_from_map(weights: dict, key: str, selected_value: str, mapping: dict) -> None:
    """
    Define diretamente um peso/penalização com base num mapa de valores.
    """
    weights[key] = mapping.get(selected_value, weights.get(key, 0))


def build_session_profile(request) -> dict:
    """
    Constrói o perfil final da sessão a partir do perfil base selecionado
    pelo utilizador e das preferências avançadas do pedido.
    """
    weights = deepcopy(PROFILE_WEIGHTS.get(request.profile_type, {}))

    # Ajustes principais de preferência
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

    # Preferências específicas do modo lazer
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

    # Preferências categóricas que serão usadas mais tarde na lógica de custo
    weights["environment_preference"] = request.environment_preference
    weights["surface_preference"] = request.surface_preference

    # Regras adicionais por objetivo de treino
    if request.training_goal == "muscle_gain":
        _adjust_weight(weights, "elevation", 0.15)
        _adjust_weight(weights, "effort", 0.10)

    return weights