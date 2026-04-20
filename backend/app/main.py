from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from app.models.route_generation import RouteGenerationRequest
from app.services.profile_service import build_session_profile
from app.services.routing_service import calculate_route, generate_personalized_route

app = FastAPI(
    title="SmartBike Routes API",
    description="API para geração de rotas cicláveis personalizadas por perfil e preferências do utilizador.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _build_default_session_profile() -> dict:
    return {
        "environment_preference": "mista",
        "surface_preference": "indiferente",
        "green_area": 0.0,
        "points_of_interest": 0.0,
        "difficulty_penalty": 0.0,
        "effort": 0.0,
        "speed": 0.0,
        "fluency": 0.0,
    }


@app.get("/health", tags=["Sistema"])
def health():
    """Endpoint de verificação do estado da API."""
    return {"status": "ok"}


@app.get("/route", tags=["Rotas"])
def route(
    startLat: float = Query(..., description="Latitude do ponto de início"),
    startLon: float = Query(..., description="Longitude do ponto de início"),
    endLat: float = Query(..., description="Latitude do ponto de fim"),
    endLon: float = Query(..., description="Longitude do ponto de fim"),
):
    """Calcula uma rota simples entre dois pontos."""
    session_profile = _build_default_session_profile()
    return calculate_route(
        startLat=startLat,
        startLon=startLon,
        endLat=endLat,
        endLon=endLon,
        profile_type="lazer",
        session_profile=session_profile,
    )


@app.post("/routes/generate", tags=["Rotas"])
def generate_route(request: RouteGenerationRequest):
    """Gera uma rota personalizada com base no perfil e preferências."""
    session_profile = build_session_profile(request)
    return generate_personalized_route(request, session_profile)
