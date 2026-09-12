"""
Modelos de domínio — estruturas de dados que trafegam entre camadas.
"""
from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# ---------------------------------------------------------------------------
# Enumerações
# ---------------------------------------------------------------------------

class RiskLevel(str, Enum):
    """Farol de risco — mapeado diretamente para o rating exibido no dashboard."""
    GREEN  = "A"   # 700–1000 — Baixo risco
    YELLOW = "B"   # 400–699  — Risco moderado
    ORANGE = "C"   # 200–399  — Risco elevado
    RED    = "D"   # 0–199    — Risco crítico / Alerta de RJ


class MonitoringFrequency(str, Enum):
    """Frequência de reprocessamento automático da carteira."""
    WEEKLY     = "weekly"     # Clientes Amarelo (B) — a cada 7 dias
    BIWEEKLY   = "biweekly"   # Clientes Verde (A)  — a cada 15 dias
    DAILY      = "daily"      # Clientes Laranja/Vermelho — alerta imediato


# ---------------------------------------------------------------------------
# Dados brutos coletados por dimensão
# ---------------------------------------------------------------------------

@dataclass
class CadastralData:
    cnpj: str
    razao_social: str = ""
    situacao_cadastral: str = ""          # ATIVA / SUSPENSA / INAPTA / BAIXADA
    data_abertura: Optional[str] = None
    cnae_principal: str = ""
    capital_social: float = 0.0
    uf: str = ""
    municipio: str = ""
    socios: list[dict] = field(default_factory=list)
    filiais: int = 0
    raw_error: Optional[str] = None       # preenchido quando a consulta falha


@dataclass
class JuridicalData:
    cnpj: str
    total_processos: int = 0
    processos_execucao: int = 0           # execuções de título
    pedidos_rj: int = 0                   # pedidos de recuperação judicial
    distribuicao_falencia: int = 0
    protestos: int = 0
    passivo_trabalhista: bool = False
    raw_error: Optional[str] = None


@dataclass
class FiscalData:
    cnpj: str
    divida_ativa_federal: bool = False
    certidao_positiva_pgfn: bool = False  # True = tem pendência
    cndt_irregular: bool = False          # CNDT = certidão de débitos trabalhistas
    fgts_irregular: bool = False
    raw_error: Optional[str] = None


@dataclass
class EnvironmentalData:
    cnpj: str
    car_numero: Optional[str] = None      # número do CAR da propriedade vinculada
    embargo_ibama: bool = False
    area_preservacao_irregular: bool = False
    municipio_propriedade: str = ""
    uf_propriedade: str = ""
    raw_error: Optional[str] = None


@dataclass
class AgroClimateData:
    municipio: str
    uf: str
    produtividade_media_soja: float = 0.0   # sc/ha — referência CONAB
    produtividade_media_milho: float = 0.0  # sc/ha
    risco_climatico_zarc: str = "MEDIO"     # BAIXO / MEDIO / ALTO
    historico_secas: int = 0                # eventos nos últimos 5 anos (INMET)
    historico_inundacoes: int = 0
    raw_error: Optional[str] = None


# ---------------------------------------------------------------------------
# Score consolidado e red flags
# ---------------------------------------------------------------------------

@dataclass
class RedFlag:
    codigo: str
    descricao: str
    severidade: str   # CRITICA / ALTA / MEDIA


@dataclass
class ScoreBreakdown:
    """Detalhamento do score por dimensão (0–250 cada = total 0–1000)."""
    cadastral:    int = 0   # situação ativa, tempo de atividade, capital social
    juridico:     int = 0   # processos, RJ, protestos
    fiscal:       int = 0   # dívida ativa, certidões
    agro_climate: int = 0   # produtividade, risco climático, embargos

    @property
    def total(self) -> int:
        return self.cadastral + self.juridico + self.fiscal + self.agro_climate

    @property
    def risk_level(self) -> RiskLevel:
        t = self.total
        if t >= 700: return RiskLevel.GREEN
        if t >= 400: return RiskLevel.YELLOW
        if t >= 200: return RiskLevel.ORANGE
        return RiskLevel.RED


@dataclass
class CreditRecommendation:
    """Recomendação gerada pelo motor — o ANALISTA decide se acata."""
    aprovado: bool
    limite_credito_sugerido: float          # R$
    condicoes_pagamento: str                # texto livre gerado pelo LLM
    prazo_maximo_dias: int
    exige_garantia: bool
    tipo_cobranca: str                      # "normal" / "juros_automaticos" / "boleto_antecipado"
    observacoes: str = ""


@dataclass
class RiskReport:
    """Relatório completo de risco — saída final do sistema."""
    cnpj: str
    razao_social: str
    analisado_em: datetime

    # Dados coletados
    cadastral:    CadastralData    = field(default_factory=lambda: CadastralData(""))
    juridico:     JuridicalData    = field(default_factory=lambda: JuridicalData(""))
    fiscal:       FiscalData       = field(default_factory=lambda: FiscalData(""))
    ambiental:    EnvironmentalData= field(default_factory=lambda: EnvironmentalData(""))
    agro_climate: AgroClimateData  = field(default_factory=lambda: AgroClimateData("", ""))

    # Score e decisão
    score: ScoreBreakdown          = field(default_factory=ScoreBreakdown)
    red_flags: list[RedFlag]       = field(default_factory=list)
    recomendacao: Optional[CreditRecommendation] = None

    # Relatório em linguagem natural (gerado pelo LLM)
    resumo_executivo: str = ""
    monitoring_frequency: MonitoringFrequency = MonitoringFrequency.BIWEEKLY
