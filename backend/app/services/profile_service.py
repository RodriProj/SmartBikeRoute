from app.core.weights import PROFILE_WEIGHTS


def get_profile_weights(profile_type: str):
    return PROFILE_WEIGHTS.get(profile_type, {})