import React, { useState } from 'react';
import { MessageSquare, Send, Bot, User } from 'lucide-react';
import { askAgent } from '../services/api';

// ----------------------------------------------------------------
// Página do Assistente IA (IBM Bob / watsonx)
// ----------------------------------------------------------------

interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const SUGGESTED_QUESTIONS = [
  'O que significa rating C para condições de pagamento?',
  'Quais são os principais red flags para risco de RJ?',
  'Como funciona o monitoramento contínuo da carteira?',
  'Qual a diferença entre inadimplência técnica e financeira?',
];

export const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 0,
      role: 'assistant',
      content:
        '👋 Olá! Sou o **AgroRisk Assistant**, alimentado pelo IBM watsonx Granite.\n\n' +
        'Posso responder suas dúvidas sobre análise de risco de crédito no agronegócio, ' +
        'explicar os critérios do sistema de farol, ou ajudar a interpretar um relatório.\n\n' +
        'Como posso ajudar?',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async (text?: string) => {
    const content = (text || input).trim();
    if (!content || loading) return;

    const userMsg: Message = {
      id: Date.now(),
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const answer = await askAgent(content);
      setMessages(prev => [
        ...prev,
        { id: Date.now() + 1, role: 'assistant', content: answer, timestamp: new Date() },
      ]);
    } catch {
      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: '❌ Erro ao conectar com o assistente. Verifique se a API está rodando.',
          timestamp: new Date(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 flex flex-col" style={{ height: 'calc(100vh - 80px)' }}>
      {/* Header */}
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <MessageSquare className="text-blue-600" size={24} />
          Assistente AgroRisk
        </h1>
        <p className="text-gray-500 text-sm mt-1">
          Powered by IBM watsonx Granite · Especialista em risco de crédito agropecuário
        </p>
      </div>

      {/* Perguntas sugeridas */}
      {messages.length <= 1 && (
        <div className="mb-4 flex flex-wrap gap-2">
          {SUGGESTED_QUESTIONS.map(q => (
            <button
              key={q}
              onClick={() => sendMessage(q)}
              className="text-xs bg-blue-50 text-blue-700 border border-blue-200 px-3 py-1.5 rounded-full hover:bg-blue-100 transition-colors"
            >
              {q}
            </button>
          ))}
        </div>
      )}

      {/* Histórico de mensagens */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-1">
        {messages.map(msg => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-gray-400 text-sm pl-2">
            <Bot size={16} />
            <span className="animate-pulse">Consultando IBM watsonx...</span>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="flex gap-2 border-t border-gray-200 pt-4">
        <input
          type="text"
          className="flex-1 border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Pergunte sobre risco de crédito, ratings, condições de pagamento..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          disabled={loading}
        />
        <button
          onClick={() => sendMessage()}
          disabled={loading || !input.trim()}
          className="flex items-center gap-1.5 bg-blue-600 text-white px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
};

// ----------------------------------------------------------------
// Bolha de mensagem
// ----------------------------------------------------------------

const MessageBubble: React.FC<{ message: Message }> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          isUser ? 'bg-blue-600' : 'bg-gray-100'
        }`}
      >
        {isUser
          ? <User size={16} className="text-white" />
          : <Bot size={16} className="text-gray-600" />
        }
      </div>

      {/* Conteúdo */}
      <div
        className={`max-w-[80%] rounded-xl px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? 'bg-blue-600 text-white rounded-tr-sm'
            : 'bg-gray-100 text-gray-800 rounded-tl-sm'
        }`}
      >
        {/* Renderiza markdown simples para o assistente */}
        {isUser ? (
          <p>{message.content}</p>
        ) : (
          <div className="prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{
              __html: message.content
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\n/g, '<br/>'),
            }}
          />
        )}
        <p className={`text-xs mt-1.5 ${isUser ? 'text-blue-200' : 'text-gray-400'}`}>
          {message.timestamp.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </div>
  );
};
