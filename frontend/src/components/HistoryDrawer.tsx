import React, { useState } from 'react';
import { X, History, Trash2, Clock, FileText, Hash, MessageSquare, ChevronRight, AlertTriangle } from 'lucide-react';
import type { QAResponse } from '../types';

interface HistoryDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  history: QAResponse[];
  onSelectInteraction: (item: QAResponse) => void;
  onClearHistory: () => Promise<void>;
  isLoading: boolean;
}

export const HistoryDrawer: React.FC<HistoryDrawerProps> = ({
  isOpen,
  onClose,
  history,
  onSelectInteraction,
  onClearHistory,
  isLoading,
}) => {
  const [confirmClear, setConfirmClear] = useState(false);

  if (!isOpen) return null;

  const formatDate = (isoString: string) => {
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        onClick={onClose}
        className="absolute inset-0 bg-slate-900/40 backdrop-blur-xs transition-opacity"
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-white shadow-2xl border-l border-slate-200 flex flex-col">
          {/* Drawer Header */}
          <div className="px-6 py-5 border-b border-slate-200 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
                <History className="w-4 h-4" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-sm">Interaction History</h3>
                <p className="text-xs text-slate-500">{history.length} saved question(s)</p>
              </div>
            </div>

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Drawer Content */}
          <div className="flex-1 overflow-y-auto p-6 space-y-3">
            {history.length === 0 ? (
              <div className="h-64 flex flex-col items-center justify-center text-center p-6 text-slate-400 space-y-2">
                <Clock className="w-8 h-8 stroke-1 text-slate-300" />
                <p className="text-xs font-medium text-slate-600">No question history yet</p>
                <p className="text-[11px] text-slate-400">
                  Questions asked in the dashboard will be persisted in MongoDB and listed here.
                </p>
              </div>
            ) : (
              history.map((item) => (
                <div
                  key={item.interaction_id}
                  onClick={() => {
                    onSelectInteraction(item);
                    onClose();
                  }}
                  className="p-4 rounded-xl border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50/20 cursor-pointer transition-all space-y-2 group"
                >
                  <div className="flex items-center justify-between text-xs">
                    <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-100 text-slate-700">
                      {item.question_mode === 'by_number' ? (
                        <>
                          <Hash className="w-3 h-3 text-indigo-500" />
                          <span>Question #{item.requested_question_number}</span>
                        </>
                      ) : (
                        <>
                          <MessageSquare className="w-3 h-3 text-indigo-500" />
                          <span>Free-text</span>
                        </>
                      )}
                    </span>
                    <span className="text-[11px] text-slate-400 flex items-center space-x-1">
                      <Clock className="w-3 h-3" />
                      <span>{formatDate(item.timestamp)}</span>
                    </span>
                  </div>

                  <p className="text-xs font-semibold text-slate-900 group-hover:text-indigo-600 transition-colors line-clamp-2">
                    {item.detected_question_text || item.question}
                  </p>

                  <p className="text-[11px] text-slate-500 line-clamp-2 leading-relaxed">
                    {item.answer}
                  </p>

                  <div className="flex items-center justify-between pt-1 text-[10px] text-slate-400 border-t border-slate-100">
                    <span className="flex items-center space-x-1 truncate max-w-[200px]">
                      <FileText className="w-3 h-3 shrink-0" />
                      <span className="truncate">{item.document_filename}</span>
                    </span>
                    <span className="flex items-center space-x-0.5 text-indigo-600 font-medium">
                      <span>View</span>
                      <ChevronRight className="w-3 h-3" />
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Drawer Footer */}
          {history.length > 0 && (
            <div className="p-4 border-t border-slate-200 bg-slate-50/50">
              {confirmClear ? (
                <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl space-y-2.5">
                  <div className="flex items-center space-x-2 text-xs font-semibold text-amber-800">
                    <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                    <span>Clear all saved interaction history?</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={async () => {
                        await onClearHistory();
                        setConfirmClear(false);
                      }}
                      disabled={isLoading}
                      className="flex-1 py-1.5 px-3 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-xs font-semibold transition-colors disabled:opacity-50"
                    >
                      Yes, Clear
                    </button>
                    <button
                      onClick={() => setConfirmClear(false)}
                      className="flex-1 py-1.5 px-3 bg-white border border-slate-300 text-slate-700 rounded-lg text-xs font-semibold hover:bg-slate-50 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  onClick={() => setConfirmClear(true)}
                  className="w-full flex items-center justify-center space-x-1.5 py-2 px-4 rounded-xl border border-slate-200 bg-white hover:bg-rose-50 hover:border-rose-200 text-slate-600 hover:text-rose-600 text-xs font-medium transition-colors"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  <span>Clear History</span>
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
