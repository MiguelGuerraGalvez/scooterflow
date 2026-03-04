from fastapi.testclient import TestClient
from app.main import app
from app.models import Zona, Patinete

# Creamos el cliente de pruebas
client = TestClient(app)

def test_main():
    '''Test que prueba que la ruta principal responda correctamente'''
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "bienvenida": "¡Bienvenid@ a Scooter Flow!",
        "mensaje": "Para poder ver todas las acciones "
        "que puedes realizar, accede a /docs"
    }

def test_crea_zona():
    '''Test que prueba que una zona se crea correctamente'''
    # Creamos los datos de prueba
    payload = {
        "nombre": "Centro",
        "codigo_postal": 41710,
        "limite_velocidad": 40
    }
    response = client.post("/zonas/create", json=payload)

    # Verificamos la respuesta
    assert response.status_code in [200, 201]
    data = response.json()

    # Comprobamos que nos devuelve el id y el nombre
    assert data["nombre"] == "Centro"
    assert "id" in data
    assert isinstance(data["id"], int)

def test_crea_patinete():
    '''Test que prueba que un patinete se crea correctamente vinculado a una zona'''
    # Creamos los datos de prueba
    zona = client.post("/zonas/create", json={
        "nombre": "Norte",
        "codigo_postal": 41710,
        "limite_velocidad": 50
    })
    payload = {
        "numero_serie": 7,
        "modelo": "smartGyro Rockway GT",
        "bateria": 14,
        "estado": "disponible",
        "puntuacion_usuario": 7,
        "zona_id": zona.json()["id"]
    }
    response = client.post("/patinetes/", json=payload)

    # Verificamos la respuesta
    assert response.status_code in [200, 201]
    data = response.json()

    # Comprobamos que nos devuelve el id y el modelo
    assert data["modelo"] == "smartGyro Rockway GT"
    assert "id" in data
    assert  isinstance(data["id"], int)

def test_validacion_bateria():
    '''Test que prueba que la bateria no puede ser menor a 0 ni mayor a 100'''
    # Creamos los datos de prueba
    zona = client.post("/zonas/create", json={
        "nombre": "Sur",
        "codigo_postal": 41710,
        "limite_velocidad": 50
    })
    payload = {
        "numero_serie": 8,
        "modelo": "SEGWAY GT3 Pro",
        "bateria": 150,
        "estado": "disponible",
        "puntuacion_usuario": 0,
        "zona_id": zona.json()["id"]
    }
    response = client.post("/patinetes/", json=payload)

    # Verificamos la respuesta
    assert response.status_code == 422
    print("\n Confirmado: La API no crea patinetes con más de 100% de batería")

def test_paso_mantenimiento():
    '''
    Test que prueba que los patinetes con menos del 15% de bateria de una zona concreta
    su estado cambia a "mantenimiento"
    '''
    # Creamos los datos de prueba
    zona = client.post("/zonas/create", json={
        "nombre": "Este",
        "codigo_postal": 41710,
        "limite_velocidad": 50
    })

    id_zona = zona.json()["id"]

    patinete = client.post("/patinetes/", json={
      "numero_serie": 14,
      "modelo": "Ninebot MAX G3 E",
      "bateria": 14,
      "estado": "disponible",
      "puntuacion_usuario": 7,
      "zona_id": id_zona
    })

    response = client.post(f"/zonas/{id_zona}/mantenimiento")

    # Verificamos la respuesta
    assert response.status_code == 200
    data = response.json()

    # Comprobamos que el estado cambia a mantenimiento
    assert patinete.json()["estado"] != data[0]["estado"]
    assert data[0]["estado"] == "mantenimiento"
