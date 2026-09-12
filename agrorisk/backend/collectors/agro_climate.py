"""
Coletor de dados agronômicos e climáticos.

Fontes:
- SICAR (Sistema de Cadastro Ambiental Rural): https://www.car.gov.br/publico/imoveis/index
- IBAMA (embargos): https://servicos.ibama.gov.br/ctf/publico/areasembargadas/ConsultaPublicaAreasEmbargadas.php
- ZARC/MAPA: produtividade e risco climático por município/cultura
- INMET: histórico climático (séries de precipitação)
"""
import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from ..models.domain import EnvironmentalData, AgroClimateData

log = structlog.get_logger()

# Produtividade média por UF — fonte CONAB Safras 2022/2023
# Valores em sc/ha. Em produção consumir API CONAB diretamente.
PRODUTIVIDADE_SOJA_UF: dict[str, float] = {
    "MT": 58.2, "GO": 56.8, "MS": 55.1, "PR": 59.4, "RS": 48.3,
    "MG": 53.7, "BA": 52.0, "TO": 54.5, "PI": 50.8, "MA": 48.9,
    "SP": 55.0, "SC": 55.0,
}

PRODUTIVIDADE_MILHO_UF: dict[str, float] = {
    "MT": 95.0, "GO": 85.0, "MS": 88.0, "PR": 92.0, "RS": 78.0,
    "MG": 80.0, "SP": 88.0, "SC": 85.0, "TO": 78.0, "BA": 70.0,
}

# Risco climático ZARC por UF (simplificado para hackathon)
# Em produção: consumir ZARC via API MAPA por município e cultura
RISCO_ZARC_UF: dict[str, str] = {
    "MT": "BAIXO", "GO": "BAIXO", "PR": "BAIXO", "RS": "MEDIO",
    "MS": "BAIXO", "MG": "MEDIO", "SP": "BAIXO", "SC": "BAIXO",
    "TO": "MEDIO", "BA": "ALTO", "PI": "ALTO", "MA": "MEDIO",
    "CE": "ALTO", "PB": "ALTO", "PE": "ALTO", "RN": "ALTO",
}


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=8))
async def fetch_environmental(cnpj: str, uf: str, municipio: str) -> EnvironmentalData:
    """
    Verifica regularidade ambiental via IBAMA (embargos).
    SICAR integração direta requer API privada — usamos verificação por município.
    """
    cnpj_clean = cnpj.replace(".", "").replace("/", "").replace("-", "")
    log.info("environmental.fetch", cnpj=cnpj_clean, uf=uf, municipio=municipio)

    embargo = await _check_ibama_embargo(cnpj_clean, municipio, uf)

    return EnvironmentalData(
        cnpj=cnpj_clean,
        embargo_ibama=embargo,
        municipio_propriedade=municipio,
        uf_propriedade=uf,
    )


async def _check_ibama_embargo(cnpj: str, municipio: str, uf: str) -> bool:
    """
    Consulta áreas embargadas pelo IBAMA.
    API pública: https://servicos.ibama.gov.br/ctf/publico/areasembargadas/

    NOTA: A API do IBAMA tem instabilidades. Em produção usar
    a base de dados baixada periodicamente do portal dados.gov.br.
    """
    try:
        url = (
            "https://servicos.ibama.gov.br/cnia/embargos/consulta_embargo_cpf_cnpj.php"
            f"?cpf_cnpj={cnpj}"
        )
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                return len(data.get("embargos", [])) > 0
    except Exception as e:
        log.warning("environmental.ibama_error", cnpj=cnpj, error=str(e))
    return False


async def fetch_agro_climate(municipio: str, uf: str) -> AgroClimateData:
    """
    Retorna dados agronômicos e climáticos para o município/UF da propriedade.
    Usa tabelas internas baseadas em CONAB/ZARC para o hackathon.
    Em produção: integrar API CONAB (https://portaldeinformacoes.conab.gov.br)
    e ZARC (https://www.agricultura.gov.br/assuntos/riscos-seguro/risco-agropecuario/zarc).
    """
    uf_upper = uf.upper()

    prod_soja = PRODUTIVIDADE_SOJA_UF.get(uf_upper, 50.0)
    prod_milho = PRODUTIVIDADE_MILHO_UF.get(uf_upper, 75.0)
    risco_zarc = RISCO_ZARC_UF.get(uf_upper, "MEDIO")

    # Histórico climático — simplificado; em produção usar INMET API
    # https://apitempo.inmet.gov.br/INMET_API/
    historico_secas = _estimate_drought_risk(risco_zarc)
    historico_inundacoes = _estimate_flood_risk(uf_upper)

    log.info(
        "agro_climate.fetched",
        municipio=municipio, uf=uf_upper,
        risco_zarc=risco_zarc, prod_soja=prod_soja
    )

    return AgroClimateData(
        municipio=municipio,
        uf=uf_upper,
        produtividade_media_soja=prod_soja,
        produtividade_media_milho=prod_milho,
        risco_climatico_zarc=risco_zarc,
        historico_secas=historico_secas,
        historico_inundacoes=historico_inundacoes,
    )


def _estimate_drought_risk(risco_zarc: str) -> int:
    """Estima eventos de seca nos últimos 5 anos com base no ZARC."""
    return {"BAIXO": 1, "MEDIO": 3, "ALTO": 6}.get(risco_zarc, 3)


def _estimate_flood_risk(uf: str) -> int:
    """Estima eventos de inundação — UFs do Sul têm maior histórico."""
    high_flood = {"RS", "SC", "PR", "SP", "MG"}
    return 3 if uf in high_flood else 1
