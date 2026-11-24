import type { HealthStatus, DocumentMetadata, QAResponse } from '../types';

const API_BASE = '/api';

export async function fetchHealth(): Promise<HealthStatus> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}

export async function fetchDocuments(): Promise<DocumentMetadata[]> {
  const res = await fetch(`${API_BASE}/documents`);
  if (!res.ok) throw new Error(`Failed to fetch documents: ${res.statusText}`);
  const data = await res.json();
  return data.documents;
}

export async function uploadDocument(file: File): Promise<DocumentMetadata> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorData.detail || 'Upload failed');
  }

  return res.json();
}

export async function deleteDocument(documentId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/documents/${documentId}`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Failed to delete document');
  }
}

export async function askQuestion(documentId: string, question: string): Promise<QAResponse> {
  const res = await fetch(`${API_BASE}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ document_id: documentId, question }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorData.detail || 'Failed to get answer');
  }

  return res.json();
}

export async function askByQuestionNumber(documentId: string, questionNumber: number): Promise<QAResponse> {
  const res = await fetch(`${API_BASE}/ask-by-number`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ document_id: documentId, question_number: questionNumber }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorData.detail || `Question number ${questionNumber} was not found.`);
  }

  return res.json();
}

export async function fetchHistory(documentId?: string): Promise<QAResponse[]> {
  const url = documentId ? `${API_BASE}/history?document_id=${encodeURIComponent(documentId)}` : `${API_BASE}/history`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch history');
  const data = await res.json();
  return data.history;
}

export async function clearHistory(documentId?: string): Promise<number> {
  const url = documentId ? `${API_BASE}/history?document_id=${encodeURIComponent(documentId)}` : `${API_BASE}/history`;
  const res = await fetch(url, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to clear history');
  const data = await res.json();
  return data.deleted_count;
}
