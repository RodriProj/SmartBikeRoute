from copy import deepcopy
from app.core.weights import PROFILE_WEIGHTS


def build_session_profile(request):
    weights = deepcopy(PROFILE_WEIGHTS.get(request.profile_type, {}))

    # Scenic
    if request.scenic_preference == "alta":
        weights["scenic"] = weights.get("scenic", 0) + 0.15
    elif request.scenic_preference == "baixa":
        weights["scenic"] = max(0, weights.get("scenic", 0) - 0.10)

    # Tráfego
    if request.traffic_avoidance == "alta":
        weights["traffic_avoidance"] = weights.get("traffic_avoidance", 0) + 0.20
    elif request.traffic_avoidance == "baixa":
        weights["traffic_avoidance"] = max(0, weights.get("traffic_avoidance", 0) - 0.10)

    # Subidas
    if request.elevation_preference == "alta":
        weights["elevation"] = weights.get("elevation", 0) + 0.15
    elif request.elevation_preference == "baixa":
        weights["elevation"] = max(0, weights.get("elevation", 0) - 0.15)

    # Dificuldade
    if request.difficulty_level == "muito_facil":
        weights["difficulty_penalty"] = 0.30
    elif request.difficulty_level == "facil":
        weights["difficulty_penalty"] = 0.15
    else:
        weights["difficulty_penalty"] = 0.05

    # Pontos de interesse
    if request.points_of_interest_preference == "alta":
        weights["points_of_interest"] = 0.25
    elif request.points_of_interest_preference == "media":
        weights["points_of_interest"] = 0.15
    else:
        weights["points_of_interest"] = 0.05

    # Ambiente
    weights["environment_preference"] = request.environment_preference

    # Piso
    weights["surface_preference"] = request.surface_preference

    # Zonas verdes
    if request.green_area_preference == "alta":
        weights["green_area"] = 0.20
    elif request.green_area_preference == "media":
        weights["green_area"] = 0.10
    else:
        weights["green_area"] = 0.0

    return weights