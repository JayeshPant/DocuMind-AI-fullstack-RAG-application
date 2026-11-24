import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { DocumentManager } from './components/DocumentManager';
import { QuestionSection } from './components/QuestionSection';
import { AnswerDisplay } from './components/AnswerDisplay';
import { HistoryDrawer } from './components/HistoryDrawer';
import { EmptyState } from './components/EmptyState';
import {
  fetchHealth,
  fetchDocuments,
  uploadDocument,
  deleteDocument,
  askQuestion,
  askByQuestionNumber,
  fetchHistory,
  clearHistory,
} from './services/api';
import type { HealthStatus, DocumentMetadata, QAResponse } from './types';
import { AlertCircle, FileText, CheckCircle2 } from 'lucide-react';

export function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [activeDocument, setActiveDocument] = useState<DocumentMetadata | null>(null);
  const [currentQA, setCurrentQA] = useState<QAResponse | null>(null);
  const [history, setHistory] = useState<QAResponse[]>([]);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'documents'>('dashboard');
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  const [isLoadingQA, setIsLoadingQA] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [qaError, setQaError] = useState<string | null>(null);

  // Initial load
  useEffect(() => {
    loadHealth();
    loadDocuments();
    loadHistory();

    const interval = setInterval(loadHealth, 25000);
    return () => clearInterval(interval);
  }, []);

  const loadHealth = async () => {
    try {
      const h = await fetchHealth();
      setHealth(h);
    } catch {
      setHealth(null);
    }
  };

  const loadDocuments = async () => {
    try {
      const docs = await fetchDocuments();
      setDocuments(docs);
      if (docs.length > 0 && !activeDocument) {
        // Auto-select preloaded STATS.pdf or first document
        const statsDoc = docs.find((d) => d.original_filename === 'STATS.pdf');
        setActiveDocument(statsDoc || docs[0]);
      }
    } catch (e) {
      console.error('Error fetching documents:', e);
    }
  };

  const loadHistory = async () => {
    try {
      const h = await fetchHistory();
      setHistory(h);
    } catch (e) {
      console.error('Error fetching history:', e);
    }
  };

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    try {
      const newDoc = await uploadDocument(file);
      setDocuments((prev) => [newDoc, ...prev]);
      setActiveDocument(newDoc);
      await loadHealth();
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteDocument = async (docId: string) => {
    await deleteDocument(docId);
    setDocuments((prev) => prev.filter((d) => d.document_id !== docId));
    if (activeDocument?.document_id === docId) {
      const remaining = documents.filter((d) => d.document_id !== docId);
      setActiveDocument(remaining.length > 0 ? remaining[0] : null);
      setCurrentQA(null);
    }
    await loadHistory();
    await loadHealth();
  };

  const handleAskByNumber = async (num: number) => {
    if (!activeDocument) return;
    setIsLoadingQA(true);
    setQaError(null);

    try {
      const res = await askByQuestionNumber(activeDocument.document_id, num);
      setCurrentQA(res);
      setHistory((prev) => [res, ...prev]);
    } catch (err: any) {
      setQaError(err.message || `Question #${num} could not be retrieved.`);
    } finally {
      setIsLoadingQA(false);
    }
  };

  const handleAskFreeText = async (question: string) => {
    if (!activeDocument) return;
    setIsLoadingQA(true);
    setQaError(null);

    try {
      const res = await askQuestion(activeDocument.document_id, question);
      setCurrentQA(res);
      setHistory((prev) => [res, ...prev]);
    } catch (err: any) {
      setQaError(err.message || 'Failed to generate answer.');
    } finally {
      setIsLoadingQA(false);
    }
  };

  const handleClearHistory = async () => {
    await clearHistory();
    setHistory([]);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <Header
        health={health}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenHistory={() => setIsHistoryOpen(true)}
        historyCount={history.length}
      />

      {/* Warning banner if backend or API key is not configured */}
      {health && !health.nvidia_configured && (
        <div className="bg-amber-500 text-white text-xs px-4 py-2.5 font-medium flex items-center justify-center space-x-2 shadow-xs">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>
            NVIDIA API Key is missing. Please add your <code className="bg-amber-600/60 px-1 py-0.5 rounded font-mono">NVIDIA_API_KEY</code> to <code className="bg-amber-600/60 px-1 py-0.5 rounded font-mono">backend/.env</code> to enable LLM answer generation.
          </span>
        </div>
      )}

      {/* Main Content Area */}
      <main className="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6">
        {activeTab === 'dashboard' ? (
          <>
            {/* Top Bar / Document Quick Selector */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs">
              <div className="flex items-center space-x-3">
                <div className="w-9 h-9 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                    Active Document
                  </span>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-bold text-slate-800">
                      {activeDocument ? activeDocument.original_filename : 'No document selected'}
                    </span>
                    {activeDocument && (
                      <span className="inline-flex items-center space-x-1 px-2 py-0.2 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                        <span>Indexed</span>
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-2 self-end sm:self-center">
                <button
                  onClick={() => setActiveTab('documents')}
                  className="px-3 py-1.5 rounded-xl border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50/50 text-xs font-semibold text-slate-700 hover:text-indigo-600 transition-colors"
                >
                  {documents.length > 0 ? 'Switch / Upload PDF' : 'Upload Document'}
                </button>
              </div>
            </div>

            {/* Question Input Section */}
            <QuestionSection
              onAskByNumber={handleAskByNumber}
              onAskFreeText={handleAskFreeText}
              disabled={isLoadingQA || !activeDocument}
              activeDocName={activeDocument?.original_filename || null}
            />

            {/* Answer Display */}
            {isLoadingQA || currentQA || qaError ? (
              <AnswerDisplay currentQA={currentQA} isLoading={isLoadingQA} error={qaError} />
            ) : (
              <EmptyState
                hasDocument={!!activeDocument}
                documentName={activeDocument?.original_filename}
                onSampleClick={handleAskFreeText}
                onSampleNumberClick={handleAskByNumber}
              />
            )}
          </>
        ) : (
          /* Documents Tab */
          <div className="space-y-6">
            <div>
              <h2 className="text-lg font-bold text-slate-900 tracking-tight">Document Management</h2>
              <p className="text-xs text-slate-500 mt-1">
                Upload new PDF files or select an active target for RAG retrieval and question answering.
              </p>
            </div>

            <DocumentManager
              documents={documents}
              activeDocument={activeDocument}
              onSelectDocument={(doc) => {
                setActiveDocument(doc);
                setActiveTab('dashboard');
              }}
              onUpload={handleUpload}
              onDelete={handleDeleteDocument}
              isLoading={isUploading}
            />
          </div>
        )}
      </main>

      {/* History Drawer */}
      <HistoryDrawer
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        history={history}
        onSelectInteraction={(item) => {
          setCurrentQA(item);
          setActiveTab('dashboard');
        }}
        onClearHistory={handleClearHistory}
        isLoading={false}
      />

      {/* Footer */}
      <footer className="border-t border-slate-200 py-4 bg-white text-center text-xs text-slate-400">
        <p>DocuMind AI • Powered by LangChain, FastEmbed, Qdrant & NVIDIA Nemotron</p>
      </footer>
    </div>
  );
}

export default App;
