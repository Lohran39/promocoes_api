from fastapi import FastAPI
from app.routes.promocoes_v2 import router as promocoes_v2_router
from app.routes.audit_v2 import router as audit_v2_router

app = FastAPI(
    title="Promoções API",
    description="API para gerenciar promoções e histórico de aplicações",
    version="2.0.0"
)

app.include_router(promocoes_v2_router)
app.include_router(audit_v2_router)


@app.get("/health")
def health():
    return {"status": "OK"}
