# 🇵🇹 Burocracia GPT

Assistente de IA para responder a dúvidas sobre burocracia portuguesa com base em documentos reais (IRS, IRC, Segurança Social, etc.).

Usa RAG (Retrieval-Augmented Generation) com ChromaDB, embeddings HuggingFace e um modelo local via Ollama (Llama3). Suporta upload de PDFs e imagens com OCR automático.

---

## Instalação

### 1. Pré-requisitos

- Python 3.10+
- [Ollama](https://ollama.com) instalado e a correr localmente com o modelo Llama3:

```bash
ollama pull llama3
ollama serve
```

### 2. Instalar dependências Python

```bash
pip install -r requirements.txt
```

#### (Opcional) Acelerar com GPU (CUDA)

Por defeito, o `pip install -r requirements.txt` instala a versão **CPU-only** do PyTorch, o que torna o `ingest.py` (embeddings + OCR) mais lento. Se tiveres uma GPU NVIDIA, instala o PyTorch com suporte CUDA **antes** do resto das dependências:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
pip install -r requirements.txt
```

Confirma que ficou tudo bem com:

```bash
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

Se `torch.cuda.is_available()` devolver `True`, o `ingest.py` e o OCR (`ocr.py`) vão usar automaticamente a GPU.

### 3. Descarregar o modelo de embeddings

```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')"
```

---

## Execução

### 1. Indexar os documentos (só é necessário fazer uma vez)

Coloca os PDFs na pasta `docs/` e executa:

```bash
python ingest.py
```

### 2. Lançar a aplicação web

```bash
streamlit run webapp.py
```

A aplicação abre automaticamente no browser em `http://localhost:8501`.

---

## O que faz

- Responde a perguntas sobre burocracia portuguesa (IRS, IRC, IVA, Segurança Social, etc.) com base numa base de conhecimento de documentos PDF oficiais.
- Permite fazer upload de um PDF ou imagem (carta, documento recebido) para análise — o sistema extrai o texto via OCR e usa-o como contexto adicional.
- Apresenta o nível de confiança de cada resposta e permite ver os chunks de contexto utilizados.
