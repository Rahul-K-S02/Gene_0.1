'use client';

import React, { useState, useEffect } from 'react';
import { HistoryItem, AnalysisResponse } from '../lib/types';
import { fetchUserHistory, deleteHistoryItem } from '../lib/api';
import { History, X, Trash2, FileText, ArrowUpRight, Calendar, Activity, Download } from 'lucide-react';

interface HistoryDashboardProps {
  isOpen: boolean;
  onClose: () => void;
  token: string | null;
  onSelectReport: (report: AnalysisResponse) => void;
}

export const HistoryDashboard: React.FC<HistoryDashboardProps> = ({
  isOpen,
  onClose,
  token,
  onSelectReport,
}) => {
  const [historyItems, setHistoryItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && token) {
      loadHistory();
    }
  }, [isOpen, token]);

  const loadHistory = async () => {
    if (!token) return;
    setLoading(true);
    try {
      const data = await fetchUserHistory(token);
      setHistoryItems(data);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (historyId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!token) return;
    if (confirm('Delete this saved analysis record?')) {
      await deleteHistoryItem(historyId, token);
      setHistoryItems((prev) => prev.filter((item) => item.history_id !== historyId));
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-end bg-slate-900/60 backdrop-blur-xs p-4 sm:p-6">
      <div className="flex flex-col h-full w-full max-w-lg rounded-3xl bg-white shadow-2xl border border-slate-200 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-6 py-4">
          <div className="flex items-center space-x-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-brand-600 text-white shadow-xs">
              <History className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900">My Genomic Search History</h3>
              <p className="text-[11px] text-slate-500 font-medium">Synced with MongoDB Database</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-xl p-1.5 text-slate-400 hover:bg-slate-200/60 hover:text-slate-600 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* History List */}
        <div className="flex-1 overflow-y-auto p-5 space-y-3 bg-slate-50/50">
          {!token ? (
            <div className="p-8 text-center text-xs text-slate-500">
              <p className="font-semibold text-slate-700 mb-1">Sign in to save and access history</p>
              <p>Your previous analyses and PDF reports will be maintained in your profile.</p>
            </div>
          ) : loading ? (
            <div className="p-8 text-center text-xs text-slate-400">Loading history records...</div>
          ) : historyItems.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-400">
              No saved reports yet. Run an analysis to save your results automatically!
            </div>
          ) : (
            historyItems.map((item) => {
              const highestRisk = item.disease_risks[0];
              return (
                <div
                  key={item.history_id}
                  onClick={() => {
                    onSelectReport({
                      analysis_id: item.analysis_id,
                      timestamp: item.timestamp,
                      patient_summary: item.patient_summary,
                      disease_risks: item.disease_risks,
                      clinvar_pathogenic_findings: item.clinvar_pathogenic_findings,
                      pharmgkb_alerts: item.pharmgkb_alerts,
                      ai_explanation_narrative: item.ai_explanation_narrative,
                      ai_lifestyle_prescriptions: item.ai_lifestyle_prescriptions,
                      evidence_citations: [],
                      pdf_report_base64: item.pdf_report_base64,
                      system_status: { database: 'MongoDB Atlas' },
                    });
                    onClose();
                  }}
                  className="rounded-2xl border border-slate-200 bg-white p-4 hover:border-brand-400 hover:shadow-xs transition-all cursor-pointer group"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <span className="text-xs font-bold text-slate-900 group-hover:text-brand-600 transition-colors">
                        {item.analysis_id}
                      </span>
                      <div className="flex items-center space-x-1.5 text-[10px] text-slate-400 mt-0.5">
                        <Calendar className="h-3 w-3" />
                        <span>{new Date(item.timestamp).toLocaleDateString()} at {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={(e) => handleDelete(item.history_id, e)}
                      className="p-1 text-slate-300 hover:text-rose-600 transition-colors"
                      title="Delete record"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>

                  {/* Summary Snippet */}
                  {highestRisk && (
                    <div className="rounded-xl bg-slate-50 p-2.5 border border-slate-100 flex items-center justify-between text-xs mb-2">
                      <span className="text-slate-600 font-medium">{highestRisk.disease_name}</span>
                      <span className="font-bold text-slate-900">
                        {highestRisk.prs_percentile.toFixed(0)}th %ile &bull; {highestRisk.risk_category}
                      </span>
                    </div>
                  )}

                  <div className="flex items-center justify-between text-[11px] font-bold text-brand-600 pt-1">
                    <span>Re-open Interactive Report</span>
                    <ArrowUpRight className="h-3.5 w-3.5 group-hover:translate-x-0.5 transition-transform" />
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
