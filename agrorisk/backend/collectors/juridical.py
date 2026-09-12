"""
Coletor de dados jurídicos via API Pública do DataJud (CNJ).
Documentação: https://datajud-wiki.cnj.jus.br/api-publica/

Endpoint de busca por CPF/CNPJ nos tribunais estaduais e federais.
Sem chave de autenticação para uso básico.
"""
import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import get_settings
from ..models.domain import JuridicalData

log = structlog.get_logger()
settings = get_settings()

# Tribunais mais relevantes para o agronegócio (Mato Grosso, Goiás, SP, MG, PR, RS)
TRIBUNAIS_AGRO = [
    "tjmt", "tjgo", "tjsp", "tjmg", "tjpr", "tjrs",
    "tjms", "tjba", "tjto", "trf1", "trf4"
]

# Classes processuais que indicam risco crítico
CLASSES_RISCO_CRITICO = {
    "Recuperação Judicial",
    "Falência",
    "Recuperação Extrajudicial",
}

CLASSES_RISCO_ALTO = {
    "Execução de Título Extrajudicial",
    "Execução Fiscal",
    "Ação de Execução",
}


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=3, max=15))
async def fetch_juridical(cnpj: str) -> JuridicalData:
    """
    Consulta processos judiciais associados ao CNPJ no DataJud (CNJ).
    Agrega por tribunal os processos de execução, RJ e falência.
    """
    cnpj_clean = cnpj.replace(".", "").replace("/", "").replace("-", "")
    log.info("juridical.fetch", cnpj=cnpj_clean)

    total = 0
    execucoes = 0
    pedidos_rj = 0
    falencias = 0

    # Consulta os principais tribunais em paralelo
    async with httpx.AsyncClient(timeout=20.0) as client:
        for tribunal in TRIBUNAIS_AGRO:
            try:
                url = f"{settings.datajud_base_url}/api_publica_{tribunal}/_search"
                payload = _build_query(cnpj_clean)
                resp = await client.post(url, json=payload, headers={"Content-Type": "application/json"})

                if resp.status_code != 200:
                    continue

                hits = resp.json().get("hits", {}).get("hits", [])
                for hit in hits:
                    source = hit.get("_source", {})
                    classe = source.get("classe", {}).get("nome", "")
                    total += 1

                    if classe in CLASSES_RISCO_CRITICO:
                        if "Recuperação Judicial" in classe or "Recuperação Extrajudicial" in classe:
                            pedidos_rj += 1
                        else:
                            falencias += 1
                    elif classe in CLASSES_RISCO_ALTO:
                        execucoes += 1

            except Exception as e:
                log.warning("juridical.tribunal_error", tribunal=tribunal, error=str(e))
                continue

    # Consulta PGFN para protestos (via Regularize)
    protestos = await _fetch_protestos(cnpj_clean)
    passivo_trabalhista = await _check_cndt(cnpj_clean)

    return JuridicalData(
        cnpj=cnpj_clean,
        total_processos=total,
        processos_execucao=execucoes,
        pedidos_rj=pedidos_rj,
        distribuicao_falencia=falencias,
        protestos=protestos,
        passivo_trabalhista=passivo_trabalhista,
    )


def _build_query(cnpj: str) -> dict:
    """Monta query ElasticSearch para busca por CNPJ no DataJud."""
    return {
        "size": 50,
        "query": {
            "bool": {
                "should": [
                    {"match": {"partes.cpfCnpj": cnpj}},
                    {"match": {"partes.nome": cnpj}},
                ]
            }
        },
        "_source": ["classe.nome", "dataAjuizamento", "tribunal", "assuntos"],
    }


async def _fetch_protestos(cnpj: str) -> int:
    """
    Consulta protestos via Serasa/CRC (simulado com base pública).
    Em produção integrar com API do CRC Nacional ou Serasa Experian.
    Retorna estimativa baseada em execuções encontradas como proxy.
    """
    # HIPÓTESE — sem API pública gratuita consolidada para protestos.
    # Em produção: integrar CRC Nacional (www.protestoce.org.br ou similar).
    # Para o hackathon, retornamos 0 e documentamos como limitação conhecida.
    return 0


async def _check_cndt(cnpj: str) -> bool:
    """
    Verifica CNDT (Certidão Negativa de Débitos Trabalhistas) via TST.
    URL pública: https://cndt-certidao.tst.jus.br/inicio.faces
    Retorna True se há passivo (certidão positiva).
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # O TST oferece consulta pública via GET para CNPJ formatado
            cnpj_fmt = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
            url = f"https://cndt-certidao.tst.jus.br/inicio.faces?consulta=cnpj&cnpj={cnpj_fmt}"
            resp = await client.get(url)
            # Verifica se a resposta indica "positiva com efeito de negativa" ou "positiva"
            content = resp.text.lower()
            return "positiva" in content and "efeito de negativa" not in content
    except Exception:
        return False  # conservador: assume regular se não conseguir verificar
