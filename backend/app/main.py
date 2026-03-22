from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from app.models.route_generation import RouteGenerationRequest
from app.services.profile_service import build_session_profile
from app.services.routing_service import calculate_route, generate_personalized_route

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/route")
def route(
    startLat: float = Query(...),
    startLon: float = Query(...),
    endLat: float = Query(...),
    endLon: float = Query(...),
):
    session_profile = {
        "environment_preference": "mista",
        "surface_preference": "indiferente",
        "green_area": 0.0,
        "points_of_interest": 0.0,
        "difficulty_penalty": 0.0,
    }

    return calculate_route(
        startLat=startLat,
        startLon=startLon,
        endLat=endLat,
        endLon=endLon,
        profile_type="lazer",
        session_profile=session_profile,
    )


@app.post("/routes/generate")
def generate_route(request: RouteGenerationRequest):
    session_profile = build_session_profile(request)
    return generate_personalized_route(request, session_profile)