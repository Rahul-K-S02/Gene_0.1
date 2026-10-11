'use client';

import React, { useState } from 'react';
import { sendChatQuestion } from '../lib/api';
import { MessageSquare, X, Send, Bot, User, Sparkles, BookOpen } from 'lucide-react';
import { FormattedMessage } from './FormattedMessage';

interface RagChatModalProps {
  isOpen: boolean;
  onClose: () => void;
  reportSummary: Record<string, any>;
  language: string;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: Array<{ title: string; citation: string }>;
}

export const RagChatModal: React.FC<RagChatModalProps> = ({
  isOpen,
  onClose,
  reportSummary,
  language,
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content:
        'Hello! I am your GeneRisk Clinical RAG Assistant. Ask me anything about your genetic polygenic risk scores, SHAP feature drivers, pharmacogenomics alerts, or lifestyle recommendations.',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userQuery = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userQuery }]);
    setLoading(true);

    try {
      const res = await sendChatQuestion(userQuery, reportSummary, language);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: res.answer,
          citations: res.citations,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content:
            'I encountered an error connecting to the clinical RAG engine. Please verify your connection or try again.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const sampleQuestions = [
    'What does my 9p21.3 (rs1333049) variant mean?',
    'Why is Simvastatin flagged for my SLCO1B1 genotype?',
    'How much can Mediterranean diet reduce my risk?',
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4">
      <div className="flex flex-col h-[600px] w-full max-w-2xl rounded-2xl bg-white shadow-2xl border border-slate-200 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-5 py-3.5">
          <div className="flex items-center space-x-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-white shadow-xs">
              <Bot className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900">
                GeneRisk Clinical Q&amp;A Assistant
              </h3>
              <p className="text-[11px] text-slate-500 font-medium">
                Grounded in Qdrant Medical Evidence Knowledge Base
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-200/60 hover:text-slate-600 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Message Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3.5 bg-slate-50/30">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex items-start space-x-2.5 ${
                msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}
            >
              <div
                className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
                  msg.role === 'user'
                    ? 'bg-brand-600 text-white'
                    : 'bg-slate-200 text-slate-700'
                }`}
              >
                {msg.role === 'user' ? <User className="h-3.5 w-3.5" /> : <Bot className="h-3.5 w-3.5" />}
              </div>

              <div
                className={`rounded-2xl px-4 py-2.5 text-xs leading-relaxed max-w-[82%] shadow-xs ${
                  msg.role === 'user'
                    ? 'bg-brand-600 text-white font-medium'
                    : 'bg-white border border-slate-200 text-slate-800'
                }`}
              >
                <FormattedMessage content={msg.content} isUser={msg.role === 'user'} />

                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-2.5 pt-2 border-t border-slate-100 text-[10px] text-slate-500">
                    <span className="font-bold block mb-1">Citations:</span>
                    <ul className="list-disc list-inside space-y-0.5">
                      {msg.citations.map((c, i) => (
                        <li key={i} className="truncate">
                          {c.title}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex items-center space-x-2 text-xs text-slate-400 p-2">
              <div className="h-3.5 w-3.5 border-2 border-brand-600 border-t-transparent rounded-full animate-spin" />
              <span>Retrieving medical evidence and reasoning...</span>
            </div>
          )}
        </div>

        {/* Quick Suggestion Chips */}
        <div className="px-4 py-2 bg-white border-t border-slate-100 flex items-center space-x-2 overflow-x-auto">
          <span className="text-[10px] font-bold text-slate-400 uppercase shrink-0">Try:</span>
          {sampleQuestions.map((q, i) => (
            <button
              key={i}
              onClick={() => {
                setInput(q);
              }}
              className="rounded-full bg-slate-100 hover:bg-slate-200 px-2.5 py-1 text-[11px] font-medium text-slate-700 whitespace-nowrap transition-colors"
            >
              {q}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div className="border-t border-slate-200 bg-white p-3">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center space-x-2"
          >
            <input
              type="text"
              placeholder="Ask a question about your genetic risk report..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="flex-1 rounded-xl border border-slate-300 px-3.5 py-2 text-xs focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-600 text-white hover:bg-brand-700 disabled:opacity-40 transition-colors"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
