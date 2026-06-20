# promocoes_api

API FastAPI para gerenciar promoções e histórico de aplicações.

## Estrutura do Projeto

```
promocoes_api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Instância FastAPI e configuração
│   ├── database.py             # Conexão PostgreSQL
│   ├── models/                 # Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── promocao.py
│   │   └── audit_log.py
│   ├── schemas/                # Schemas Pydantic
│   │   ├── __init__.py
│   │   ├── promocao.py
│   │   └── audit_log.py
│   └── routes/                 # Routers FastAPI
│       ├── __init__.py
│       ├── promocoes.py        # Endpoints de promoção
│       └── audit.py            # Endpoints de auditoria
├── venv/
├── requirements.txt
├── run.py                      # Entry point
└── README.md
```

## Pré-requisitos
- PostgreSQL rodando (host: 127.0.0.1, porta: 5432, banco: `promocoes_db`)
- Python 3.10+

## Setup rápido (macOS / Linux)

```bash
cd promocoes_api
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Rodar a aplicação

```bash
source venv/bin/activate
python run.py
```

Ou com uvicorn direto:
```bash
source venv/bin/activate
python -m uvicorn app.main:app --reload
```

Acesse a documentação interativa em: http://localhost:8000/docs

## Endpoints

### Promoções (`/promocoes`)
- `POST /promocoes` — Criar nova promoção
- `GET /promocoes` — Listar promoções ativas
- `DELETE /promocoes/{id}` — Desativar promoção
- `POST /promocoes/avaliar?valor_pedido=100` — Avaliar promoções aplicáveis
- `POST /promocoes/apply` — Aplicar promoção e registrar auditoria

### Auditoria (`/audit`)
- `GET /audit/history?limite=10` — Histórico de aplicações

## Banco de Dados

Credenciais padrão em `app/database.py`:
```
Host: 127.0.0.1
Porta: 5432
Usuário: postgres
Senha: lh39
Banco: promocoes_db
```

Para criar o banco:
```bash
createdb -U postgres promocoes_db
```
