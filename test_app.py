import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_pagina_inicial(client):
    """Testa se a página inicial carrega com sucesso (HTTP 200)"""
    response = client.get('/')
    assert response.status_code == 200

def test_busca_cpf_valido_elegivel(client):
    """Testa busca com CPF da Maria (Elegível)"""
    response = client.post('/atendimentos/busca', data={'cpf': '123.456.789-00'})
    assert response.status_code == 200
    assert b'ASSISTIDO ELEGIVEL' in response.data or b'Maria Oliveira' in response.data

def test_busca_cpf_invalido(client):
    """Testa busca com CPF em formato incorreto"""
    response = client.post('/atendimentos/busca', data={'cpf': '123'})
    assert response.status_code == 200
    assert b'CPF' in response.data

def test_painel_estoque(client):
    """Testa se a página do estoque carrega corretamente"""
    response = client.get('/estoque')
    assert response.status_code == 200
