# Statistical Techniques RAG Application

A Retrieval-Augmented Generation (RAG) system built with LangChain, FastEmbed, Qdrant in-memory vector store, and NVIDIA's Nemotron language model.

## Overview

This project implements an end-to-end question-answering pipeline grounded on statistical reference documents:
1. **Document Loading**: Loads course literature and reference materials from PDF files using `PyPDFLoader`.
2. **Text Chunking**: Splits documents into overlapping text chunks using `RecursiveCharacterTextSplitter`.
3. **Embeddings & Vector Store**: Computes dense vector embeddings locally using `FastEmbedEmbeddings` (`BAAI/bge-small-en-v1.5-onnx-Q`) and indexes them into an in-memory `Qdrant` vector store.
4. **Context Retrieval**: Queries the vector store for the top-$k$ most relevant context chunks.
5. **Generation**: Synthesizes accurate, grounded answers using NVIDIA NIM (`nvidia/nemotron-3.5-lightning-30b-a3b`).

---

## Project Structure

```text
.
├── document_loader/
│   └── STATS.pdf             # Reference PDF documents
├── .env.example              # Template for environment variables
├── .gitignore                # Excludes secrets, venv, and cache files
├── main.py                   # Main RAG execution script
├── README.md                 # Project documentation
└── requirements.txt          # Python dependencies
```

---

## Prerequisites

* Python 3.10+
* NVIDIA NIM API Key (obtain from [NVIDIA Build](https://build.nvidia.com/))

---

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd "RAG application"
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Copy `.env.example` to `.env` and fill in your NVIDIA API key:
   ```bash
   # Windows (PowerShell)
   Copy-Item .env.example .env

   # Linux / macOS
   cp .env.example .env
   ```
   Open `.env` and insert your key:
   ```env
   NVIDIA_API_KEY=nvapi-...
   ```

---

## Running the Application

Ensure your reference PDF is placed at `document_loader/STATS.pdf`, then run:

```bash
python main.py
```

The application will load and index the document, perform semantic similarity search against the sample question, and generate a tutor response grounded strictly in the provided context.
