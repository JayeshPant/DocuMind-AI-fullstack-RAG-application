import logging
from typing import List, Tuple, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.app.config import settings

logger = logging.getLogger("documind.rag")


class RAGService:
    def __init__(self):
        logger.info("Initializing FastEmbed embeddings and in-memory Qdrant client...")
        # 1. Embeddings (identical to main.py)
        self.embeddings = FastEmbedEmbeddings()

        # 2. Qdrant In-Memory Client
        self.client = QdrantClient(location=":memory:")

        # Track active vectorstores per document ID for clean multi-document isolation
        self.vectorstores: Dict[str, QdrantVectorStore] = {}

        # 3. LLM Configuration (preserving nemotron configuration)
        self.llm: Optional[ChatNVIDIA] = None
        self._init_llm()

        # 4. Prompt Template
        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are an expert document-grounded academic tutor. "
                "Answer the user's question accurately using ONLY the provided document context. "
                "For numbered-question requests, answer the exact question identified from the document. "
                "Provide a clear, accurate, well-structured explanation with mathematical or conceptual rigor where applicable. "
                "Do not invent document facts, formulas, quotations, page numbers, or source references. "
                "If the supplied context does not contain sufficient information to answer the question reliably, "
                "explicitly state: 'The provided document context does not contain sufficient information to answer this question.'\n\n"
                "Context:\n{context}"
            ),
            ("human", "{question}"),
        ])

    def _init_llm(self):
        if settings.NVIDIA_API_KEY:
            try:
                self.llm = ChatNVIDIA(
                    model=settings.NVIDIA_MODEL,
                    nvidia_api_key=settings.NVIDIA_API_KEY,
                    temperature=settings.TEMPERATURE,
                    max_completion_tokens=settings.MAX_COMPLETION_TOKENS,
                )
                logger.info(f"Initialized ChatNVIDIA with model: {settings.NVIDIA_MODEL}")
            except Exception as e:
                logger.error(f"Failed to initialize ChatNVIDIA: {e}")
                self.llm = None
        else:
            logger.warning("NVIDIA_API_KEY is not configured. LLM invocation will raise an error until configured.")
            self.llm = None

    def refresh_key(self, key: str):
        settings.NVIDIA_API_KEY = key
        self._init_llm()

    def get_collection_name(self, document_id: str) -> str:
        clean_id = document_id.replace("-", "_")
        return f"col_{clean_id}"

    def index_document(self, document_id: str, chunks: List[Document]) -> QdrantVectorStore:
        col_name = self.get_collection_name(document_id)
        
        # Recreate collection if it already exists
        try:
            self.client.delete_collection(collection_name=col_name)
        except Exception:
            pass

        self.client.create_collection(
            collection_name=col_name,
            vectors_config=VectorParams(size=settings.VECTOR_SIZE, distance=Distance.COSINE),
        )

        vectorstore = QdrantVectorStore(
            client=self.client,
            collection_name=col_name,
            embedding=self.embeddings,
        )
        
        if chunks:
            vectorstore.add_documents(chunks)
        
        self.vectorstores[document_id] = vectorstore
        logger.info(f"Indexed {len(chunks)} chunks into Qdrant collection '{col_name}'.")
        return vectorstore

    def delete_document_vectors(self, document_id: str) -> bool:
        col_name = self.get_collection_name(document_id)
        if document_id in self.vectorstores:
            del self.vectorstores[document_id]
        try:
            self.client.delete_collection(collection_name=col_name)
            return True
        except Exception as e:
            logger.warning(f"Failed or already deleted collection {col_name}: {e}")
            return False

    def get_vectorstore(self, document_id: str) -> Optional[QdrantVectorStore]:
        if document_id in self.vectorstores:
            return self.vectorstores[document_id]
        
        col_name = self.get_collection_name(document_id)
        try:
            collections = [c.name for c in self.client.get_collections().collections]
            if col_name in collections:
                vs = QdrantVectorStore(
                    client=self.client,
                    collection_name=col_name,
                    embedding=self.embeddings,
                )
                self.vectorstores[document_id] = vs
                return vs
        except Exception as e:
            logger.error(f"Error checking Qdrant collection {col_name}: {e}")
        return None

    def query(self, document_id: str, question: str, k: int = 3) -> Tuple[str, List[Document]]:
        """
        Executes the RAG pipeline:
        1. Retrieves top-k chunks from document's Qdrant collection.
        2. Constructs context.
        3. Invokes NVIDIA ChatNVIDIA LLM.
        4. Returns (answer, retrieved_docs).
        """
        vectorstore = self.get_vectorstore(document_id)
        if not vectorstore:
            raise ValueError(f"Document ID '{document_id}' has not been indexed in the vector database.")

        # Re-check LLM if it wasn't initialized earlier
        if self.llm is None and settings.NVIDIA_API_KEY:
            self._init_llm()

        if self.llm is None:
            raise ValueError("NVIDIA_API_KEY is not configured in backend/.env. Please provide a valid NVIDIA API key.")

        # Retrieve relevant chunks
        retriever = vectorstore.as_retriever(search_kwargs={"k": k})
        retrieved_docs = retriever.invoke(question)

        # Build context
        context = "\n\n".join([doc.page_content for doc in retrieved_docs]) if retrieved_docs else "No context found."

        # RAG Chain invocation
        rag_chain = self.prompt | self.llm | StrOutputParser()
        answer = rag_chain.invoke({"context": context, "question": question})

        return answer, retrieved_docs


rag_service = RAGService()
