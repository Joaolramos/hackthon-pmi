import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({ baseURL: API_BASE, timeout: 60000 });

// ----------------------------------------------------------------
// Tipos espelhando os schemas da API Python
// ----------------------------------------------------------------

export interface ScoreBreakdown {
  cadastral: number;
  juridico: number;
  fiscal: number;
  agro_climate: number;
  total: number;
}

export interface RedFlag {
  codigo: string;
  descricao: string;
  severidade: 'CRITICA' | 'ALTA' | 'MEDIA';
}

export interface AnalyzeResponse {
  cnpj: string;
  razao_social: string;
  score_total: number;
  rating: 'A' | 'B' | 'C' | 'D';
  rating_label: string;
  aprovado: boolean;
  limite_sugerido: number;
  condicoes_pagamento: string;
  prazo_maximo_dias: number;
  exige_garantia: boolean;
  tipo_cobranca: string;
  red_flags: RedFlag[];
  score_breakdown: ScoreBreakdown;
  resumo_executivo: string;
  monitoring_frequency: string;
  analisado_em: string;
}

export interface PortfolioClient {
  cnpj: string;
  razao_social?: string;
  rating?: string;
  score?: number;
  ultimo_check?: string;
  red_flags_criticas?: number;
}

// ----------------------------------------------------------------
// Funções de API
// ----------------------------------------------------------------

export const analyzeClient = async (
  cnpj: string,
  limiteSolicitado?: number
): Promise<AnalyzeResponse> => {
  const { data } = await api.post('/api/v1/analyze', {
    cnpj,
    limite_solicitado: limiteSolicitado || null,
  });
  return data;
};

export const askAgent = async (
  question: string,
  context?: Record<string, unknown>
): Promise<string> => {
  const { data } = await api.post('/api/v1/chat', { question, context });
  return data.answer;
};

export const getRiskLevels = async () => {
  const { data } = await api.get('/api/v1/risk-levels');
  return data.levels;
};

export const healthCheck = async (): Promise<boolean> => {
  try {
    await api.get('/health');
    return true;
  } catch {
    return false;
  }
};
