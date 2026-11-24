import React, { useState } from 'react';
import { Hash, MessageSquare, Send, Sparkles, AlertCircle } from 'lucide-react';

interface QuestionSectionProps {
  onAskByNumber: (num: number) => Promise<void>;
  onAskFreeText: (question: string) => Promise<void>;
  disabled: boolean;
  activeDocName: string | null;
}

export const QuestionSection: React.FC<QuestionSectionProps> = ({
  onAskByNumber,
  onAskFreeText,
  disabled,
  activeDocName,
}) => {
  const [mode, setMode] = useState<'by_number' | 'free_text'>('by_number');
  const [questionNumber, setQuestionNumber] = useState<string>('');
  const [freeTextQuestion, setFreeTextQuestion] = useState<string>('');
  const [localError, setLocalError] = useState<string | null>(null);

  const handleSubmitByNumber = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    const parsed = parseInt(questionNumber.trim(), 10);
    if (isNaN(parsed) || parsed <= 0) {
      setLocalError('Please enter a valid positive question number (e.g., 1, 2, 5).');
      return;
    }

    try {
      await onAskByNumber(parsed);
    } catch (err: any) {
      setLocalError(err.message || 'Failed to retrieve question.');
    }
  };

  const handleSubmitFreeText = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    const trimmed = freeTextQuestion.trim();
    if (!trimmed) {
      setLocalError('Please enter a question to ask.');
      return;
    }

    try {
      await onAskFreeText(trimmed);
    } catch (err: any) {
      setLocalError(err.message || 'Failed to generate answer.');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmitFreeText(e);
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden">
      {/* Mode Switcher Tabs */}
      <div className="flex border-b border-slate-200 bg-slate-50/70 p-1.5 gap-1.5">
        <button
          type="button"
          onClick={() => {
            setMode('by_number');
            setLocalError(null);
          }}
          className={`flex-1 flex items-center justify-center space-x-2 py-2.5 px-3 rounded-xl text-xs font-semibold transition-all ${
            mode === 'by_number'
              ? 'bg-white text-indigo-700 shadow-xs ring-1 ring-slate-200/80'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/60'
          }`}
        >
          <Hash className="w-4 h-4 text-indigo-500" />
          <span>Ask by Question Number</span>
          <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-indigo-100 text-indigo-800 uppercase tracking-wider">
            Primary
          </span>
        </button>

        <button
          type="button"
          onClick={() => {
            setMode('free_text');
            setLocalError(null);
          }}
          className={`flex-1 flex items-center justify-center space-x-2 py-2.5 px-3 rounded-xl text-xs font-semibold transition-all ${
            mode === 'free_text'
              ? 'bg-white text-indigo-700 shadow-xs ring-1 ring-slate-200/80'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/60'
          }`}
        >
          <MessageSquare className="w-4 h-4 text-indigo-500" />
          <span>Ask Anything (Free Text)</span>
        </button>
      </div>

      {/* Input Form Body */}
      <div className="p-5 sm:p-6">
        {mode === 'by_number' ? (
          <form onSubmit={handleSubmitByNumber} className="space-y-4">
            <div>
              <label htmlFor="qnum" className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                Enter Question Number
              </label>
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
                <div className="relative flex-1">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <Hash className="w-4 h-4" />
                  </div>
                  <input
                    id="qnum"
                    type="number"
                    min="1"
                    step="1"
                    placeholder="e.g. 1, 2, 5"
                    value={questionNumber}
                    onChange={(e) => {
                      setQuestionNumber(e.target.value);
                      if (localError) setLocalError(null);
                    }}
                    disabled={disabled}
                    className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 disabled:opacity-60 disabled:cursor-not-allowed transition-all"
                  />
                </div>

                <button
                  type="submit"
                  disabled={disabled || !questionNumber.trim()}
                  className="inline-flex items-center justify-center space-x-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white font-semibold text-xs tracking-wide shadow-sm shadow-indigo-100 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Sparkles className="w-4 h-4" />
                  <span>Find and Answer Question</span>
                </button>
              </div>
              <p className="text-[11px] text-slate-500 mt-2">
                DocuMind scans {activeDocName || 'the document'} for Q1., Question 1, 1., etc., extracts the full question text, and answers it using RAG.
              </p>
            </div>
          </form>
        ) : (
          <form onSubmit={handleSubmitFreeText} className="space-y-4">
            <div>
              <label htmlFor="freetext" className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                Ask anything about your document
              </label>
              <div className="relative">
                <textarea
                  id="freetext"
                  rows={3}
                  placeholder="Ask anything about your document (e.g. What are the normal equations for least squares?)..."
                  value={freeTextQuestion}
                  onChange={(e) => {
                    setFreeTextQuestion(e.target.value);
                    if (localError) setLocalError(null);
                  }}
                  onKeyDown={handleKeyDown}
                  disabled={disabled}
                  className="w-full p-3.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-900 placeholder:text-slate-400 focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 disabled:opacity-60 disabled:cursor-not-allowed transition-all resize-y"
                />
              </div>

              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 mt-2">
                <p className="text-[11px] text-slate-400">
                  Press <kbd className="px-1.5 py-0.5 rounded border border-slate-200 bg-slate-100 font-mono text-[10px]">Enter</kbd> to submit, <kbd className="px-1.5 py-0.5 rounded border border-slate-200 bg-slate-100 font-mono text-[10px]">Shift+Enter</kbd> for newline
                </p>

                <button
                  type="submit"
                  disabled={disabled || !freeTextQuestion.trim()}
                  className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white font-semibold text-xs tracking-wide shadow-sm shadow-indigo-100 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Ask Question</span>
                </button>
              </div>
            </div>
          </form>
        )}

        {localError && (
          <div className="mt-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{localError}</span>
          </div>
        )}
      </div>
    </div>
  );
};
