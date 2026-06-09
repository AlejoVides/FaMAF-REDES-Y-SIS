"""
Tests que debés implementar: casos borde de la lista de juegos.
Contrato: POST con juego_id (id del catálogo). Completar según openapi.yaml.
"""

import pytest


@pytest.fixture
def usuario_id(client):
    r = client.post("/usuarios", json={"nombre": "UsuarioBorde"})
    assert r.status_code == 201
    return r.get_json()["id"]


def test_agregar_juego_falta_campo_obligatorio_400(client, usuario_id):
    # TODO: POST sin un campo obligatorio (ej. juego_id) debe devolver 400
    body = {
        "tengo": True,
        "quiero": False,
        "jugado": False,
        "me_gusta": False,
    }
    r = client.post(f"/usuarios/{usuario_id}/juegos", json=body)
    assert r.status_code == 400

def test_actualizar_juego_id_inexistente_404(client, usuario_id):
    # TODO: PUT /usuarios/<id>/juegos/Q99999 (no en lista) debe devolver 404
    body = {
        "tengo": True,
        "quiero": False,
        "jugado": False,
        "me_gusta": False,
    }
    r = client.put(f"/usuarios/{usuario_id}/juegos/Q99999", json=body)
    assert r.status_code == 404

def test_eliminar_juego_no_en_lista_404(client, usuario_id):
    # TODO: DELETE /usuarios/<id>/juegos/<juego_id> con juego no en la lista debe devolver 404
    r = client.delete(f"/usuarios/{usuario_id}/juegos/Q12312")
    assert r.status_code == 404

def test_agregar_juego_id_inexistente_404(client, usuario_id):
    # TODO: POST con juego_id que no existe en catálogo ni Wikidata debe devolver 404
    body = {
        "juego_id": "QINVALIDO",
        "tengo": True,
        "quiero": False,
        "jugado": False,
        "me_gusta": False,
     }
    r = client.post(f"/usuarios/{usuario_id}/juegos", json=body)
    assert r.status_code == 404

def test_ordenar_por_fecha_lanzamiento(client, usuario_id):
    # TODO: GET juegos con ordenar=fecha_lanzamiento debe devolver ordenado
    # Primero agregamos algunos juegos con diferentes fechas de lanzamiento
    juegos = [
        ("Q12379", True, False, False, False),  # Suponiendo juegos con fechas diferentes
        ("Q23602", False, True, False, False),
        ("Q188953", False, False, True, False),
    ]
    
    for juego_id, tengo, quiero, jugado, me_gusta in juegos:
        body = {
            "juego_id": juego_id,
            "tengo": tengo,
            "quiero": quiero,
            "jugado": jugado,
            "me_gusta": me_gusta,
        }
        r = client.post(f"/usuarios/{usuario_id}/juegos", json=body)
        # Ignoramos si ya existe (409) o si no se encuentra (404)
        assert r.status_code in [201, 404, 409, 502]
    
    # Ahora obtenemos la lista ordenada
    r = client.get(f"/usuarios/{usuario_id}/juegos?ordenar=fecha_lanzamiento")
    assert r.status_code == 200
    
    data = r.get_json()
    # Verificamos que tenga al menos un juego
    if len(data) > 0:
        fechas = [item.get("lanzamiento") or "" for item in data]
        assert fechas == sorted(fechas), f"Fechas no ordenadas: {fechas}"
