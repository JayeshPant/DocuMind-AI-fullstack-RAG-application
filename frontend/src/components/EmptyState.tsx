import React from 'react';
import { FileQuestion, Sparkles, ArrowUp } from 'lucide-react';

interface EmptyStateProps {
  hasDocument: boolean;
  documentName?: string;
  onSampleClick: (q: string) => void;
  onSampleNumberClick: (num: number) => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  hasDocument,
  documentName,
  onSampleClick,
  onSampleNumberClick,
}) => {
  if (!hasDocument) {
    return (
      <div className="bg-white border border-slate-200 rounded-2xl p-10 text-center space-y-4 shadow-2xs">
        <div className="w-14 h-14 rounded-2xl bg-indigo-50 text-indigo-500 mx-auto flex items-center justify-center">
          <FileQuestion className="w-7 h-7" />
        </div>
        <div className="max-w-md mx-auto space-y-1">
          <h3 className="font-bold text-slate-800 text-base">No Active Document Selected</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            Upload your lecture notes, study guide, or question bank PDF above to start extracting questions and generating grounded answers.
          </p>
        </div>
        <div className="inline-flex items-center space-x-1.5 text-xs text-indigo-600 font-semibold bg-indigo-50/80 px-3 py-1.5 rounded-full">
          <ArrowUp className="w-3.5 h-3.5" />
          <span>Upload a PDF to get started</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-8 sm:p-10 text-center space-y-5 shadow-2xs">
      <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-50 to-violet-100 text-indigo-600 mx-auto flex items-center justify-center shadow-xs">
        <Sparkles className="w-7 h-7" />
      </div>

      <div className="max-w-md mx-auto space-y-1">
        <h3 className="font-bold text-slate-800 text-base">Ready to Answer Questions</h3>
        <p className="text-xs text-slate-500 leading-relaxed">
          {documentName} is indexed in the in-memory vector database. Enter a question number or ask anything below.
        </p>
      </div>

      {/* Suggested question chips */}
      <div className="pt-2 max-w-lg mx-auto">
        <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-2.5">
          Try a sample action:
        </p>
        <div className="flex flex-wrap items-center justify-center gap-2">
          <button
            onClick={() => onSampleNumberClick(1)}
            className="px-3 py-1.5 rounded-lg border border-slate-200 bg-slate-50 hover:bg-indigo-50 hover:border-indigo-200 text-slate-700 hover:text-indigo-700 text-xs font-medium transition-colors"
          >
            Ask Question #1
          </button>
          <button
            onClick={() =>
              onSampleClick(
                'What are the normal equations for fitting a straight line using the principle of least squares?'
              )
            }
            className="px-3 py-1.5 rounded-lg border border-slate-200 bg-slate-50 hover:bg-indigo-50 hover:border-indigo-200 text-slate-700 hover:text-indigo-700 text-xs font-medium transition-colors"
          >
            "Normal equations for least squares"
          </button>
        </div>
      </div>
    </div>
  );
};
