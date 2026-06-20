def test_avaliar_promocao_aplicavel(client):
    """Testa se o cálculo de desconto está correto quando a promoção se aplica."""
    client.post("/v2/promocoes", json={
        "nome": "Black Friday",
        "desconto_pct": 10.0,
        "valor_minimo": 300.0
    })

    resposta = client.post("/v2/promocoes/avaliar?valor_pedido=500")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados[0]["desconto"] == 50.0
    assert dados[0]["valor_final"] == 450.0


def test_avaliar_promocao_nao_aplicavel(client):
    """Testa quando o valor do pedido não atinge o mínimo."""
    client.post("/v2/promocoes", json={
        "nome": "Black Friday",
        "desconto_pct": 10.0,
        "valor_minimo": 300.0
    })

    resposta = client.post("/v2/promocoes/avaliar?valor_pedido=100")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados == {"mensagem": "Nenhuma promoção aplicável"}
