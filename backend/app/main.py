from fastapi import FastAPI, Query
from app.services.routing_service import calculate_route, generate_personalized_route
from app.models.route_generation import RouteGenerationRequest
from app.services.profile_service import get_profile_weights

app = FastAPI()


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
    return calculate_route(startLat, startLon, endLat, endLon)


@app.post("/routes/generate")
def generate_route(request: RouteGenerationRequest):
    profile_weights = get_profile_weights(request.profile_type)
    return generate_personalized_route(request, profile_weights)