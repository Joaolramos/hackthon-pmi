"""
Coletor de dados cadastrais via ReceitaWS (API pública, sem chave).
Fallback para CNPJA se disponível.

ReceitaWS: https://receitaws.com.br/v1/cnpj/{cnpj}
Limite: ~3 req/min sem chave. Para produção usar CNPJA com chave paga.
"""
import re
import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import get_settings
from ..models.domain import CadastralData

log = structlog.get_logger()
settings = get_settings()


def _clean_cnpj(cnpj: str) -> str:
    """Remove formatação do CNPJ, mantém apenas dígitos."""
    return re.sub(r"\D", "", cnpj)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def fetch_cadastral(cnpj: str) -> CadastralData:
    """
    Consulta dados cadastrais na Receita Federal via ReceitaWS.
    Retorna CadastralData preenchido; em caso de erro retorna objeto com raw_error.
    """
    cnpj_clean = _clean_cnpj(cnpj)
    url = f"{settings.receitaws_base_url}/cnpj/{cnpj_clean}"

    log.info("cadastral.fetch", cnpj=cnpj_clean)

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        if data.get("status") == "ERROR":
            return CadastralData(cnpj=cnpj_clean, raw_error=data.get("message", "CNPJ não encontrado"))

        # Extrai sócios
        socios = [
            {"nome": s.get("nome", ""), "qual": s.get("qual", "")}
            for s in data.get("qsa", [])
        ]

        return CadastralData(
            cnpj=cnpj_clean,
            razao_social=data.get("nome", ""),
            situacao_cadastral=data.get("situacao", ""),
            data_abertura=data.get("abertura", ""),
            cnae_principal=data.get("atividade_principal", [{}])[0].get("code", ""),
            capital_social=_parse_capital(data.get("capital_social", "0")),
            uf=data.get("uf", ""),
            municipio=data.get("municipio", ""),
            socios=socios,
            filiais=len(data.get("filiais", [])),
        )

    except httpx.HTTPStatusError as e:
        log.warning("cadastral.http_error", cnpj=cnpj_clean, status=e.response.status_code)
        return CadastralData(cnpj=cnpj_clean, raw_error=f"HTTP {e.response.status_code}")
    except Exception as e:
        log.error("cadastral.unexpected_error", cnpj=cnpj_clean, error=str(e))
        return CadastralData(cnpj=cnpj_clean, raw_error=str(e))


def _parse_capital(value: str) -> float:
    """Converte string de capital social 'R$ 1.000.000,00' para float."""
    try:
        cleaned = re.sub(r"[R$\s.]", "", value).replace(",", ".")
        return float(cleaned)
    except (ValueError, AttributeError):
        return 0.0
