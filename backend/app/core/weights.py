"""
Pesos base dos perfis de rota.

Cada modo de utilização define uma distribuição inicial de prioridades
que será depois ajustada pelo `profile_service.py` com base nas
preferências avançadas do utilizador.
"""

PROFILE_WEIGHTS = {
    "lazer": {
        # Adequação da rota à distância pretendida
        "distance_fit": 0.15,

        # Segurança e conforto
        "safety": 0.25,
        "traffic_avoidance": 0.20,
        "surface": 0.10,

        # Qualidade da experiência
        "scenic": 0.25,
        "elevation": 0.05,

        # Campos adicionais usados na personalização avançada
        "points_of_interest": 0.10,
        "green_area": 0.10,
        "difficulty_penalty": 0.15,
    },

    "exercicio": {
        # Objetivo físico e adequação ao treino
        "distance_fit": 0.20,
        "effort": 0.20,
        "elevation": 0.25,

        # Controlo de conforto e segurança
        "safety": 0.10,
        "traffic_avoidance": 0.10,
        "surface": 0.10,

        # Aspetos secundários
        "scenic": 0.05,
    },

    "competicao": {
        # Performance
        "distance_fit": 0.15,
        "speed": 0.25,
        "fluency": 0.15,
        "elevation": 0.10,

        # Qualidade do piso e segurança mínima
        "surface": 0.20,
        "safety": 0.05,
        "traffic_avoidance": 0.10,

        # Aspeto visual com prioridade muito baixa
        "scenic": 0.00,
    }
}