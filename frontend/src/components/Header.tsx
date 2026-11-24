import React from 'react';
import { Bot, CheckCircle2, AlertCircle, Database, Cpu, History, FileText } from 'lucide-react';
import type { HealthStatus } from '../types';

interface HeaderProps {
  health: HealthStatus | null;
  activeTab: 'dashboard' | 'documents';
  setActiveTab: (tab: 'dashboard' | 'documents') => void;
  onOpenHistory: () => void;
  historyCount: number;
}

export const Header: React.FC<HeaderProps> = ({
  health,
  activeTab,
  setActiveTab,
  onOpenHistory,
  historyCount,
}) => {
  const isHealthy = health?.status === 'healthy';

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo & Title */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-md shadow-indigo-100">
              <Bot className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-xl tracking-tight text-slate-900">DocuMind</span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
                  AI RAG
                </span>
              </div>
              <p className="text-xs text-slate-500 hidden sm:block">
                Your Intelligent PDF Question Answering Assistant
              </p>
            </div>
          </div>

          {/* Navigation & Status */}
          <div className="flex items-center space-x-3 sm:space-x-5">
            {/* Nav Tabs */}
            <nav className="flex space-x-1 bg-slate-100 p-1 rounded-lg">
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                  activeTab === 'dashboard'
                    ? 'bg-white text-indigo-600 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setActiveTab('documents')}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors flex items-center space-x-1.5 ${
                  activeTab === 'documents'
                    ? 'bg-white text-indigo-600 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <FileText className="w-3.5 h-3.5" />
                <span>Documents</span>
              </button>
            </nav>

            {/* History Button */}
            <button
              onClick={onOpenHistory}
              className="relative p-2 text-slate-600 hover:text-indigo-600 hover:bg-slate-50 rounded-lg transition-colors border border-slate-200"
              title="View Q&A History"
            >
              <History className="w-4 h-4" />
              {historyCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-indigo-600 text-white text-[10px] font-bold w-4 h-4 rounded-full flex items-center justify-center">
                  {historyCount > 9 ? '9+' : historyCount}
                </span>
              )}
            </button>

            {/* Health / Engine Status */}
            <div className="hidden md:flex items-center space-x-2 pl-3 border-l border-slate-200">
              <div
                className={`flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-medium ${
                  isHealthy
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                    : 'bg-rose-50 text-rose-700 border border-rose-200'
                }`}
              >
                {isHealthy ? (
                  <>
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Backend Online</span>
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-3.5 h-3.5 text-rose-600" />
                    <span>Disconnected</span>
                  </>
                )}
              </div>

              {health?.nvidia_configured && (
                <span className="flex items-center space-x-1 px-2 py-0.5 rounded-md text-[11px] font-medium bg-slate-100 text-slate-700">
                  <Cpu className="w-3 h-3 text-emerald-600" />
                  <span>NVIDIA Nemotron</span>
                </span>
              )}

              <span
                className={`flex items-center space-x-1 px-2 py-0.5 rounded-md text-[11px] font-medium ${
                  health?.mongodb_connected
                    ? 'bg-slate-100 text-slate-700'
                    : 'bg-amber-50 text-amber-700'
                }`}
                title={health?.mongodb_connected ? 'MongoDB Atlas Connected' : 'Using Local Storage Fallback'}
              >
                <Database className="w-3 h-3 text-indigo-600" />
                <span>{health?.mongodb_connected ? 'MongoDB Atlas' : 'Local DB'}</span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
