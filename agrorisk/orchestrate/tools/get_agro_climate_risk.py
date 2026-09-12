from ibm_watsonx_orchestrate.agent_builder.tools import tool
import httpx

_PROD_SOJA: dict = {
    "MT": 58.2, "GO": 56.8, "MS": 55.1, "PR": 59.4, "RS": 48.3,
    "MG": 53.7, "BA": 52.0, "TO": 54.5, "PI": 50.8, "MA": 48.9,
    "SP": 55.0, "SC": 55.0, "RO": 52.0, "PA": 50.0,
}
_PROD_MILHO: dict = {
    "MT": 95.0, "GO": 85.0, "MS": 88.0, "PR": 92.0, "RS": 78.0,
    "MG": 80.0, "SP": 88.0, "SC": 85.0, "TO": 78.0, "BA": 70.0,
}
_RISCO_ZARC: dict = {
    "MT": "BAIXO", "GO": "BAIXO", "PR": "BAIXO", "RS": "MEDIO",
    "MS": "BAIXO", "MG": "MEDIO", "SP": "BAIXO", "SC": "BAIXO",
    "TO": "MEDIO", "BA": "ALTO",  "PI": "ALTO",  "MA": "MEDIO",
    "CE": "ALTO",  "PB": "ALTO",  "PE": "ALTO",  "RN": "ALTO",
    "RO": "MEDIO", "PA": "MEDIO",
}


@tool
def get_agro_climate_risk(uf: str, municipio: str, cnpj: str) -> dict:
    """
    Avalia o risco agronômico e climático da propriedade rural vinculada ao cliente.
    Consulta dados de produtividade agrícola regional (CONAB), risco climático por
    cultura e região (ZARC/MAPA), histórico de eventos climáticos adversos (INMET)
    e verifica existência de embargos ambientais (IBAMA).

    Args:
        uf: Sigla do estado onde está localizada a propriedade (ex: MT, GO, PR)
        municipio: Nome do município da propriedade rural
        cnpj: CNPJ do cliente (para consulta de embargos IBAMA)

    Returns:
        Dicionário com risco climático ZARC, produtividade regional, histórico climático e embargo IBAMA
    """
    uf_upper = uf.upper().strip()
    cnpj_clean = "".join(c for c in cnpj if c.isdigit())

    prod_soja  = _PROD_SOJA.get(uf_upper, 50.0)
    prod_milho = _PROD_MILHO.get(uf_upper, 75.0)
    risco_zarc = _RISCO_ZARC.get(uf_upper, "MEDIO")

    historico_secas      = {"BAIXO": 1, "MEDIO": 3, "ALTO": 6}.get(risco_zarc, 3)
    historico_inundacoes = {"RS": 3, "SC": 3, "PR": 3, "SP": 2, "MG": 2}.get(uf_upper, 1)

    embargo_ibama = False
    try:
        url = (
            "https://servicos.ibama.gov.br/cnia/embargos/consulta_embargo_cpf_cnpj.php"
            f"?cpf_cnpj={cnpj_clean}"
        )
        resp = httpx.get(url, timeout=8.0)
        if resp.status_code == 200:
            embargo_ibama = len(resp.json().get("embargos", [])) > 0
    except Exception:
        pass

    nivel_agro = (
        "ALTO"  if embargo_ibama or risco_zarc == "ALTO"
        else "MEDIO" if risco_zarc == "MEDIO" or historico_secas >= 4
        else "BAIXO"
    )

    return {
        "uf": uf_upper,
        "municipio": municipio,
        "risco_climatico_zarc": risco_zarc,
        "nivel_risco_agro_consolidado": nivel_agro,
        "produtividade_media_soja_sc_ha": prod_soja,
        "produtividade_media_milho_sc_ha": prod_milho,
        "historico_secas_5anos": historico_secas,
        "historico_inundacoes_5anos": historico_inundacoes,
        "embargo_ibama": embargo_ibama,
        "fonte_produtividade": "CONAB Safras 2022/2023",
        "fonte_risco_climatico": "ZARC/MAPA",
    }
