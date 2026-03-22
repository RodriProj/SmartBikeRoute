from typing import Literal, Optional

from pydantic import BaseModel, Field


class RouteGenerationRequest(BaseModel):
    # Coordenadas de início e fim
    startLat: float = Field(..., description="Latitude do ponto de início")
    startLon: float = Field(..., description="Longitude do ponto de início")
    endLat: float = Field(..., description="Latitude do ponto de fim")
    endLon: float = Field(..., description="Longitude do ponto de fim")

    # Perfil principal de utilização
    profile_type: Literal["lazer", "exercicio", "competicao"] = Field(
        ...,
        description="Modo principal da rota"
    )

    # Estrutura base da rota
    target_distance_km: Optional[float] = Field(
        default=None,
        ge=0,
        description="Distância desejada em quilómetros"
    )
    loop: bool = Field(
        default=False,
        description="Indica se a rota deve regressar ao ponto inicial"
    )

    # Preferências transversais
    elevation_preference: Literal["baixa", "media", "alta"] = Field(
        default="media",
        description="Preferência por subidas"
    )
    scenic_preference: Literal["baixa", "media", "alta"] = Field(
        default="media",
        description="Preferência por percursos panorâmicos"
    )
    traffic_avoidance: Literal["baixa", "media", "alta"] = Field(
        default="media",
        description="Nível de prioridade para evitar trânsito"
    )

    # Opções avançadas do modo lazer
    difficulty_level: Literal["muito_facil", "facil", "moderada"] = Field(
        default="facil",
        description="Nível de dificuldade desejado para a rota"
    )
    points_of_interest_preference: Literal["baixa", "media", "alta"] = Field(
        default="media",
        description="Preferência por passar por pontos de interesse"
    )
    environment_preference: Literal["urbana", "rural", "mista"] = Field(
        default="mista",
        description="Preferência pelo tipo de ambiente da rota"
    )
    surface_preference: Literal["asfalto", "asfalto_ecovia", "indiferente"] = Field(
        default="indiferente",
        description="Tipo de piso preferido"
    )
    green_area_preference: Literal["baixa", "media", "alta"] = Field(
        default="media",
        description="Preferência por zonas verdes e natureza"
    )

    # Objetivos adicionais
    training_goal: Optional[str] = Field(
        default=None,
        description="Objetivo do treino, usado sobretudo nos modos exercício e competição"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
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
                "difficulty_level": "facil",
                "points_of_interest_preference": "alta",
                "environment_preference": "rural",
                "surface_preference": "asfalto_ecovia",
                "green_area_preference": "alta",
                "training_goal": None
            }
        }
    }