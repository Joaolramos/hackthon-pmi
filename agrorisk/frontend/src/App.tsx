import React from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { Search, LayoutDashboard, MessageSquare, Zap } from 'lucide-react';
import { AnalyzePage } from './pages/AnalyzePage';
import { PortfolioPage } from './pages/PortfolioPage';
import { ChatPage } from './pages/ChatPage';
import './index.css';

// ----------------------------------------------------------------
// Layout principal com nav lateral
// ----------------------------------------------------------------

const NAV_ITEMS = [
  { to: '/',          label: 'Carteira',  icon: <LayoutDashboard size={18} /> },
  { to: '/analyze',   label: 'Analisar',  icon: <Search size={18} /> },
  { to: '/chat',      label: 'Assistente',icon: <MessageSquare size={18} /> },
];

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="flex min-h-screen bg-gray-50">
    {/* Sidebar */}
    <aside className="w-56 bg-white border-r border-gray-200 flex flex-col">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <Zap size={16} className="text-white" />
          </div>
          <div>
            <p className="text-sm font-bold text-gray-900">AgroRisk</p>
            <p className="text-xs text-gray-400">Intelligence</p>
          </div>
        </div>
        <p className="text-xs text-gray-400 mt-2">Powered by IBM watsonx</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV_ITEMS.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              }`
            }
          >
            {item.icon}
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Footer da sidebar */}
      <div className="px-5 py-4 border-t border-gray-100">
        <p className="text-xs text-gray-400">Krill Tech · Hackathon PMI-DF 2026</p>
      </div>
    </aside>

    {/* Conteúdo principal */}
    <main className="flex-1 overflow-auto">{children}</main>
  </div>
);

// ----------------------------------------------------------------
// App com roteamento
// ----------------------------------------------------------------

const App: React.FC = () => (
  <BrowserRouter>
    <Layout>
      <Routes>
        <Route path="/"        element={<PortfolioPage />} />
        <Route path="/analyze" element={<AnalyzePage />} />
        <Route path="/chat"    element={<ChatPage />} />
      </Routes>
    </Layout>
  </BrowserRouter>
);

export default App;
