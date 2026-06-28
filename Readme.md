# 🇵🇹 Burocracia GPT

Assistente de IA para responder a dúvidas sobre burocracia portuguesa com base em documentos reais (IRS, IRC, Segurança Social, etc.).

Usa RAG (Retrieval-Augmented Generation) com ChromaDB, embeddings HuggingFace e um modelo local via Ollama (Llama3). Suporta upload de PDFs e imagens com OCR automático.

> **Este projeto corre inteiramente em Docker** — não é necessário instalar Python, Ollama, nem qualquer dependência no computador.

---

## Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e em execução

---

## Instalação e execução

### 1. Adicionar os documentos (opcional)

Colocar mais PDFs de legislação portuguesa na pasta `docs/` se pretender, antes de arrancar o projeto.

### 2. Arrancar no Docker Desktop

Abre um terminal na pasta do projeto e corre:

```bash
docker compose up --build
```

O Docker trata automaticamente de tudo:

| Passo | O que acontece |
|---|---|
| Build da imagem | Instala todas as dependências do `requirements.txt` |
| Embeddings | Descarrega o modelo HuggingFace multilingue |
| Ollama | Arranca o servidor do modelo de linguagem |
| Llama 3 | Descarrega o modelo (~4 GB, só na primeira vez) |
| Ingest | Lê os PDFs da pasta `docs/`, cria chunks e popula o ChromaDB |
| App | Lança a aplicação Streamlit na porta 8501 |

### 3. Abrir a aplicação

No Docker Desktop, quando os três containers estiverem a **verde (running)**:

- Clica no link **`8501:8501`** no container `app`
- Ou acede diretamente a: **http://localhost:8501**

---

## Estrutura dos containers

| Container | Imagem | Função |
|---|---|---|
| `app` | Build local | Aplicação Streamlit + ChromaDB |
| `ollama` | `ollama/ollama` | Servidor do modelo Llama 3 |
| `ollama-setup` | `ollama/ollama` | Descarrega o Llama 3 (corre uma vez) |

---

## Estrutura do projeto

```
├── Dockerfile             # Imagem da aplicação Streamlit
├── docker-compose.yml     # Orquestra os 3 serviços
├── webapp.py              # Interface Streamlit (chat, upload, arquitetura)
├── ingest.py              # Lê PDFs, cria embeddings e popula o ChromaDB
├── rag.py                 # Pesquisa semântica na base vetorial
├── llm.py                 # Chama o Ollama (Llama 3) com prompt e contexto
├── ocr.py                 # Extrai texto de imagens com EasyOCR
├── memory.py              # Gestão do histórico de conversação
├── config.py              # Configurações gerais
├── docs/                  # PDFs de legislação portuguesa (adicionares tu)
└── db/                    # Base ChromaDB (gerada automaticamente)
```

---

## O que faz

- Responde a perguntas sobre burocracia portuguesa (IRS, IRC, IVA, Segurança Social, etc.) com base numa base de conhecimento de documentos PDF oficiais.
- Permite fazer upload de um PDF ou imagem (carta, documento recebido) para análise — o sistema extrai o texto via OCR e usa-o como contexto adicional.
- Apresenta o nível de confiança de cada resposta e permite ver os chunks de contexto utilizados.

---

## Parar e reiniciar

```bash
# Parar
docker compose down

# Reiniciar (sem rebuild — muito mais rápido)
docker compose up
```

> Na segunda execução, o modelo Llama 3 e os dados do ChromaDB já estão guardados em volumes Docker, por isso o arranque é quase imediato.