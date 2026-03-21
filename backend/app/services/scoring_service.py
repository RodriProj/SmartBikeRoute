def get_speed_by_profile(profile_type: str) -> int:
    speed_kmh_by_profile = {
        "lazer": 12,
        "exercicio": 20,
        "competicao": 28
    }
    return speed_kmh_by_profile.get(profile_type, 15)


def calculate_estimated_time(distance_km: float, profile_type: str):
    if distance_km <= 0:
        return None

    speed_kmh = get_speed_by_profile(profile_type)
    return round((distance_km / speed_kmh) * 60)


def calculate_distance_difference(actual_distance_km: float, target_distance_km):
    if target_distance_km is None:
        return None

    return round(actual_distance_km - target_distance_km, 2)