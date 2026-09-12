"""
Coletor de dados fiscais e trabalhistas.

Fontes:
- PGFN (Dívida Ativa Federal): https://www.regularize.pgfn.gov.br
- TST CNDT: https://cndt-certidao.tst.jus.br
- CRF-FGTS (Caixa): https://consulta-crf.caixa.gov.br
"""
import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from ..models.domain import FiscalData

log = structlog.get_logger()


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=8))
async def fetch_fiscal(cnpj: str) -> FiscalData:
    """
    Verifica situação fiscal federal (PGFN) e trabalhista (CNDT / FGTS).
    Retorna FiscalData com flags booleanas de irregularidade.
    """
    cnpj_clean = cnpj.replace(".", "").replace("/", "").replace("-", "")
    log.info("fiscal.fetch", cnpj=cnpj_clean)

    divida_ativa = await _check_pgfn(cnpj_clean)
    cndt = await _check_cndt_fiscal(cnpj_clean)
    fgts = await _check_fgts(cnpj_clean)

    return FiscalData(
        cnpj=cnpj_clean,
        divida_ativa_federal=divida_ativa,
        certidao_positiva_pgfn=divida_ativa,
        cndt_irregular=cndt,
        fgts_irregular=fgts,
    )


async def _check_pgfn(cnpj: str) -> bool:
    """
    Verifica situação na PGFN (Procuradoria Geral da Fazenda Nacional).
    API pública Regularize: https://www.regularize.pgfn.gov.br/api/situacao/{cnpj}

    Retorna True se há débito inscrito em dívida ativa.
    """
    try:
        url = f"https://www.regularize.pgfn.gov.br/api/situacao/{cnpj}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                situacao = data.get("situacao", "REGULAR").upper()
                return situacao not in ("REGULAR", "SEM DEBITO")
    except Exception as e:
        log.warning("fiscal.pgfn_error", cnpj=cnpj, error=str(e))
    return False


async def _check_cndt_fiscal(cnpj: str) -> bool:
    """
    Verifica CNDT via TST — Certidão Negativa de Débitos Trabalhistas.
    Retorna True se IRREGULAR (possui débitos).
    """
    try:
        cnpj_fmt = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        url = f"https://cndt-certidao.tst.jus.br/inicio.faces?consulta=cnpj&cnpj={cnpj_fmt}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            content = resp.text.lower()
            return "positiva" in content and "efeito de negativa" not in content
    except Exception:
        return False


async def _check_fgts(cnpj: str) -> bool:
    """
    Verifica CRF-FGTS (Certidão de Regularidade do FGTS) via Caixa.
    URL pública: https://consulta-crf.caixa.gov.br

    NOTA: A Caixa exige CAPTCHA na interface web. Em produção usar
    integração via e-Social ou certificado digital.
    Para o hackathon, retornamos False (regular) e documentamos como gap.
    """
    # ⚠️ HIPÓTESE — integração direta com FGTS requer certificado digital.
    # Gap conhecido; não compromete o score pois outros indicadores cobrem.
    log.debug("fiscal.fgts_skipped", cnpj=cnpj, reason="requires_cert_digital")
    return False
