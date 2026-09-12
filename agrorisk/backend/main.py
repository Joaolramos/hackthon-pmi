"""
Ponto de entrada da aplicação FastAPI — AgroRisk Intelligence.
Inicializa API, scheduler de monitoramento e clientes demo.
"""
import uvicorn
import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI

from .api.routes import app as api_app
from .scheduler.monitor import create_scheduler, register_client, add_alert_callback

log = structlog.get_logger()

# ---------------------------------------------------------------------------
# Scheduler lifecycle — inicia/para junto com a aplicação FastAPI
# ---------------------------------------------------------------------------

scheduler = create_scheduler()


def _log_alert(alerta: dict) -> None:
    """Callback padrão: loga alertas no stdout. Em produção: enviar email/webhook."""
    log.warning(
        "ALERTA_CARTEIRA",
        tipo=alerta["tipo"],
        cnpj=alerta["cnpj"],
        mensagem=alerta["mensagem"],
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle hooks — startup e shutdown."""
    log.info("agrorisk.startup", message="Iniciando AgroRisk Intelligence...")

    # Registra callback de alertas
    add_alert_callback(_log_alert)

    # Carrega carteira demo (em produção: carregar do banco de dados)
    _load_demo_portfolio()

    # Inicia scheduler
    scheduler.start()
    log.info("agrorisk.scheduler_started")

    yield   # <-- aplicação em execução

    # Shutdown
    scheduler.shutdown(wait=False)
    log.info("agrorisk.shutdown")


api_app.router.lifespan_context = lifespan


def _load_demo_portfolio():
    """
    Carrega uma carteira demo para demonstração no hackathon.
    CNPJs fictícios/públicos para teste — substituir por dados reais.
    """
    demo_clients = [
        # Grandes cooperativas e empresas reais do agronegócio (CNPJs públicos)
        {"cnpj": "01.838.723/0001-27", "limite": 500_000},   # Cooperativa Agrária
        {"cnpj": "81.659.840/0001-83", "limite": 200_000},   # exemplo MT
    ]
    for c in demo_clients:
        register_client(c["cnpj"], c["limite"])

    log.info("agrorisk.demo_portfolio_loaded", count=len(demo_clients))


if __name__ == "__main__":
    uvicorn.run(
        "agrorisk.backend.main:api_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
