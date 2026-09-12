import React from 'react';

// Configuração de cores e labels por rating
export const RATING_CONFIG = {
  A: {
    label: 'Verde — Baixo Risco',
    emoji: '🟢',
    color: '#16a34a',
    bg: '#dcfce7',
    border: '#bbf7d0',
    textColor: '#14532d',
    scoreRange: '700–1000',
    monitoring: 'Quinzenal',
  },
  B: {
    label: 'Amarelo — Risco Moderado',
    emoji: '🟡',
    color: '#ca8a04',
    bg: '#fef9c3',
    border: '#fde047',
    textColor: '#713f12',
    scoreRange: '400–699',
    monitoring: 'Semanal',
  },
  C: {
    label: 'Laranja — Risco Elevado',
    emoji: '🟠',
    color: '#ea580c',
    bg: '#ffedd5',
    border: '#fdba74',
    textColor: '#7c2d12',
    scoreRange: '200–399',
    monitoring: 'Diário',
  },
  D: {
    label: 'Vermelho — Risco Crítico',
    emoji: '🔴',
    color: '#dc2626',
    bg: '#fee2e2',
    border: '#fca5a5',
    textColor: '#7f1d1d',
    scoreRange: '0–199',
    monitoring: 'Diário',
  },
} as const;

export type Rating = keyof typeof RATING_CONFIG;

// ----------------------------------------------------------------
// RatingBadge — exibe o farol colorido
// ----------------------------------------------------------------

interface RatingBadgeProps {
  rating: Rating;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export const RatingBadge: React.FC<RatingBadgeProps> = ({
  rating,
  showLabel = true,
  size = 'md',
}) => {
  const cfg = RATING_CONFIG[rating];
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-2 font-semibold',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-medium ${sizeClasses[size]}`}
      style={{
        backgroundColor: cfg.bg,
        color: cfg.textColor,
        border: `1px solid ${cfg.border}`,
      }}
    >
      <span>{cfg.emoji}</span>
      {showLabel && <span>Rating {rating} — {cfg.label.split('—')[1].trim()}</span>}
    </span>
  );
};

// ----------------------------------------------------------------
// ScoreGauge — círculo de score visual
// ----------------------------------------------------------------

interface ScoreGaugeProps {
  score: number;
  rating: Rating;
  size?: number;
}

export const ScoreGauge: React.FC<ScoreGaugeProps> = ({ score, rating, size = 120 }) => {
  const cfg = RATING_CONFIG[rating];
  const pct = score / 1000;
  const r = (size / 2) - 10;
  const circumference = 2 * Math.PI * r;
  const dashOffset = circumference * (1 - pct);

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <circle
          cx={size / 2} cy={size / 2} r={r}
          fill="none" stroke="#e5e7eb" strokeWidth="10"
        />
        <circle
          cx={size / 2} cy={size / 2} r={r}
          fill="none"
          stroke={cfg.color}
          strokeWidth="10"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 1s ease' }}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-2xl font-bold" style={{ color: cfg.color }}>{score}</span>
        <span className="text-xs text-gray-500">/ 1000</span>
      </div>
    </div>
  );
};

// ----------------------------------------------------------------
// RedFlagItem — exibe uma red flag com ícone de severidade
// ----------------------------------------------------------------

interface RedFlagItemProps {
  codigo: string;
  descricao: string;
  severidade: 'CRITICA' | 'ALTA' | 'MEDIA';
}

const SEVERITY_CONFIG = {
  CRITICA: { icon: '🚨', color: '#dc2626', bg: '#fee2e2', label: 'Crítica' },
  ALTA:    { icon: '⚠️', color: '#ea580c', bg: '#ffedd5', label: 'Alta' },
  MEDIA:   { icon: 'ℹ️', color: '#ca8a04', bg: '#fef9c3', label: 'Média' },
};

export const RedFlagItem: React.FC<RedFlagItemProps> = ({ codigo, descricao, severidade }) => {
  const cfg = SEVERITY_CONFIG[severidade];
  return (
    <div
      className="flex items-start gap-3 rounded-lg p-3 mb-2"
      style={{ backgroundColor: cfg.bg, borderLeft: `3px solid ${cfg.color}` }}
    >
      <span className="text-lg flex-shrink-0">{cfg.icon}</span>
      <div>
        <span
          className="text-xs font-semibold uppercase tracking-wide"
          style={{ color: cfg.color }}
        >
          {cfg.label} · {codigo}
        </span>
        <p className="text-sm text-gray-700 mt-0.5">{descricao}</p>
      </div>
    </div>
  );
};

// ----------------------------------------------------------------
// LoadingSpinner
// ----------------------------------------------------------------

export const LoadingSpinner: React.FC<{ message?: string }> = ({
  message = 'Analisando...',
}) => (
  <div className="flex flex-col items-center justify-center gap-3 py-12">
    <div className="w-10 h-10 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
    <p className="text-gray-500 text-sm">{message}</p>
  </div>
);
