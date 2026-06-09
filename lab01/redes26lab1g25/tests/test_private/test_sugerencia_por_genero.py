"""
Tests que debés implementar: sugerencia con filtro por género.
Completar los tests según el contrato de la API.
"""

import pytest
from src.store import CATALOGO_JUEGOS, LISTAS_JUEGOS

def test_sugerencia_con_genero_solo_devuelve_ese_genero(client):
    # TODO: Sugerencia con ?genero=X solo debe devolver juegos de ese género
    user = client.post("/usuarios", json={"nombre": "Ana"})
    assert user.status_code == 201
    
    data = user.get_json()
    assert "id" in data
    
    usuario_id = data["id"]
    
    CATALOGO_JUEGOS["Q1"] = {
        "id": "Q1",
        "nombre": "Juego de Accion",
        "genero": "Accion",
        "descripcion": "Un juego de acción",
        "lanzamiento": "2020",
        "plataforma": "PC"
    }
    
    CATALOGO_JUEGOS["Q2"] = {
        "id": "Q2",
        "nombre": "Juego de Aventura",
        "genero": "Aventura",
        "descripcion": "Un juego de aventura",
        "lanzamiento": "2021",
        "plataforma": "PC"
    }
    
    LISTAS_JUEGOS[usuario_id] = [
        {"juego_id": "Q1", "tengo": True, "quiero": False, "jugado": False, "me_gusta": False},
        {"juego_id": "Q2", "tengo": True, "quiero": False, "jugado": False, "me_gusta": False}
    ]
    
    r = client.get(f"/usuarios/{usuario_id}/sugerencia?genero=Accion")
    assert r.status_code == 200
    
    data2 = r.get_json()
    
    assert data2["genero"] == "Accion"


def test_sugerencia_genero_sin_coincidencias_404(client):
    # TODO: Sin juegos del género pedido debe devolver 404
    user = client.post("/usuarios", json={"nombre": "Carlos"})
    assert user.status_code == 201
    
    usuario_id = user.get_json()["id"]
    
    from src.store import CATALOGO_JUEGOS, LISTAS_JUEGOS
    
    CATALOGO_JUEGOS["Q3"] = {
        "id": "Q3",
        "nombre": "Juego de Aventura",
        "genero": "Aventura",
        "descripcion": "Solo aventura",
        "lanzamiento": "2022",
        "plataforma": "Xbox"
    }
    
    LISTAS_JUEGOS[usuario_id] = [
        {"juego_id": "Q3", "tengo": True, "quiero": False, "jugado": False, "me_gusta": False}
    ]
    
    r = client.get(f"/usuarios/{usuario_id}/sugerencia?genero=Accion")
    
    assert r.status_code == 404
