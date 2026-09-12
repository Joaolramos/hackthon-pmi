import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { AlertTriangle, Users, TrendingDown, Shield } from 'lucide-react';
import { RatingBadge, RATING_CONFIG, Rating } from '../components/RiskComponents';

// ----------------------------------------------------------------
// Dados mock da carteira (em produção: consumir /api/v1/portfolio)
// ----------------------------------------------------------------

const MOCK_PORTFOLIO = [
  { cnpj: '01.838.723/0001-27', razao_social: 'Cooperativa Agrária Ltda',      rating: 'A', score: 820, ultimo_check: '2025-07-14', red_flags_criticas: 0 },
  { cnpj: '12.345.678/0001-90', razao_social: 'Fazenda São João Agropecuária',  rating: 'B', score: 610, ultimo_check: '2025-07-13', red_flags_criticas: 0 },
  { cnpj: '98.765.432/0001-10', razao_social: 'Agro Cerrado Comércio e Representações', rating: 'B', score: 430, ultimo_check: '2025-07-10', red_flags_criticas: 1 },
  { cnpj: '11.222.333/0001-44', razao_social: 'Produtores Unidos do MT',        rating: 'C', score: 310, ultimo_check: '2025-07-14', red_flags_criticas: 2 },
  { cnpj: '55.666.777/0001-88', razao_social: 'Rural Insumos Goiás S.A.',       rating: 'C', score: 240, ultimo_check: '2025-07-14', red_flags_criticas: 1 },
  { cnpj: '33.444.555/0001-66', razao_social: 'Agroindústria Sertão Verde',     rating: 'D', score: 95,  ultimo_check: '2025-07-14', red_flags_criticas: 3 },
];

const RISK_DISTRIBUTION = [
  { rating: 'A 🟢', count: 1, color: '#16a34a' },
  { rating: 'B 🟡', count: 2, color: '#ca8a04' },
  { rating: 'C 🟠', count: 2, color: '#ea580c' },
  { rating: 'D 🔴', count: 1, color: '#dc2626' },
];

// ----------------------------------------------------------------
// Página da Carteira
// ----------------------------------------------------------------

export const PortfolioPage: React.FC = () => {
  const alertas = MOCK_PORTFOLIO.filter(c => c.rating === 'C' || c.rating === 'D');
  const totalRisco = MOCK_PORTFOLIO.filter(c => c.rating !== 'A').length;

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Carteira Monitorada</h1>
        <p className="text-gray-500 mt-1">
          Early Warning System — monitoramento contínuo de risco da carteira de clientes Krill Tech
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <KpiCard
          icon={<Users size={20} className="text-blue-600" />}
          label="Total de Clientes"
          value={MOCK_PORTFOLIO.length.toString()}
          bg="bg-blue-50"
        />
        <KpiCard
          icon={<AlertTriangle size={20} className="text-orange-500" />}
          label="Alertas Ativos"
          value={alertas.length.toString()}
          bg="bg-orange-50"
          highlight={alertas.length > 0}
        />
        <KpiCard
          icon={<TrendingDown size={20} className="text-red-500" />}
          label="Em Risco"
          value={`${totalRisco}/${MOCK_PORTFOLIO.length}`}
          bg="bg-red-50"
        />
        <KpiCard
          icon={<Shield size={20} className="text-green-600" />}
          label="Rating Verde (A)"
          value={`${MOCK_PORTFOLIO.filter(c => c.rating === 'A').length}`}
          bg="bg-green-50"
        />
      </div>

      {/* Distribuição de risco */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Distribuição de Risco na Carteira</h3>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={RISK_DISTRIBUTION} barCategoryGap="30%">
              <XAxis dataKey="rating" tick={{ fontSize: 12 }} />
              <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
              <Tooltip formatter={(v: number) => [`${v} cliente(s)`, 'Quantidade']} />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {RISK_DISTRIBUTION.map(entry => (
                  <Cell key={entry.rating} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Alertas imediatos */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <AlertTriangle size={16} className="text-orange-500" />
            Alertas Imediatos (C e D)
          </h3>
          {alertas.length === 0 ? (
            <p className="text-gray-400 text-sm">Nenhum alerta ativo.</p>
          ) : (
            <div className="space-y-3">
              {alertas.map(c => (
                <div
                  key={c.cnpj}
                  className="flex items-center justify-between p-3 rounded-lg"
                  style={{ backgroundColor: RATING_CONFIG[c.rating as Rating].bg }}
                >
                  <div>
                    <p className="text-sm font-medium text-gray-800">{c.razao_social}</p>
                    <p className="text-xs text-gray-500">{c.cnpj}</p>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <RatingBadge rating={c.rating as Rating} showLabel={false} size="sm" />
                    <span className="text-xs text-gray-500">{c.score}/1000</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Tabela da carteira completa */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100">
          <h3 className="text-sm font-semibold text-gray-700">Todos os Clientes</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-gray-500 text-xs uppercase tracking-wide">
                <th className="px-6 py-3 text-left">Empresa</th>
                <th className="px-6 py-3 text-left">CNPJ</th>
                <th className="px-6 py-3 text-center">Rating</th>
                <th className="px-6 py-3 text-center">Score</th>
                <th className="px-6 py-3 text-center">Flags Críticas</th>
                <th className="px-6 py-3 text-center">Último Check</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {MOCK_PORTFOLIO.map(client => (
                <tr key={client.cnpj} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-3 font-medium text-gray-800">{client.razao_social}</td>
                  <td className="px-6 py-3 text-gray-500 font-mono text-xs">{client.cnpj}</td>
                  <td className="px-6 py-3 text-center">
                    <RatingBadge rating={client.rating as Rating} showLabel={false} size="sm" />
                  </td>
                  <td className="px-6 py-3 text-center font-semibold">{client.score}</td>
                  <td className="px-6 py-3 text-center">
                    {client.red_flags_criticas > 0 ? (
                      <span className="inline-flex items-center gap-1 text-red-600 font-medium">
                        🚨 {client.red_flags_criticas}
                      </span>
                    ) : (
                      <span className="text-green-600">✓</span>
                    )}
                  </td>
                  <td className="px-6 py-3 text-center text-gray-400 text-xs">{client.ultimo_check}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// ----------------------------------------------------------------
// KPI Card
// ----------------------------------------------------------------

const KpiCard: React.FC<{
  icon: React.ReactNode;
  label: string;
  value: string;
  bg: string;
  highlight?: boolean;
}> = ({ icon, label, value, bg, highlight }) => (
  <div className={`rounded-xl border p-4 ${bg} ${highlight ? 'border-orange-300' : 'border-gray-200'}`}>
    <div className="flex items-center gap-2 mb-2">{icon}<span className="text-xs text-gray-500">{label}</span></div>
    <p className={`text-2xl font-bold ${highlight ? 'text-orange-600' : 'text-gray-800'}`}>{value}</p>
  </div>
);
