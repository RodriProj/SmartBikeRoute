from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


ExerciseGoal = Literal[
    "queimar_gordura",
    "ganhar_resistencia",
    "trabalhar_musculo",
    "recuperacao_ativa",
    "treino_misto",
]

CompetitionGoal = Literal[
    "velocidade",
    "ritmo_constante",
    "subida",
    "resistencia_competitiva",
    "simulacao_prova",
]

_EXERCISE_GOALS = {"queimar_gordura", "ganhar_resistencia", "trabalhar_musculo", "recuperacao_ativa", "treino_misto"}
_COMPETITION_GOALS = {"velocidade", "ritmo_constante", "subida", "resistencia_competitiva", "simulacao_prova"}


class RouteGenerationRequest(BaseModel):
    # Coordenadas base da rota
    startLat: float = Field(..., ge=-90, le=90, description="Latitude do ponto de início")
    startLon: float = Field(..., ge=-180, le=180, description="Longitude do ponto de início")
    endLat: float = Field(..., ge=-90, le=90, description="Latitude do ponto de fim")
    endLon: float = Field(..., ge=-180, le=180, description="Longitude do ponto de fim")

    # Modo principal da rota
    profile_type: Literal["lazer", "exercicio", "competicao"] = Field(
        ..., description="Perfil da rota: lazer, exercício ou competição"
    )

    # Estrutura base da rota
    target_distance_km: Optional[float] = Field(
        default=None, ge=0.5, le=300, description="Distância desejada em km (0.5–300)"
    )
    loop: bool = Field(default=False, description="Rota circular — termina no ponto de início")

    # Preferências comuns aos 3 perfis
    elevation_preference: Literal["baixa", "media", "alta"] = Field(default="media")
    scenic_preference: Literal["baixa", "media", "alta"] = Field(default="media")
    traffic_avoidance: Literal["baixa", "media", "alta"] = Field(default="media")
    environment_preference: Literal["urbana", "rural", "mista"] = Field(default="mista")
    surface_preference: Literal["asfalto", "asfalto_ecovia", "indiferente"] = Field(default="indiferente")

    # Opções específicas do perfil lazer
    difficulty_level: Literal["muito_facil", "facil", "moderada"] = Field(default="facil")
    points_of_interest_preference: Literal["baixa", "media", "alta"] = Field(default="media")
    green_area_preference: Literal["baixa", "media", "alta"] = Field(default="media")

    # Opções específicas dos perfis exercício e competição
    intensity_preference: Literal["baixa", "media", "alta"] = Field(default="media")
    route_fluency: Literal["baixa", "media", "alta"] = Field(default="media")

    # Objetivo específico da sessão
    training_goal: Optional[
        Literal[
            "queimar_gordura",
            "ganhar_resistencia",
            "trabalhar_musculo",
            "recuperacao_ativa",
            "treino_misto",
            "velocidade",
            "ritmo_constante",
            "subida",
            "resistencia_competitiva",
            "simulacao_prova",
        ]
    ] = Field(default=None)

    @model_validator(mode="after")
    def validate_training_goal_coherence(self) -> "RouteGenerationRequest":
        goal = self.training_goal
        if goal is None:
            return self
        if self.profile_type == "lazer" and goal in _EXERCISE_GOALS | _COMPETITION_GOALS:
            raise ValueError(
                f"O objetivo '{goal}' não é compatível com o perfil 'lazer'."
            )
        if self.profile_type == "exercicio" and goal in _COMPETITION_GOALS:
            raise ValueError(
                f"O objetivo '{goal}' é exclusivo do perfil 'competicao'. "
                "Para exercício usa: queimar_gordura, ganhar_resistencia, trabalhar_musculo, recuperacao_ativa, treino_misto."
            )
        if self.profile_type == "competicao" and goal in _EXERCISE_GOALS:
            raise ValueError(
                f"O objetivo '{goal}' é exclusivo do perfil 'exercicio'. "
                "Para competição usa: velocidade, ritmo_constante, subida, resistencia_competitiva, simulacao_prova."
            )
        return self

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "startLat": 41.2952, "startLon": -7.7460,
                    "endLat": 41.3005, "endLon": -7.7398,
                    "profile_type": "lazer",
                    "target_distance_km": 12, "loop": True,
                    "elevation_preference": "baixa", "scenic_preference": "alta",
                    "traffic_avoidance": "alta", "environment_preference": "rural",
                    "surface_preference": "asfalto_ecovia", "difficulty_level": "facil",
                    "points_of_interest_preference": "alta", "green_area_preference": "alta",
                    "intensity_preference": "media", "route_fluency": "media", "training_goal": None,
                },
                {
                    "startLat": 41.2952, "startLon": -7.7460,
                    "endLat": 41.3400, "endLon": -7.7000,
                    "profile_type": "exercicio",
                    "target_distance_km": 25, "loop": False,
                    "elevation_preference": "alta", "scenic_preference": "baixa",
                    "traffic_avoidance": "media", "environment_preference": "mista",
                    "surface_preference": "asfalto", "difficulty_level": "moderada",
                    "points_of_interest_preference": "baixa", "green_area_preference": "media",
                    "intensity_preference": "alta", "route_fluency": "media",
                    "training_goal": "trabalhar_musculo",
                },
                {
                    "startLat": 41.2952, "startLon": -7.7460,
                    "endLat": 41.3600, "endLon": -7.6800,
                    "profile_type": "competicao",
                    "target_distance_km": 40, "loop": False,
                    "elevation_preference": "media", "scenic_preference": "baixa",
                    "traffic_avoidance": "baixa", "environment_preference": "rural",
                    "surface_preference": "asfalto", "difficulty_level": "moderada",
                    "points_of_interest_preference": "baixa", "green_area_preference": "baixa",
                    "intensity_preference": "alta", "route_fluency": "alta",
                    "training_goal": "velocidade",
                },
            ]
        }
    }
