import os

EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
CHROMA_PATH = "db"

CHUNK_SIZE = 900
CHUNK_OVERLAP = 200

TOP_K = 5

# Lê a URL do Ollama da variável de ambiente (definida no docker-compose)
# Se não existir, usa o valor padrão para execução local
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL_NAME = "llama3"
