export interface DocumentMetadata {
  document_id: string;
  original_filename: string;
  file_size: number;
  upload_timestamp: string;
  processing_status: 'pending' | 'processing' | 'indexed' | 'failed';
  page_count: number;
  chunk_count: number;
  indexing_status: string;
  error?: string | null;
}

export interface SourceExcerpt {
  page: number;
  content: string;
}

export interface QAResponse {
  interaction_id: string;
  document_id: string;
  document_filename: string;
  question_mode: 'free_text' | 'by_number';
  requested_question_number?: number | null;
  detected_question_text?: string | null;
  question: string;
  answer: string;
  sources: SourceExcerpt[];
  timestamp: string;
}

export interface HealthStatus {
  status: string;
  app_name: string;
  version: string;
  nvidia_configured: boolean;
  mongodb_connected: boolean;
  mongodb_error?: string | null;
  active_documents_count: number;
}
