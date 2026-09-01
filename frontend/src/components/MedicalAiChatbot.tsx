'use client';

import React, { useState, useRef, useEffect } from 'react';
import { AgentChatMessage } from '../lib/types';
import { sendAgentChatMessage } from '../lib/api';
import {
  Bot, MessageSquare, X, Send, Sparkles, ShieldAlert,
  HeartPulse, Landmark, Pill, ChevronDown, Video, Play, ExternalLink, Ribbon
} from 'lucide-react';

interface MedicalAiChatbotProps {
  patientContext?: Record<string, any>;
  language: string;
}

export const MedicalAiChatbot: React.FC<MedicalAiChatbotProps> = ({
  patientContext,
  language,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<AgentChatMessage[]>([
    {
      id: '1',
      sender: 'agent',
      text: 'Namaste & Hello! I am Dr. GeneRisk, your 24/7 AI Medical, Cancer Awareness & Public Health Assistant. Ask me about your genetic risk report, cancer warning signs, safe home remedies for common symptoms, nearest hospital emergency guidance, or government health schemes (Ayushman Bharat, Jan Aushadhi & Arogya Karnataka).',
      timestamp: new Date().toISOString(),
      suggestedActions: [
        'Cancer warning signs & screening age',
        'How to get Ayushman ₹5 Lakh Cover?',
        'Home remedies for mild acidity/BP',
        'Emergency hospital triage (108)',
      ],
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeVideoModal, setActiveVideoModal] = useState<{ id: string; title: string } | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = async (textToSend?: string) => {
    const query = textToSend || input.trim();
    if (!query || loading) return;

    setInput('');
    const userMsg: AgentChatMessage = {
      id: String(Date.now()),
      sender: 'user',
      text: query,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const historyPayload = messages.slice(-4).map((m) => ({
        role: m.sender === 'user' ? 'user' : 'assistant',
        content: m.text,
      }));

      const res = await sendAgentChatMessage(query, historyPayload, patientContext, language);

      const agentMsg: AgentChatMessage = {
        id: String(Date.now() + 1),
        sender: 'agent',
        text: res.reply,
        intent: res.intent_detected,
        citations: res.citations,
        suggestedActions: res.suggested_actions,
        timestamp: res.timestamp,
      };
      setMessages((prev) => [...prev, agentMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: String(Date.now() + 1),
          sender: 'agent',
          text: 'I apologize, I am temporarily unable to connect to the medical knowledge server. Please try again.',
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-5 right-5 z-50">
      {/* Video Modal Inside Chatbot */}
      {activeVideoModal && (
        <div className="fixed inset-0 z-60 flex items-center justify-center bg-slate-900/80 p-4">
          <div className="relative w-full max-w-xl rounded-2xl bg-slate-900 p-4 shadow-2xl border border-slate-700 space-y-3">
            <div className="flex items-center justify-between text-white">
              <h4 className="text-xs sm:text-sm font-bold truncate pr-4">
                {activeVideoModal.title}
              </h4>
              <div className="flex items-center space-x-2">
                <a
                  href={`https://www.youtube.com/watch?v=${activeVideoModal.id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center space-x-1 text-xs font-bold text-slate-300 hover:text-white bg-slate-800 px-2.5 py-1 rounded-lg border border-slate-700"
                >
                  <span>YouTube</span>
                  <ExternalLink className="h-3 w-3" />
                </a>
                <button
                  onClick={() => setActiveVideoModal(null)}
                  className="flex h-7 w-7 items-center justify-center rounded-full bg-rose-600 hover:bg-rose-700 text-white font-bold"
                >
                  ✕
                </button>
              </div>
            </div>

            <div className="aspect-video w-full rounded-xl overflow-hidden bg-black border border-slate-800">
              <iframe
                src={`https://www.youtube-nocookie.com/embed/${activeVideoModal.id}?autoplay=1&rel=0`}
                title={activeVideoModal.title}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                className="w-full h-full"
              />
            </div>
          </div>
        </div>
      )}

      {/* Floating Toggle Button */}
      {!isOpen && (
        <button
          type="button"
          onClick={() => setIsOpen(true)}
          className="flex items-center space-x-2.5 rounded-full bg-gradient-to-r from-brand-600 via-indigo-600 to-brand-700 px-5 py-3 text-white shadow-xl shadow-brand-500/30 hover:scale-105 active:scale-95 transition-all"
        >
          <div className="relative">
            <Bot className="h-6 w-6" />
            <span className="absolute -top-1 -right-1 h-2.5 w-2.5 rounded-full bg-emerald-400 animate-ping" />
            <span className="absolute -top-1 -right-1 h-2.5 w-2.5 rounded-full bg-emerald-400" />
          </div>
          <div className="text-left hidden sm:block">
            <p className="text-xs font-black leading-tight">Dr. GeneRisk AI</p>
            <p className="text-[10px] text-brand-100 font-medium">24/7 Medical &amp; Scheme Assistant</p>
          </div>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="flex flex-col h-[580px] w-[360px] sm:w-[440px] rounded-3xl bg-white shadow-2xl border border-slate-200 overflow-hidden animate-in fade-in slide-in-from-bottom-5">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-slate-200 bg-gradient-to-r from-brand-600 via-indigo-600 to-purple-700 px-5 py-3.5 text-white">
            <div className="flex items-center space-x-2.5">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/20 text-white backdrop-blur-xs shadow-inner">
                <Bot className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold">Dr. GeneRisk AI Health Assistant</h3>
                <p className="text-[10px] text-brand-100 font-medium">
                  Grounded in AHA, ADA, NCCN Cancer &amp; Indian Govt Health Schemes
                </p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="rounded-xl p-1.5 text-white/80 hover:bg-white/10 hover:text-white transition-colors"
            >
              <ChevronDown className="h-5 w-5" />
            </button>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50/50 text-xs">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`rounded-2xl px-4 py-2.5 leading-relaxed max-w-[90%] shadow-2xs ${
                    m.sender === 'user'
                      ? 'bg-brand-600 text-white font-medium'
                      : 'bg-white border border-slate-200 text-slate-800'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{m.text}</p>

                  {/* Intent Tag */}
                  {m.intent && m.intent !== 'general' && (
                    <div className="mt-2 flex items-center space-x-1 text-[10px] text-slate-400 border-t border-slate-100 pt-1.5 font-bold uppercase">
                      {m.intent === 'emergency_hospital' && (
                        <span className="text-rose-600">🚨 Emergency Response Protocol</span>
                      )}
                      {m.intent === 'cancer_awareness' && (
                        <span className="text-rose-700 flex items-center space-x-1">
                          <Ribbon className="h-3 w-3" />
                          <span>🎗️ Cancer Early Warning &amp; Screening</span>
                        </span>
                      )}
                      {m.intent === 'home_remedy' && (
                        <span className="text-emerald-600">🌿 Supportive Home Wellness</span>
                      )}
                      {m.intent === 'govt_scheme' && (
                        <span className="text-brand-600">🏥 Government Healthcare Scheme</span>
                      )}
                      {m.intent === 'medical_faq' && (
                        <span className="text-indigo-600">🧬 Clinical Genomic Education</span>
                      )}
                    </div>
                  )}

                  {/* Citations & Videos */}
                  {m.citations && m.citations.length > 0 && (
                    <div className="mt-2.5 border-t border-slate-100 pt-2 text-[10px] text-slate-500 space-y-1.5">
                      <div>
                        <span className="font-bold text-slate-700">Clinical Citations:</span>{' '}
                        {m.citations.map((c) => c.title).join(' • ')}
                      </div>

                      {/* Video Badges */}
                      <div className="flex flex-wrap gap-1.5 pt-0.5">
                        {m.citations
                          .filter((c) => c.video_url)
                          .map((c, idx) => {
                            const videoId = c.video_url?.split('v=')[1] || 'z4L3wu5D2eM';
                            return (
                              <div key={idx} className="flex items-center space-x-1">
                                <button
                                  type="button"
                                  onClick={() => setActiveVideoModal({ id: videoId, title: c.title })}
                                  className="inline-flex items-center space-x-1 rounded-md bg-rose-50 hover:bg-rose-100 px-2 py-0.5 text-[9px] font-bold text-rose-700 border border-rose-200 transition-colors"
                                >
                                  <Play className="h-2.5 w-2.5 fill-current text-rose-600" />
                                  <span>Watch Video</span>
                                </button>
                                <a
                                  href={`https://www.youtube.com/watch?v=${videoId}`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-slate-400 hover:text-slate-600 p-0.5"
                                  title="Open in YouTube"
                                >
                                  <ExternalLink className="h-2.5 w-2.5" />
                                </a>
                              </div>
                            );
                          })}
                      </div>
                    </div>
                  )}
                </div>

                {/* Suggested Action Chips */}
                {m.suggestedActions && m.suggestedActions.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1.5 max-w-[92%]">
                    {m.suggestedActions.map((action, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSend(action)}
                        className="rounded-full bg-slate-200/80 hover:bg-brand-100 hover:text-brand-800 text-[11px] font-medium text-slate-700 px-2.5 py-1 transition-all"
                      >
                        {action}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex items-center space-x-2 text-xs text-slate-400 p-2">
                <div className="h-3.5 w-3.5 border-2 border-brand-600 border-t-transparent rounded-full animate-spin" />
                <span>Dr. GeneRisk is retrieving clinical guidelines...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
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
                placeholder="Ask Dr. GeneRisk about cancer signs, health, or schemes..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                className="flex-1 rounded-xl border border-slate-300 px-3.5 py-2 text-xs focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
              />
              <button
                type="submit"
                disabled={!input.trim() || loading}
                className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-600 text-white hover:bg-brand-700 disabled:opacity-40 transition-colors shadow-xs"
              >
                <Send className="h-4 w-4" />
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
