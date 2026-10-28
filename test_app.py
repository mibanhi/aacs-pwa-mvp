import pytest
from app import app, ESTOQUE_PEPS, mascarar_cpf, validar_cpf

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_validar_cpf_utilitarios():
    assert validar_cpf("123.456.789-00") is True
    assert validar_cpf("12345") is False
    assert mascarar_cpf("12345678900") == "***.456.789-**"

def test_busca_cpf_elegivel(client):
    response = client.post('/atendimentos/busca', data={'cpf': '123.456.789-00'})
    assert response.status_code == 200
    assert b"ASSISTIDO ELEGIVEL PARA BENEFICIO" in response.data

def test_busca_cpf_invalido(client):
    response = client.post('/atendimentos/busca', data={'cpf': '123'})
    assert response.status_code == 400

def test_cadastro_estoque_peps(client):
    novo_lote = {'item': 'Arroz 5kg', 'quantidade': '10', 'validade': '2026-10-30'}
    response = client.post('/estoque/painel-peps', data=novo_lote)
    assert response.status_code == 201
    # Verifica se o lote de validade mais proxima (30/10) ficou em primeiro no PEPS
    assert ESTOQUE_PEPS[0]['validade'] == '2026-10-30'

def test_cadastro_estoque_invalido(client):
    response = client.post('/estoque/painel-peps', data={'item': 'Arroz'})
    assert response.status_code == 400

def test_confirmar_entrega_sucesso(client):
    response = client.post('/atendimentos/confirmar')
    assert response.status_code == 200
    assert b"Entrega confirmada com sucesso" in response.data
