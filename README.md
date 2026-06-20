# 🎯 Promoções API

API REST para gerenciamento de promoções de e-commerce, com avaliação de descontos, histórico de auditoria e cache de alta performance.

![Python](https://img.shields.io/badge/Python-3.14-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.137-009688)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-336791)
![Redis](https://img.shields.io/badge/Redis-7-DC382D)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)

---

## 📖 Sobre o projeto

Esta API resolve um problema central de e-commerce: **decidir, de forma confiável e auditável, quais promoções se aplicam a um pedido**.

O projeto foi construído **sem ORM** — todo o SQL é escrito à mão, com proteção nativa contra SQL Injection, controle total sobre índices e queries, e migrações versionadas via [Clandestino](https://pypi.org/project/clandestino/).

> 💡 Por que sem ORM? Porque em sistemas que envolvem dinheiro, controle explícito sobre cada query é mais valioso do que a conveniência de um tradutor automático. [Leia mais sobre essa decisão ↓](#-por-que-sem-orm)

---

## 🏗️ Arquitetura

```mermaid
flowchart LR
    Client["🌐 Cliente"] --> API["⚡ FastAPI"]
    API --> Routes["📍 Routes"]
    Routes --> Repo["🗂️ Repository<br/>(SQL puro)"]
    Repo --> Cache{"🔴 Redis<br/>tem cache?"}
    Cache -->|Sim| ReturnCache["✅ Retorna do cache"]
    Cache -->|Não| DB["🐘 PostgreSQL"]
    DB --> SaveCache["💾 Salva no Redis"]
    SaveCache --> ReturnCache
```

**Fluxo de uma requisição:**
1. O cliente chama um endpoint (ex: `GET /v2/promocoes`)
2. A rota delega a lógica pro repositório correspondente
3. O repositório primeiro consulta o Redis — se tiver cache válido, retorna direto
4. Se não tiver, busca no PostgreSQL com SQL parametrizado e atualiza o cache

---

## 🧰 Stack tecnológica

| Camada | Tecnologia | Função |
|---|---|---|
| API | **FastAPI** | Framework web assíncrono |
| Validação | **Pydantic** | Schemas de entrada e saída |
| Banco de dados | **PostgreSQL 18** | Armazenamento relacional |
| Driver | **Psycopg 3** | Conexão assíncrona nativa, sem ORM |
| Cache | **Redis 7** | Cache de promoções ativas |
| Migrações | **Clandestino** | Controle de versão do schema do banco |
| Testes | **Pytest** | Testes automatizados com mocks |

---

## 📂 Estrutura do projeto

promocoes_api/

├── app/

│   ├── main.py                      # Instância FastAPI

│   ├── db_pool.py                   # Conexão PostgreSQL (Psycopg 3 async)

│   ├── redis_client.py              # Conexão Redis

│   ├── repositories/                # SQL puro, isolado da lógica de rota

│   │   ├── promocao_repository.py

│   │   └── audit_log_repository.py

│   ├── routes/                      # Endpoints da API

│   │   ├── promocoes_v2.py

│   │   └── audit_v2.py

│   └── schemas/                     # Validação Pydantic

├── migrations/                      # Migrações versionadas (Clandestino)

├── tests/                           # Testes automatizados (pytest)

├── .env                             # Variáveis de ambiente (não commitar)

├── requirements.txt

└── run.py                           # Entry point

---

## ⚙️ Como rodar localmente

### 1. Pré-requisitos
- Python 3.10+
- PostgreSQL 18 rodando
- Docker (para o Redis)

### 2. Clonar e instalar dependências

```bash
cd promocoes_api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
CLANDESTINO_MIGRATION_REPO=POSTGRES
CLANDESTINO_POSTGRES_CONNECTION_STRING=postgresql://postgres:SUA_SENHA@127.0.0.1:5432/promocoes_db
```

### 4. Subir o Redis via Docker

```bash
docker run -d --name redis-promocoes -p 6379:6379 redis:7-alpine
```

### 5. Rodar as migrações

```bash
./venv/bin/cdt -m
```

### 6. Iniciar a API

```bash
python run.py
```

Documentação interativa disponível em **http://localhost:8000/docs**

---

## 📡 Endpoints

### Promoções

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/v2/promocoes` | Lista promoções ativas (com cache) |
| `POST` | `/v2/promocoes` | Cria uma nova promoção |
| `DELETE` | `/v2/promocoes/{id}` | Desativa uma promoção |
| `POST` | `/v2/promocoes/avaliar` | Calcula descontos aplicáveis a um pedido |
| `POST` | `/v2/promocoes/apply` | Aplica a promoção e registra na auditoria |

### Auditoria

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/v2/audit/history` | Histórico geral de aplicações |
| `GET` | `/v2/audit/history/{promocao_id}` | Histórico de uma promoção específica |

---

## 🗄️ Modelo de dados

```mermaid
erDiagram
    PROMOCOES {
        int id PK
        string nome
        float desconto_pct
        float valor_minimo
        bool ativa
    }
    AUDIT_LOGS {
        int id PK
        int promocao_id FK
        float valor_pedido
        float desconto_aplicado
        float valor_final
        timestamp timestamp
    }
    PROMOCOES ||--o{ AUDIT_LOGS : "gera"
```

Índices criados deliberadamente para otimizar as queries mais frequentes:
- `idx_promocoes_ativa` — acelera o filtro `WHERE ativa = TRUE`
- `idx_audit_logs_timestamp` — acelera a ordenação do histórico
- `idx_audit_logs_promocao_id` — acelera a busca por promoção específica

---

## 🔴 Cache com Redis

```mermaid
sequenceDiagram
    participant C as Cliente
    participant R as Repository
    participant Redis
    participant PG as PostgreSQL

    C->>R: GET /v2/promocoes
    R->>Redis: existe cache?
    alt cache existe
        Redis-->>R: retorna dados
    else cache vazio
        R->>PG: SELECT * FROM promocoes
        PG-->>R: dados
        R->>Redis: salva cache (TTL 5min)
    end
    R-->>C: resposta
```

O cache é **invalidado automaticamente** sempre que uma promoção é criada ou desativada — garantindo que o cliente nunca veja dados desatualizados.

---

## 🧱 Migrações com Clandestino

Em vez de deixar um ORM criar tabelas magicamente, cada mudança no banco é um arquivo Python versionado e rastreável:

```bash
# criar uma nova migração
./venv/bin/cdt -cm nome_da_migracao default

# aplicar migrações pendentes
./venv/bin/cdt -m

# listar migrações
./venv/bin/cdt -lm

# desfazer a última migração
./venv/bin/cdt -rm
```

O Clandestino nunca executa a mesma migração duas vezes — cada uma é registrada numa tabela de controle própria no banco.

---

## 🔐 Segurança contra SQL Injection

Toda query usa parâmetros (`%s`) em vez de concatenação de strings:

```python
# ❌ Vulnerável — nunca fazer isso
query = f"SELECT * FROM promocoes WHERE nome = '{nome}'"

# ✅ Seguro — usado em todo o projeto
await cur.execute(
    "SELECT * FROM promocoes WHERE nome = %s",
    (nome,)
)
```

O Psycopg 3 escapa automaticamente qualquer caractere perigoso, tratando o valor como dado puro — nunca como código SQL executável.

---

## 🧪 Testes

```bash
pytest tests/ -v
```

Os testes usam um banco PostgreSQL isolado (`promocoes_test_db`) e **mockam o Redis**, garantindo testes rápidos e independentes de infraestrutura externa:

```python
@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    mock = AsyncMock()
    mock.get.return_value = None
    monkeypatch.setattr(promo_repo, "redis_client", mock)
```

---

## 🤔 Por que sem ORM?

| | Com ORM | Sem ORM (este projeto) |
|---|---|---|
| Controle do SQL gerado | ❌ Abstraído | ✅ Total |
| Performance em escala | Depende do ORM | Otimizável manualmente |
| Curva de aprendizado | Mais rápida | Exige conhecer SQL |
| Migrações | Geradas automaticamente | Escritas e revisadas manualmente |

Em sistemas onde dados financeiros estão em jogo, a previsibilidade de SQL explícito supera a conveniência de uma camada de tradução automática.

---

## 🚀 Roadmap

- [ ] Containerizar API + PostgreSQL + Redis com Docker Compose
- [ ] Pipeline de CI/CD (GitHub Actions) rodando os testes automaticamente
- [ ] Observabilidade com OpenTelemetry
- [ ] Suporte a cupons exclusivos e campanhas por categoria

---

## 👤 Autor

**Lohran Lira**
🔗 [LinkedIn](https://linkedin.com/in/lohran-lira-) · 💻 [GitHub](https://github.com/Lohran39) · 📧 lohranpaula@gmail.com 
