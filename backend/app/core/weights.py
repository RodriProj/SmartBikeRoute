"""
Pesos base por perfil.

Estes valores são o ponto de partida; profile_service.py ajusta-os
com base nas preferências do utilizador antes de chegarem ao edge_cost_service.

Os pesos não precisam de somar 1.0 — são usados como valores absolutos
passados ao edge_cost_service como session_profile[key].

Lazer    → segurança, conforto, exploração, baixo esforço
Exercício → equilíbrio distância/esforço/elevação, alguma segurança
Competição → fluidez, velocidade, piso de qualidade, alguma segurança
"""

PROFILE_WEIGHTS: dict = {
    "lazer": {
        # Segurança e conforto têm o maior peso
        "safety": 0.25,
        "traffic_avoidance": 0.20,
        "scenic": 0.20,
        # Exploração e ambiente
        "points_of_interest": 0.15,
        "green_area": 0.10,
        # Menos penalização por dificuldade por defeito (ajustado via difficulty_level)
        "difficulty_penalty": 0.15,
        # Piso e elevação em segundo plano
        "surface": 0.10,
        "elevation": 0.05,
        # Distância como referência (não penaliza percurso)
        "distance_fit": 0.10,
    },
    "exercicio": {
        # Elevação e esforço dominantes
        "elevation": 0.25,
        "effort": 0.20,
        # Distância é importante para treino
        "distance_fit": 0.20,
        # Segurança presente mas não dominante
        "safety": 0.10,
        "traffic_avoidance": 0.10,
        # Piso relevante para treino
        "surface": 0.10,
        # Estética em segundo plano
        "scenic": 0.05,
    },
    "competicao": {
        # Velocidade e fluidez dominantes
        "speed": 0.25,
        "surface": 0.20,
        "fluency": 0.15,
        # Distância como referência
        "distance_fit": 0.15,
        # Elevação estratégica
        "elevation": 0.10,
        # Trânsito aceitável em competição
        "traffic_avoidance": 0.10,
        # Segurança mínima (não deve ser ignorada)
        "safety": 0.05,
        # Estética irrelevante
        "scenic": 0.00,
    },
}
