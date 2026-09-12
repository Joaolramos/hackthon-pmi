import React, { useState } from 'react';
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer, Tooltip } from 'recharts';
import ReactMarkdown from 'react-markdown';
import { Search, AlertTriangle, CheckCircle, XCircle, Clock, Shield } from 'lucide-react';

import { analyzeClient, AnalyzeResponse } from '../services/api';
import {
  RatingBadge,
  ScoreGauge,
  RedFlagItem,
  LoadingSpinner,
  Rating,
} from '../components/RiskComponents';

// ----------------------------------------------------------------
// Página de Análise Individual de Risco
// ----------------------------------------------------------------

export const AnalyzePage: React.FC = () => {
  const [cnpj, setCnpj]     = useState('');
  const [limite, setLimite] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult]  = useState<AnalyzeResponse | null>(null);
  const [error, setError]    = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!cnpj.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await analyzeClient(cnpj.trim(), limite ? parseFloat(limite) : undefined);
      setResult(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Erro ao conectar com a API.';
      setError(`Erro na análise: ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleAnalyze();
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Análise de Risco de Crédito</h1>
        <p className="text-gray-500 mt-1">
          Insira o CNPJ do cliente para análise completa de due diligence automatizada.
        </p>
      </div>

      {/* Formulário de busca */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <div className="flex gap-3 flex-wrap">
          <input
            type="text"
            className="flex-1 min-w-[200px] border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="CNPJ (ex: 12.345.678/0001-90)"
            value={cnpj}
            onChange={e => setCnpj(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <input
            type="number"
            className="w-48 border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Limite solicitado (R$)"
            value={limite}
            onChange={e => setLimite(e.target.value)}
          />
          <button
            onClick={handleAnalyze}
            disabled={loading || !cnpj.trim()}
            className="flex items-center gap-2 bg-blue-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <Search size={16} />
            {loading ? 'Analisando...' : 'Analisar'}
          </button>
        </div>
      </div>

      {/* Estado de carregamento */}
      {loading && (
        <LoadingSpinner message="Consultando Receita Federal, DataJud, PGFN, IBAMA, ZARC... aguarde." />
      )}

      {/* Erro */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      {/* Resultado */}
      {result && <AnalysisResult result={result} />}
    </div>
  );
};

// ----------------------------------------------------------------
// Componente de resultado completo
// ----------------------------------------------------------------

const AnalysisResult: React.FC<{ result: AnalyzeResponse }> = ({ result }) => {
  const radarData = [
    { subject: 'Cadastral',   score: result.score_breakdown.cadastral,   fullMark: 250 },
    { subject: 'Jurídico',    score: result.score_breakdown.juridico,    fullMark: 250 },
    { subject: 'Fiscal',      score: result.score_breakdown.fiscal,      fullMark: 250 },
    { subject: 'Agro/Clima',  score: result.score_breakdown.agro_climate,fullMark: 250 },
  ];

  const ratingKey = result.rating as Rating;
  const dataFormatted = new Date(result.analisado_em).toLocaleString('pt-BR');

  return (
    <div className="space-y-6">
      {/* Card principal — Score + Decisão */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex flex-wrap items-start justify-between gap-6">
          {/* Score Gauge */}
          <div className="flex flex-col items-center gap-2">
            <ScoreGauge score={result.score_total} rating={ratingKey} size={130} />
            <RatingBadge rating={ratingKey} size="lg" />
          </div>

          {/* Info da empresa */}
          <div className="flex-1 min-w-[220px]">
            <h2 className="text-xl font-bold text-gray-900">{result.razao_social}</h2>
            <p className="text-sm text-gray-500 mb-4">CNPJ: {result.cnpj} · Analisado em {dataFormatted}</p>

            {/* Decisão */}
            <div className={`flex items-center gap-2 rounded-lg px-4 py-3 mb-3 ${
              result.aprovado ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
            }`}>
              {result.aprovado
                ? <CheckCircle size={20} />
                : <XCircle size={20} />
              }
              <span className="font-semibold text-sm">
                {result.aprovado ? 'APROVADO — condições sugeridas abaixo' : 'NÃO RECOMENDADO pelo sistema'}
              </span>
            </div>
            <p className="text-xs text-gray-400">
              ⚠️ A decisão final é sempre do analista de crédito responsável.
            </p>
          </div>

          {/* Condições de crédito */}
          <div className="bg-gray-50 rounded-lg p-4 min-w-[200px]">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
              Condições Sugeridas
            </h3>
            <div className="space-y-2">
              <MetaRow label="Limite sugerido" value={`R$ ${result.limite_sugerido.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`} />
              <MetaRow label="Prazo máximo"    value={`${result.prazo_maximo_dias} dias`} />
              <MetaRow label="Cobrança"        value={result.tipo_cobranca.replace('_', ' ')} />
              <MetaRow label="Garantia exigida" value={result.exige_garantia ? 'Sim' : 'Não'} />
              <MetaRow label="Monitoramento"   value={result.monitoring_frequency} />
            </div>
          </div>
        </div>
      </div>

      {/* Breakdown do score — radar */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Score por Dimensão</h3>
          <ResponsiveContainer width="100%" height={220}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="subject" tick={{ fontSize: 12 }} />
              <Tooltip formatter={(v: number) => [`${v}/250`, 'Pontos']} />
              <Radar
                name="Score"
                dataKey="score"
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.3}
              />
            </RadarChart>
          </ResponsiveContainer>
          {/* Legenda numérica */}
          <div className="grid grid-cols-2 gap-2 mt-2">
            {radarData.map(d => (
              <div key={d.subject} className="flex justify-between text-xs text-gray-600 bg-gray-50 rounded px-2 py-1">
                <span>{d.subject}</span>
                <span className="font-semibold">{d.score}/250</span>
              </div>
            ))}
          </div>
        </div>

        {/* Condições de pagamento detalhadas */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Shield size={16} className="text-blue-500" />
            Condições de Pagamento
          </h3>
          <p className="text-sm text-gray-700 leading-relaxed">{result.condicoes_pagamento}</p>
          <div className="mt-4 flex items-center gap-2 text-xs text-gray-500">
            <Clock size={14} />
            <span>Próximo monitoramento: {result.monitoring_frequency}</span>
          </div>
        </div>
      </div>

      {/* Red Flags */}
      {result.red_flags.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <AlertTriangle size={16} className="text-orange-500" />
            Red Flags Identificadas ({result.red_flags.length})
          </h3>
          {result.red_flags.map(flag => (
            <RedFlagItem key={flag.codigo} {...flag} />
          ))}
        </div>
      )}

      {/* Resumo executivo (LLM) */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">
          📋 Resumo Executivo — gerado por IBM watsonx Granite
        </h3>
        <div className="prose prose-sm max-w-none text-gray-700">
          <ReactMarkdown>{result.resumo_executivo}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
};

// ----------------------------------------------------------------
// Helper interno
// ----------------------------------------------------------------

const MetaRow: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="flex justify-between items-center text-sm">
    <span className="text-gray-500">{label}</span>
    <span className="font-medium text-gray-800">{value}</span>
  </div>
);
