"""
Sistema de Monitoramento Contínuo da Carteira — Early Warning System

Lógica de frequência (definida pela equipe):
  🟢 Verde (A)    → Quinzenal (a cada 15 dias)
  🟡 Amarelo (B)  → Semanal   (a cada 7 dias)
  🟠 Laranja (C)  → Diário    (alerta imediato)
  🔴 Vermelho (D) → Diário    (alerta imediato)

O scheduler roda em background junto com o FastAPI.
Em produção: persistir carteira em PostgreSQL e usar Celery + Redis para jobs distribuídos.
Para o hackathon: APScheduler in-memory demonstra a lógica completa.
"""
import asyncio
import structlog
from datetime import datetime
from typing import Callable
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from ..agents.risk_agent import analyze_client
from ..models.domain import RiskLevel, MonitoringFrequency

log = structlog.get_logger()

# ---------------------------------------------------------------------------
# Carteira monitorada (em produção: banco de dados)
# ---------------------------------------------------------------------------

# Estrutura: {cnpj: {"rating": "B", "ultimo_check": datetime, "limite_solicitado": float}}
_portfolio: dict[str, dict] = {}

# Callbacks de alerta (em produção: webhook, email, Slack)
_alert_callbacks: list[Callable] = []


def register_client(cnpj: str, limite_solicitado: float = None) -> None:
    """Adiciona um cliente à carteira monitorada."""
    clean = cnpj.replace(".", "").replace("/", "").replace("-", "")
    _portfolio[clean] = {
        "cnpj": clean,
        "rating": None,               # será preenchido na próxima análise
        "ultimo_check": None,
        "limite_solicitado": limite_solicitado,
        "adicionado_em": datetime.now().isoformat(),
    }
    log.info("portfolio.client_registered", cnpj=clean)


def get_portfolio() -> list[dict]:
    """Retorna o estado atual da carteira."""
    return list(_portfolio.values())


def add_alert_callback(callback: Callable) -> None:
    """Registra função a ser chamada quando um alerta é gerado."""
    _alert_callbacks.append(callback)


# ---------------------------------------------------------------------------
# Lógica de verificação de alertas
# ---------------------------------------------------------------------------

async def _check_client(cnpj: str) -> None:
    """
    Reanálise de um cliente da carteira.
    Dispara alertas se o rating piorar ou se red flags críticas surgirem.
    """
    entry = _portfolio.get(cnpj)
    if not entry:
        return

    log.info("monitoring.check_client", cnpj=cnpj)

    try:
        report = await analyze_client(cnpj, entry.get("limite_solicitado"))
        novo_rating = report.score.risk_level.value
        rating_anterior = entry.get("rating")

        # Atualiza estado
        _portfolio[cnpj].update({
            "rating": novo_rating,
            "score": report.score.total,
            "ultimo_check": datetime.now().isoformat(),
            "razao_social": report.razao_social,
            "red_flags_count": len(report.red_flags),
            "red_flags_criticas": sum(1 for f in report.red_flags if f.severidade == "CRITICA"),
        })

        # Verifica piora de rating
        _check_rating_degradation(cnpj, rating_anterior, novo_rating, report)

    except Exception as e:
        log.error("monitoring.check_error", cnpj=cnpj, error=str(e))


def _check_rating_degradation(
    cnpj: str,
    rating_anterior: str,
    novo_rating: str,
    report
) -> None:
    """
    Dispara alerta se o rating piorou ou se há red flags críticas novas.
    Ordem de gravidade: A < B < C < D
    """
    ordem = {"A": 1, "B": 2, "C": 3, "D": 4}
    anterior_val = ordem.get(rating_anterior, 0)
    novo_val = ordem.get(novo_rating, 0)

    flags_criticas = [f for f in report.red_flags if f.severidade == "CRITICA"]

    if novo_val > anterior_val:
        alerta = {
            "tipo": "RATING_DEGRADADO",
            "cnpj": cnpj,
            "razao_social": report.razao_social,
            "rating_anterior": rating_anterior,
            "rating_novo": novo_rating,
            "score": report.score.total,
            "red_flags": [f.descricao for f in flags_criticas],
            "timestamp": datetime.now().isoformat(),
            "mensagem": (
                f"⚠️ ALERTA: {report.razao_social} (CNPJ {cnpj}) "
                f"teve rating alterado de {rating_anterior} para {novo_rating}. "
                f"Score atual: {report.score.total}/1000."
            ),
        }
        log.warning("monitoring.rating_degraded", **alerta)
        _dispatch_alert(alerta)

    elif flags_criticas and rating_anterior == novo_rating:
        alerta = {
            "tipo": "RED_FLAG_CRITICA",
            "cnpj": cnpj,
            "razao_social": report.razao_social,
            "rating": novo_rating,
            "red_flags": [f.descricao for f in flags_criticas],
            "timestamp": datetime.now().isoformat(),
            "mensagem": (
                f"🚨 RED FLAG: {report.razao_social} — "
                f"{len(flags_criticas)} alerta(s) crítico(s) identificado(s)."
            ),
        }
        log.warning("monitoring.red_flag", **alerta)
        _dispatch_alert(alerta)


def _dispatch_alert(alerta: dict) -> None:
    """Envia o alerta para todos os callbacks registrados."""
    for callback in _alert_callbacks:
        try:
            callback(alerta)
        except Exception as e:
            log.error("monitoring.callback_error", error=str(e))


# ---------------------------------------------------------------------------
# Jobs agendados por frequência
# ---------------------------------------------------------------------------

async def _run_green_checks():
    """Job quinzenal — clientes Verde (A)."""
    clients = [c for c in _portfolio.values() if c.get("rating") == "A"]
    log.info("monitoring.job_green", count=len(clients))
    for c in clients:
        await _check_client(c["cnpj"])
        await asyncio.sleep(2)  # throttle entre consultas


async def _run_yellow_checks():
    """Job semanal — clientes Amarelo (B)."""
    clients = [c for c in _portfolio.values() if c.get("rating") == "B"]
    log.info("monitoring.job_yellow", count=len(clients))
    for c in clients:
        await _check_client(c["cnpj"])
        await asyncio.sleep(2)


async def _run_critical_checks():
    """Job diário — clientes Laranja (C) e Vermelho (D) — alerta imediato."""
    clients = [c for c in _portfolio.values() if c.get("rating") in ("C", "D")]
    log.info("monitoring.job_critical", count=len(clients))
    for c in clients:
        await _check_client(c["cnpj"])
        await asyncio.sleep(1)


async def _run_initial_checks():
    """Analisa clientes sem rating ainda (recém adicionados)."""
    clients = [c for c in _portfolio.values() if c.get("rating") is None]
    log.info("monitoring.job_initial", count=len(clients))
    for c in clients:
        await _check_client(c["cnpj"])
        await asyncio.sleep(2)


# ---------------------------------------------------------------------------
# Inicialização do scheduler
# ---------------------------------------------------------------------------

def create_scheduler() -> AsyncIOScheduler:
    """
    Cria e configura o scheduler APScheduler com todos os jobs de monitoramento.
    Chame start() depois de montar o scheduler.
    """
    scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")

    # Clientes recém-adicionados (sem rating): verifica a cada 5 minutos
    scheduler.add_job(
        _run_initial_checks,
        trigger=IntervalTrigger(minutes=5),
        id="initial_checks",
        name="Análise inicial de novos clientes",
        replace_existing=True,
    )

    # Clientes Verde (A): quinzenal
    scheduler.add_job(
        _run_green_checks,
        trigger=IntervalTrigger(days=15),
        id="green_checks",
        name="Monitoramento quinzenal — Verde (A)",
        replace_existing=True,
    )

    # Clientes Amarelo (B): semanal
    scheduler.add_job(
        _run_yellow_checks,
        trigger=IntervalTrigger(weeks=1),
        id="yellow_checks",
        name="Monitoramento semanal — Amarelo (B)",
        replace_existing=True,
    )

    # Clientes Laranja/Vermelho: diário
    scheduler.add_job(
        _run_critical_checks,
        trigger=IntervalTrigger(days=1),
        id="critical_checks",
        name="Monitoramento diário — Laranja (C) e Vermelho (D)",
        replace_existing=True,
    )

    return scheduler
