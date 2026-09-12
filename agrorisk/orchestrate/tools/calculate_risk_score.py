from ibm_watsonx_orchestrate.agent_builder.tools import tool
from datetime import datetime


@tool
def calculate_risk_score(company_data: dict) -> dict:
    """
    Calcula o score de risco de crédito 0 a 1000 de uma empresa do agronegócio
    com base nos dados coletados pela ferramenta fetch_company_risk_data.
    Divide o score em 4 dimensões: Cadastral, Jurídico, Fiscal e Agro/Climático.
    Classifica o resultado no farol de risco: A (Verde), B (Amarelo), C (Laranja) ou D (Vermelho).
    Identifica e lista os principais red flags de risco.

    Args:
        company_data: Dicionário retornado por fetch_company_risk_data com dados da empresa

    Returns:
        Dicionário com score total, breakdown por dimensão, rating (A/B/C/D), label do farol e lista de red flags
    """
    cadastral = company_data.get("cadastral", {})
    juridico  = company_data.get("juridico", {})
    fiscal    = company_data.get("fiscal", {})
    agro      = company_data.get("agro_climate", {})

    red_flags = []

    # ----------------------------------------------------------------
    # DIMENSÃO 1 — CADASTRAL (0–250)
    # ----------------------------------------------------------------
    s_cad = 0

    situacao = (cadastral.get("situacao") or "").upper()
    if situacao == "ATIVA":
        s_cad += 100
    elif situacao in ("SUSPENSA", "INAPTA"):
        s_cad += 20
        red_flags.append({"severidade": "ALTA", "codigo": "CAD001",
                          "descricao": f"Situação cadastral irregular: {situacao}"})
    elif situacao == "BAIXADA":
        red_flags.append({"severidade": "CRITICA", "codigo": "CAD002",
                          "descricao": "CNPJ baixado — empresa inativa"})
    else:
        s_cad += 60

    data_abertura = cadastral.get("data_abertura", "")
    anos = 0.0
    if data_abertura:
        try:
            abertura = datetime.strptime(data_abertura, "%d/%m/%Y")
            anos = (datetime.now() - abertura).days / 365.25
        except ValueError:
            pass
    if anos >= 10:
        s_cad += 60
    elif anos >= 5:
        s_cad += 45
    elif anos >= 2:
        s_cad += 25
    elif anos >= 1:
        s_cad += 10
    else:
        red_flags.append({"severidade": "MEDIA", "codigo": "CAD003",
                          "descricao": f"Empresa com menos de 1 ano de atividade ({anos:.1f} anos)"})

    capital = float(cadastral.get("capital_social") or 0)
    if capital >= 1_000_000:
        s_cad += 60
    elif capital >= 500_000:
        s_cad += 45
    elif capital >= 100_000:
        s_cad += 30
    elif capital >= 10_000:
        s_cad += 15
    else:
        s_cad += 5
        if capital < 1_000:
            red_flags.append({"severidade": "MEDIA", "codigo": "CAD004",
                              "descricao": f"Capital social muito baixo: R$ {capital:,.2f}"})

    cnae = cadastral.get("cnae_principal", "")
    if cnae.startswith(("01", "02", "03", "46.1", "46.2")):
        s_cad += 30

    s_cad = min(s_cad, 250)

    # ----------------------------------------------------------------
    # DIMENSÃO 2 — JURÍDICO (0–250)
    # ----------------------------------------------------------------
    s_jur = 250

    pedidos_rj = int(juridico.get("pedidos_recuperacao_judicial") or 0)
    falencias  = int(juridico.get("pedidos_falencia") or 0)
    execucoes  = int(juridico.get("processos_execucao") or 0)

    if pedidos_rj > 0:
        s_jur -= 200
        red_flags.append({"severidade": "CRITICA", "codigo": "JUR001",
                          "descricao": f"Pedido(s) de Recuperação Judicial: {pedidos_rj}"})
    if falencias > 0:
        s_jur -= 200
        red_flags.append({"severidade": "CRITICA", "codigo": "JUR002",
                          "descricao": f"Pedido(s) de falência: {falencias}"})
    if execucoes >= 5:
        s_jur -= 80
        red_flags.append({"severidade": "ALTA", "codigo": "JUR003",
                          "descricao": f"Alto volume de execuções: {execucoes}"})
    elif execucoes >= 2:
        s_jur -= 40
        red_flags.append({"severidade": "ALTA", "codigo": "JUR004",
                          "descricao": f"Execuções em andamento: {execucoes}"})
    elif execucoes == 1:
        s_jur -= 15

    s_jur = max(s_jur, 0)

    # ----------------------------------------------------------------
    # DIMENSÃO 3 — FISCAL (0–250)
    # ----------------------------------------------------------------
    s_fis = 250

    if fiscal.get("divida_ativa_federal"):
        s_fis -= 100
        red_flags.append({"severidade": "CRITICA", "codigo": "FIS001",
                          "descricao": "Débito inscrito em dívida ativa federal (PGFN)"})

    s_fis = max(s_fis, 0)

    # ----------------------------------------------------------------
    # DIMENSÃO 4 — AGRO/CLIMÁTICO (0–250)
    # ----------------------------------------------------------------
    s_agro = 0

    if agro.get("embargo_ibama"):
        red_flags.append({"severidade": "CRITICA", "codigo": "AMB001",
                          "descricao": "Área embargada pelo IBAMA — propriedade com restrição legal"})
    else:
        s_agro += 100

    risco_zarc = (agro.get("risco_climatico_zarc") or "MEDIO").upper()
    s_agro += {"BAIXO": 80, "MEDIO": 50, "ALTO": 20}.get(risco_zarc, 50)
    if risco_zarc == "ALTO":
        red_flags.append({"severidade": "ALTA", "codigo": "AMB002",
                          "descricao": f"Alto risco climático ZARC: {agro.get('uf', '')}"})

    prod_soja = float(agro.get("produtividade_media_soja_sc_ha") or 50.0)
    if prod_soja >= 58:
        s_agro += 40
    elif prod_soja >= 52:
        s_agro += 28
    elif prod_soja >= 45:
        s_agro += 15
    else:
        s_agro += 5
        red_flags.append({"severidade": "MEDIA", "codigo": "AMB003",
                          "descricao": f"Produtividade regional baixa: {prod_soja:.1f} sc/ha"})

    eventos = int(agro.get("historico_secas_5anos") or 0) + int(agro.get("historico_inundacoes_5anos") or 0)
    s_agro += 30 if eventos <= 2 else 15 if eventos <= 5 else 0

    if not agro:
        s_agro = 125  # neutro quando sem dados agro

    s_agro = min(s_agro, 250)

    # ----------------------------------------------------------------
    # TOTAL E RATING
    # ----------------------------------------------------------------
    total = s_cad + s_jur + s_fis + s_agro

    if total >= 700:
        rating, rating_label, monitoring = "A", "🟢 Verde — Baixo Risco", "Quinzenal"
    elif total >= 400:
        rating, rating_label, monitoring = "B", "🟡 Amarelo — Risco Moderado", "Semanal"
    elif total >= 200:
        rating, rating_label, monitoring = "C", "🟠 Laranja — Risco Elevado", "Diário"
    else:
        rating, rating_label, monitoring = "D", "🔴 Vermelho — Risco Crítico", "Diário"

    ordem = {"CRITICA": 0, "ALTA": 1, "MEDIA": 2}
    red_flags.sort(key=lambda f: ordem.get(f["severidade"], 9))

    return {
        "cnpj": company_data.get("cnpj", ""),
        "razao_social": company_data.get("cadastral", {}).get("razao_social", ""),
        "score_total": total,
        "rating": rating,
        "rating_label": rating_label,
        "monitoring_frequency": monitoring,
        "score_breakdown": {
            "cadastral": s_cad,
            "juridico": s_jur,
            "fiscal": s_fis,
            "agro_climate": s_agro,
        },
        "red_flags": red_flags,
        "total_red_flags": len(red_flags),
        "flags_criticas": sum(1 for f in red_flags if f["severidade"] == "CRITICA"),
    }
