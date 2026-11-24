import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle2, Trash2, Layers, AlertCircle, RefreshCw } from 'lucide-react';
import type { DocumentMetadata } from '../types';

interface DocumentManagerProps {
  documents: DocumentMetadata[];
  activeDocument: DocumentMetadata | null;
  onSelectDocument: (doc: DocumentMetadata) => void;
  onUpload: (file: File) => Promise<void>;
  onDelete: (docId: string) => Promise<void>;
  isLoading: boolean;
}

export const DocumentManager: React.FC<DocumentManagerProps> = ({
  documents,
  activeDocument,
  onSelectDocument,
  onUpload,
  onDelete,
  isLoading,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    setUploadError(null);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      await processFile(files[0]);
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    setUploadError(null);
    if (e.target.files && e.target.files.length > 0) {
      await processFile(e.target.files[0]);
      e.target.value = '';
    }
  };

  const processFile = async (file: File) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setUploadError('Only PDF files are supported.');
      return;
    }
    if (file.size > 25 * 1024 * 1024) {
      setUploadError('File size exceeds 25MB limit.');
      return;
    }

    try {
      await onUpload(file);
    } catch (err: any) {
      setUploadError(err.message || 'Failed to upload document.');
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="space-y-6">
      {/* Upload Dropzone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-2xl p-6 sm:p-8 text-center cursor-pointer transition-all duration-200 ${
          isDragging
            ? 'border-indigo-500 bg-indigo-50/50 scale-[1.01]'
            : 'border-slate-300 hover:border-indigo-400 bg-white hover:bg-slate-50/50'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf,.pdf"
          onChange={handleFileChange}
          className="hidden"
        />
        <div className="flex flex-col items-center justify-center space-y-3">
          <div className="w-12 h-12 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center shadow-xs">
            {isLoading ? (
              <RefreshCw className="w-6 h-6 animate-spin text-indigo-600" />
            ) : (
              <UploadCloud className="w-6 h-6" />
            )}
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-800">
              {isLoading ? 'Processing & Indexing Document...' : 'Click to browse or drag and drop your PDF'}
            </p>
            <p className="text-xs text-slate-500 mt-1">PDF documents up to 25MB</p>
          </div>
        </div>
      </div>

      {uploadError && (
        <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{uploadError}</span>
        </div>
      )}

      {/* Active Document Card */}
      {activeDocument && (
        <div className="bg-gradient-to-r from-indigo-50/80 via-white to-violet-50/60 border border-indigo-200 rounded-2xl p-4 sm:p-5 shadow-xs">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3.5">
              <div className="w-10 h-10 rounded-xl bg-indigo-600 text-white flex items-center justify-center shadow-sm shrink-0">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h3 className="font-semibold text-slate-900 text-sm sm:text-base">
                    {activeDocument.original_filename}
                  </h3>
                  <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-100 text-emerald-800 border border-emerald-200">
                    <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                    <span>Active Target</span>
                  </span>
                </div>
                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500 mt-1.5">
                  <span>Size: {formatSize(activeDocument.file_size)}</span>
                  <span>Pages: {activeDocument.page_count}</span>
                  <span className="flex items-center space-x-1">
                    <Layers className="w-3.5 h-3.5 text-indigo-500" />
                    <span>Chunks: {activeDocument.chunk_count}</span>
                  </span>
                  <span>ID: {activeDocument.document_id}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Document Library / List */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Available Documents ({documents.length})
          </h4>
        </div>

        {documents.length === 0 ? (
          <div className="p-8 text-center bg-white rounded-xl border border-slate-200 text-slate-400 text-xs">
            No documents indexed yet. Upload a PDF above to begin.
          </div>
        ) : (
          <div className="grid gap-2.5 sm:grid-cols-2">
            {documents.map((doc) => {
              const isActive = activeDocument?.document_id === doc.document_id;
              return (
                <div
                  key={doc.document_id}
                  onClick={() => onSelectDocument(doc)}
                  className={`flex items-center justify-between p-3.5 rounded-xl border cursor-pointer transition-all ${
                    isActive
                      ? 'border-indigo-500 bg-indigo-50/40 shadow-xs ring-1 ring-indigo-500/20'
                      : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-center space-x-3 min-w-0 pr-2">
                    <div
                      className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                        isActive ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      <FileText className="w-4 h-4" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-xs font-semibold text-slate-900 truncate">
                        {doc.original_filename}
                      </p>
                      <p className="text-[11px] text-slate-500">
                        {doc.page_count} pgs • {formatSize(doc.file_size)}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 shrink-0">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDelete(doc.document_id);
                      }}
                      className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                      title="Delete document"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
