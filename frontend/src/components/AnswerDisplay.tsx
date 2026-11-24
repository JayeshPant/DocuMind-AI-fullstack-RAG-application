import React, { useState } from 'react';
import { Copy, Check, BookOpen, FileText, ChevronDown, ChevronUp, Sparkles, AlertCircle } from 'lucide-react';
import type { QAResponse } from '../types';

interface AnswerDisplayProps {
  currentQA: QAResponse | null;
  isLoading: boolean;
  error: string | null;
}

export const AnswerDisplay: React.FC<AnswerDisplayProps> = ({ currentQA, isLoading, error }) => {
  const [copied, setCopied] = useState(false);
  const [sourcesOpen, setSourcesOpen] = useState(true);

  const handleCopy = async () => {
    if (!currentQA?.answer) return;
    try {
      await navigator.clipboard.writeText(currentQA.answer);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-xs space-y-5 animate-pulse">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="space-y-1.5 flex-1">
            <div className="h-4 bg-slate-200 rounded-md w-1/3"></div>
            <div className="h-3 bg-slate-100 rounded-md w-1/4"></div>
          </div>
        </div>

        <div className="space-y-2.5 pt-2">
          <div className="h-3.5 bg-slate-200 rounded-md w-full"></div>
          <div className="h-3.5 bg-slate-200 rounded-md w-5/6"></div>
          <div className="h-3.5 bg-slate-200 rounded-md w-4/6"></div>
          <div className="h-3.5 bg-slate-100 rounded-md w-full pt-4"></div>
          <div className="h-3.5 bg-slate-200 rounded-md w-3/4"></div>
        </div>

        <div className="pt-4 border-t border-slate-100">
          <div className="h-8 bg-slate-100 rounded-xl w-48"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-rose-50/70 border border-rose-200 rounded-2xl p-6 shadow-xs flex items-start space-x-3 text-rose-800">
        <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <h4 className="font-semibold text-sm">Failed to generate answer</h4>
          <p className="text-xs text-rose-700 leading-relaxed">{error}</p>
        </div>
      </div>
    );
  }

  if (!currentQA) {
    return null;
  }

  return (
    <div className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden transition-all">
      {/* Header Info */}
      <div className="bg-gradient-to-r from-slate-50 to-indigo-50/30 px-6 py-4 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 ring-4 ring-emerald-100"></span>
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
            {currentQA.question_mode === 'by_number'
              ? `Question #${currentQA.requested_question_number}`
              : 'Answer Output'}
          </span>
          <span className="text-xs text-slate-400">•</span>
          <span className="text-xs text-slate-600 font-medium">{currentQA.document_filename}</span>
        </div>

        <button
          onClick={handleCopy}
          className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-medium transition-colors shadow-2xs"
          title="Copy answer text"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-600" />
              <span className="text-emerald-700">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5 text-slate-500" />
              <span>Copy Answer</span>
            </>
          )}
        </button>
      </div>

      <div className="p-6 sm:p-8 space-y-6">
        {/* Detected Question Banner (if by_number) */}
        {currentQA.detected_question_text && (
          <div className="p-4 rounded-xl bg-indigo-50/70 border border-indigo-100 space-y-1">
            <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-700">
              Detected Question in PDF
            </span>
            <p className="text-sm font-semibold text-indigo-950 leading-snug">
              {currentQA.detected_question_text}
            </p>
          </div>
        )}

        {/* Answer Typography */}
        <div className="space-y-4">
          <div className="text-sm sm:text-base text-slate-800 leading-relaxed whitespace-pre-wrap font-normal">
            {currentQA.answer}
          </div>
        </div>

        {/* Evidence / Source Excerpts Section */}
        {currentQA.sources && currentQA.sources.length > 0 && (
          <div className="pt-6 border-t border-slate-100">
            <button
              onClick={() => setSourcesOpen(!sourcesOpen)}
              className="w-full flex items-center justify-between py-2 text-left group"
            >
              <div className="flex items-center space-x-2">
                <BookOpen className="w-4 h-4 text-indigo-600" />
                <span className="text-xs font-bold uppercase tracking-wider text-slate-700 group-hover:text-indigo-600 transition-colors">
                  Retrieved Document Evidence ({currentQA.sources.length} chunks)
                </span>
              </div>
              <div className="text-slate-400 group-hover:text-slate-600 transition-colors">
                {sourcesOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </div>
            </button>

            {sourcesOpen && (
              <div className="mt-3 grid gap-3 sm:grid-cols-2">
                {currentQA.sources.map((source, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/60 hover:bg-slate-50 transition-colors text-xs space-y-2"
                  >
                    <div className="flex items-center justify-between text-slate-500 font-medium">
                      <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-white border border-slate-200 text-indigo-700 font-semibold text-[11px]">
                        <FileText className="w-3 h-3" />
                        <span>Page {source.page}</span>
                      </span>
                      <span className="text-[10px] text-slate-400">Chunk {idx + 1}</span>
                    </div>
                    <p className="text-slate-700 leading-relaxed font-mono text-[11px] bg-white p-2.5 rounded-lg border border-slate-100 overflow-hidden text-ellipsis">
                      "{source.content}"
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
