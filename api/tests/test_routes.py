import pytest
from fastapi.testclient import TestClient
import os
import json
from main import app  # Importa la app desde tu archivo principal

client = TestClient(app)

# Función para cargar el JSON desde la carpeta "example_payloads"
def load_payload(file_name):
    path = os.path.join(os.path.dirname(__file__), "..", "example_payloads", file_name)
    with open(path, 'r') as file:
        return json.load(file)

# Test para el payload 1
def test_production_plan_payload_1():
    payload = load_payload("payload1.json")
    response = client.post("/productionplan", json=payload)
    assert response.status_code == 200
    response_json = response.json()
    assert "powerplants" in response_json
    # Aquí puedes hacer más validaciones sobre los datos retornados

# Test para el payload 2
def test_production_plan_payload_2():
    payload = load_payload("payload2.json")
    response = client.post("/productionplan", json=payload)
    assert response.status_code == 200
    response_json = response.json()
    assert "powerplants" in response_json

# Test para el payload 3
def test_production_plan_payload_3():
    payload = load_payload("payload3.json")
    response = client.post("/productionplan", json=payload)
    assert response.status_code == 200
    response_json = response.json()
    assert "powerplants" in response_json

def test_production_plan_payload_4():
    payload = load_payload("payload3.json")
    response = client.post("/productionplan", json=payload)
    assert response.status_code == 200
    response_json = response.json()
    assert "powerplants" in response_json

def test_production_plan_payload_5():
    payload = load_payload("payload3.json")
    response = client.post("/productionplan", json=payload)
    assert response.status_code == 200
    response_json = response.json()
    assert "powerplants" in response_json