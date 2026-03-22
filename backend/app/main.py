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
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _build_default_session_profile() -> dict:
    """
    Perfil de sessão mínimo usado no endpoint de rota simples.
    Serve para manter compatibilidade com testes rápidos sem exigir
    todas as preferências avançadas.
    """
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
    """
    Endpoint de verificação do estado da API.
    """
    return {"status": "ok"}


@app.get("/route", tags=["Rotas"])
def route(
    startLat: float = Query(..., description="Latitude do ponto de início"),
    startLon: float = Query(..., description="Longitude do ponto de início"),
    endLat: float = Query(..., description="Latitude do ponto de fim"),
    endLon: float = Query(..., description="Longitude do ponto de fim"),
):
    """
    Calcula uma rota simples entre dois pontos.

    Este endpoint existe para:
    - testes rápidos
    - integração inicial com frontend
    - debug do cálculo base de rotas

    Usa um perfil de sessão neutro e assume o modo lazer como base.
    """
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
    """
    Gera uma rota personalizada com base em:
    - perfil principal
    - distância pretendida
    - preferências de ambiente
    - dificuldade
    - intensidade
    - objetivo da sessão
    - restantes opções avançadas

    O pedido é transformado num `session_profile`,
    que depois influencia diretamente o custo das arestas no cálculo da rota.
    """
    session_profile = build_session_profile(request)
    return generate_personalized_route(request, session_profile)