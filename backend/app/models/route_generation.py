from typing import Literal, Optional

from pydantic import BaseModel, Field


class RouteGenerationRequest(BaseModel):
    # -------------------------------------------------------------------------
    # Coordenadas base da rota
    # -------------------------------------------------------------------------
    startLat: float = Field(
        ...,
        description="Latitude do ponto de início da rota"
    )
    startLon: float = Field(
        ...,
        description="Longitude do ponto de início da rota"
    )
    endLat: float = Field(
        ...,
        description="Latitude do ponto de fim da rota"
    )
    endLon: float = Field(
        ...,
        description="Longitude do ponto de fim da rota"
    )

    # -------------------------------------------------------------------------
    # Modo principal da rota
    # -------------------------------------------------------------------------
    profile_type: Literal["lazer", "exercicio", "competicao"] = Field(
        ...,
        description="Modo principal da rota: lazer, exercício ou competição"
    )

    # -------------------------------------------------------------------------
    # Estrutura base da rota
    # -------------------------------------------------------------------------
    target_distance_km: Optional[float] = Field(
        default=None,
        ge=0,
        description="Distância desejada em quilómetros"
    )
    loop: bool = Field(
        default=False,
        description="Indica se a rota deve regressar ao ponto inicial"
    )

    # -------------------------------------------------------------------------
    # Preferências transversais (comuns aos 3 modos)
    # -------------------------------------------------------------------------
    elevation_preference: Literal["baixa", "media", "alta"] = Field(
        default="media",
        description="Preferência por subidas e relevo"
    )
    scenic_preference: Literal["baixa", "media", "alta"] = Field(
        default="media",
        description="Preferência por percursos panorâmicos e visualmente agradáveis"
    )
    traffic_avoidance: Literal["baixa", "media", "alta"] = Field(
        default="media",
        description="Nível de prioridade para evitar trânsito"
    )
    environment_preference: Literal["urbana", "rural", "mista"] = Field(
        default="mista",
        description="Preferência pelo tipo de ambiente da rota"
    )
    surface_preference: Literal["asfalto", "asfalto_ecovia", "indiferente"] = Field(
        default="indiferente",
        description="Tipo de piso preferido"
    )

    # -------------------------------------------------------------------------
    # Opções avançadas específicas do modo lazer
    # -------------------------------------------------------------------------
    difficulty_level: Literal["muito_facil", "facil", "moderada"] = Field(
        default="facil",
        description="Nível de dificuldade desejado, especialmente relevante no modo lazer"
    )
    points_of_interest_preference: Literal["baixa", "media", "alta"] = Field(
        default="media",
        description="Preferência por passar por pontos de interesse"
    )
    green_area_preference: Literal["baixa", "media", "alta"] = Field(
        default="media",
        description="Preferência por zonas verdes e natureza"
    )

    # -------------------------------------------------------------------------
    # Opções avançadas específicas dos modos exercício e competição
    # -------------------------------------------------------------------------
    intensity_preference: Literal["baixa", "media", "alta"] = Field(
        default="media",
        description="Intensidade pretendida do treino ou da rota"
    )
    route_fluency: Literal["baixa", "media", "alta"] = Field(
        default="media",
        description="Preferência por rotas com menos interrupções e maior fluidez"
    )

    # -------------------------------------------------------------------------
    # Objetivo específico da sessão
    # -------------------------------------------------------------------------
    training_goal: Optional[
        Literal[
            # Exercício
            "queimar_gordura",
            "ganhar_resistencia",
            "trabalhar_musculo",
            "recuperacao_ativa",
            "treino_misto",
            # Competição
            "velocidade",
            "ritmo_constante",
            "subida",
            "resistencia_competitiva",
            "simulacao_prova",
        ]
    ] = Field(
        default=None,
        description=(
            "Objetivo principal do treino ou da sessão. "
            "Pode ser usado nos modos exercício e competição."
        )
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "startLat": 41.2952,
                    "startLon": -7.7460,
                    "endLat": 41.3005,
                    "endLon": -7.7398,
                    "profile_type": "lazer",
                    "target_distance_km": 12,
                    "loop": True,
                    "elevation_preference": "baixa",
                    "scenic_preference": "alta",
                    "traffic_avoidance": "alta",
                    "environment_preference": "rural",
                    "surface_preference": "asfalto_ecovia",
                    "difficulty_level": "facil",
                    "points_of_interest_preference": "alta",
                    "green_area_preference": "alta",
                    "intensity_preference": "media",
                    "route_fluency": "media",
                    "training_goal": None
                },
                {
                    "startLat": 41.2952,
                    "startLon": -7.7460,
                    "endLat": 41.3400,
                    "endLon": -7.7000,
                    "profile_type": "exercicio",
                    "target_distance_km": 25,
                    "loop": False,
                    "elevation_preference": "alta",
                    "scenic_preference": "baixa",
                    "traffic_avoidance": "media",
                    "environment_preference": "mista",
                    "surface_preference": "asfalto",
                    "difficulty_level": "moderada",
                    "points_of_interest_preference": "baixa",
                    "green_area_preference": "media",
                    "intensity_preference": "alta",
                    "route_fluency": "media",
                    "training_goal": "trabalhar_musculo"
                },
                {
                    "startLat": 41.2952,
                    "startLon": -7.7460,
                    "endLat": 41.3600,
                    "endLon": -7.6800,
                    "profile_type": "competicao",
                    "target_distance_km": 40,
                    "loop": False,
                    "elevation_preference": "media",
                    "scenic_preference": "baixa",
                    "traffic_avoidance": "baixa",
                    "environment_preference": "rural",
                    "surface_preference": "asfalto",
                    "difficulty_level": "moderada",
                    "points_of_interest_preference": "baixa",
                    "green_area_preference": "baixa",
                    "intensity_preference": "alta",
                    "route_fluency": "alta",
                    "training_goal": "velocidade"
                }
            ]
        }
    }