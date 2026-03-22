from copy import deepcopy
from app.core.weights import PROFILE_WEIGHTS


def build_session_profile(request):
    weights = deepcopy(PROFILE_WEIGHTS.get(request.profile_type, {}))

    if request.scenic_preference == "alta":
        weights["scenic"] = weights.get("scenic", 0) + 0.10
    elif request.scenic_preference == "baixa":
        weights["scenic"] = max(0, weights.get("scenic", 0) - 0.10)

    if request.traffic_avoidance == "alta":
        weights["traffic_avoidance"] = weights.get("traffic_avoidance", 0) + 0.10
    elif request.traffic_avoidance == "baixa":
        weights["traffic_avoidance"] = max(0, weights.get("traffic_avoidance", 0) - 0.10)

    if request.elevation_preference == "alta":
        weights["elevation"] = weights.get("elevation", 0) + 0.10
    elif request.elevation_preference == "baixa":
        weights["elevation"] = max(0, weights.get("elevation", 0) - 0.10)

    if request.training_goal == "muscle_gain":
        weights["elevation"] = weights.get("elevation", 0) + 0.15
        weights["effort"] = weights.get("effort", 0) + 0.10

    return weights