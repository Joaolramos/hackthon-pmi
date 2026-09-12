from ibm_watsonx_orchestrate.agent_builder.tools import tool
import httpx
import re


def _clean_cnpj(cnpj: str) -> str:
    return re.sub(r"\D", "", cnpj)


def _fmt_cnpj(cnpj: str) -> str:
    c = _clean_cnpj(cnpj)
    return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}" if len(c) == 14 else c


@tool
def fetch_company_risk_data(cnpj: str) -> dict:
    """
    Realiza due diligence automatizada de uma empresa do agronegócio a partir do CNPJ.
    Consulta Receita Federal (dados cadastrais), DataJud/CNJ (processos judiciais e
    pedidos de Recuperação Judicial) e PGFN (dívida ativa federal).
    Retorna um dicionário consolidado com todos os dados de risco coletados.

    Args:
        cnpj: CNPJ da empresa a ser analisada (com ou sem formatação)

    Returns:
        Dicionário com dados cadastrais, jurídicos e fiscais da empresa
    """
    cnpj_clean = _clean_cnpj(cnpj)

    result = {
        "cnpj": cnpj_clean,
        "cnpj_formatado": _fmt_cnpj(cnpj_clean),
        "cadastral": {},
        "juridico": {},
        "fiscal": {},
        "erros": [],
    }

    # --- 1. CADASTRAL — ReceitaWS ---
    try:
        resp = httpx.get(f"https://receitaws.com.br/v1/cnpj/{cnpj_clean}", timeout=15.0)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") != "ERROR":
                socios = [s.get("nome", "") for s in data.get("qsa", [])]
                capital_raw = re.sub(r"[R$\s.]", "", data.get("capital_social", "0")).replace(",", ".")
                try:
                    capital = float(capital_raw)
                except ValueError:
                    capital = 0.0
                result["cadastral"] = {
                    "razao_social": data.get("nome", ""),
                    "situacao": data.get("situacao", ""),
                    "data_abertura": data.get("abertura", ""),
                    "cnae_principal": (data.get("atividade_principal") or [{}])[0].get("code", ""),
                    "capital_social": capital,
                    "uf": data.get("uf", ""),
                    "municipio": data.get("municipio", ""),
                    "socios": socios,
                    "numero_socios": len(socios),
                }
            else:
                result["erros"].append(f"Cadastral: {data.get('message', 'CNPJ não encontrado')}")
        else:
            result["erros"].append(f"Cadastral HTTP {resp.status_code}")
    except Exception as e:
        result["erros"].append(f"Cadastral: {str(e)}")

    # --- 2. JURÍDICO — DataJud (CNJ) tribunais agro ---
    tribunais = ["tjmt", "tjgo", "tjsp", "tjmg", "tjpr", "tjrs", "tjms", "trf1", "trf4"]
    total_proc = execucoes = pedidos_rj = falencias = 0
    classes_criticas = {"Recuperação Judicial", "Falência", "Recuperação Extrajudicial"}
    classes_exec = {"Execução de Título Extrajudicial", "Execução Fiscal", "Ação de Execução"}

    for tribunal in tribunais:
        try:
            url = f"https://api-publica.datajud.cnj.jus.br/api_publica_{tribunal}/_search"
            payload = {
                "size": 20,
                "query": {"bool": {"should": [{"match": {"partes.cpfCnpj": cnpj_clean}}]}},
                "_source": ["classe.nome", "dataAjuizamento"],
            }
            resp = httpx.post(url, json=payload, timeout=10.0)
            if resp.status_code == 200:
                for hit in resp.json().get("hits", {}).get("hits", []):
                    classe = hit.get("_source", {}).get("classe", {}).get("nome", "")
                    total_proc += 1
                    if classe in classes_criticas:
                        pedidos_rj += 1 if "Recuperação" in classe else 0
                        falencias  += 1 if "Falência" in classe else 0
                    elif classe in classes_exec:
                        execucoes += 1
        except Exception:
            continue

    result["juridico"] = {
        "total_processos": total_proc,
        "processos_execucao": execucoes,
        "pedidos_recuperacao_judicial": pedidos_rj,
        "pedidos_falencia": falencias,
        "risco_rj_detectado": pedidos_rj > 0,
    }

    # --- 3. FISCAL — PGFN ---
    divida_ativa = False
    try:
        resp = httpx.get(
            f"https://www.regularize.pgfn.gov.br/api/situacao/{cnpj_clean}",
            timeout=10.0,
        )
        if resp.status_code == 200:
            situacao = resp.json().get("situacao", "REGULAR").upper()
            divida_ativa = situacao not in ("REGULAR", "SEM DEBITO")
    except Exception:
        pass

    result["fiscal"] = {
        "divida_ativa_federal": divida_ativa,
        "certidao_pgfn_irregular": divida_ativa,
    }

    return result
