from fastapi.testclient import TestClient

from app.main import app, registros


client = TestClient(app)


def setup_function() -> None:
    # Evita interferência entre testes ao limpar o estado em memória.
    registros.clear()


def test_criar_registro_com_sucesso() -> None:
    response = client.post(
        "/registro-foco",
        json={
            "nivel_foco": 5,
            "tempo_minutos": 50,
            "comentario": "Implementei uma feature nova.",
            "categoria": "coding",
            "tags": ["backend", "api"],
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["registro"]["nivel_foco"] == 5
    assert body["registro"]["tempo_minutos"] == 50


def test_rejeita_nivel_foco_invalido() -> None:
    response = client.post(
        "/registro-foco",
        json={"nivel_foco": 7, "tempo_minutos": 30, "comentario": "Teste inválido"},
    )
    assert response.status_code == 422


def test_diagnostico_com_registros() -> None:
    # Cria dois blocos para validar média, soma de tempo e contagem.
    client.post(
        "/registro-foco",
        json={
            "nivel_foco": 4,
            "tempo_minutos": 60,
            "comentario": "Sessão de estudo.",
            "categoria": "estudo",
        },
    )
    client.post(
        "/registro-foco",
        json={
            "nivel_foco": 2,
            "tempo_minutos": 40,
            "comentario": "Muitas distrações com notificações.",
            "categoria": "outros",
        },
    )

    response = client.get("/diagnostico-produtividade")
    assert response.status_code == 200
    body = response.json()
    assert body["media_nivel_foco"] == 3.0
    assert body["tempo_total_focado_minutos"] == 100
    assert body["total_registros"] == 2


def test_diagnostico_sem_registros() -> None:
    response = client.get("/diagnostico-produtividade")
    assert response.status_code == 404
