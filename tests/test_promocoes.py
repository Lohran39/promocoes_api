def test_criar_promocao(client):
    """Testa se uma promoção é criada corretamente."""
    resposta = client.post("/v2/promocoes", json={
        "nome": "Black Friday",
        "desconto_pct": 10.0,
        "valor_minimo": 300.0
    })
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["nome"] == "Black Friday"
    assert dados["ativa"] is True


def test_listar_promocoes(client):
    """Testa se a lista retorna as promoções criadas."""
    client.post("/v2/promocoes", json={
        "nome": "Natal",
        "desconto_pct": 15.0,
        "valor_minimo": 200.0
    })

    resposta = client.get("/v2/promocoes")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert len(dados) == 1
    assert dados[0]["nome"] == "Natal"


def test_deletar_promocao(client):
    """Testa se uma promoção é desativada corretamente."""
    criada = client.post("/v2/promocoes", json={
        "nome": "Ano Novo",
        "desconto_pct": 20.0,
        "valor_minimo": 100.0
    }).json()

    resposta = client.delete(f"/v2/promocoes/{criada['id']}")
    assert resposta.status_code == 200

    listagem = client.get("/v2/promocoes").json()
    assert len(listagem) == 0


def test_deletar_promocao_inexistente(client):
    """Testa erro ao deletar promoção que não existe."""
    resposta = client.delete("/v2/promocoes/9999")
    assert resposta.status_code == 404
